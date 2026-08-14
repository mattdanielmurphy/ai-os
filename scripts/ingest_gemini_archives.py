#!/usr/bin/env python3
"""
Ingest Gemini Chat Archives into Hermes Agent's FTS5 Search Database.

Scans ~/Documents/gemini-archive/threads for markdown files with YAML frontmatter
(structured by gemini-archive-browser) and inserts them into Hermes' state.db
so they become searchable via Hermes' session/history search.

Usage:
    python3 scripts/ingest_gemini_archives.py              # dry-run (no writes)
    python3 scripts/ingest_gemini_archives.py --write       # actually write

Undo:
    cp ~/.hermes/state.db.bak.gemini-ingest ~/.hermes/state.db
"""

import argparse
import copy
import hashlib
import json
import os
import re
import sqlite3
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
ARCHIVE_DIR = Path.home() / "Documents" / "gemini-archive" / "threads"
HERMES_DB = Path.home() / ".hermes" / "state.db"
BACKUP_PATH = HERMES_DB.with_suffix(".db.bak.gemini-ingest")

# For the constraint: UNIQUE INDEX idx_sessions_title_unique ON sessions(title) WHERE title IS NOT NULL
# So we set title to NULL for null-title to avoid collision with other null-title entries
# Actually looking at the schema: CREATE UNIQUE INDEX idx_sessions_title_unique ON sessions(title) WHERE title IS NOT NULL;
# So NULL titles are excluded from the unique constraint — safe to set NULL.

SOURCE_NAME = "gemini-archive"

# ── Parsing ────────────────────────────────────────────────────────────

# Regex for gemini-message HTML comments
MSG_START_RE = re.compile(
    r'<!--\s*gemini-message\s+index=(\d+)\s+role="?(user|assistant|model)"?\s+timestamp="([^"]*)"\s*-->'
)
MSG_END_RE = re.compile(r'<!--\s*/gemini-message\s*-->')

# YAML frontmatter
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_timestamp(ts_str: str) -> float:
    """Parse a timestamp string to Unix epoch float. Supports ISO and custom formats."""
    # Try ISO format
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.timestamp()
    except ValueError:
        pass
    # Try "YYYY-MM-DD HH:MM" format
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
        # If no timezone info, assume local
        dt = dt.replace(tzinfo=timezone.utc)  # avoid naive/local issues
        return dt.timestamp()
    except ValueError:
        pass
    # Try "YYYY-MM-DD HH:MM MDT-6" or similar
    m = re.match(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", ts_str)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    # Fallback: current timestamp
    print(f"  ⚠ Could not parse timestamp '{ts_str}', using current time")
    return time.time()


def parse_yaml_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter.  We keep it simple: YAML is close enough
    to JSON for our frontmatter format.  Use a lightweight line-based parser
    to avoid a dependency."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    raw = m.group(1)
    meta = {}
    for line in raw.strip().splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # Remove surrounding quotes
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        meta[key] = val
    return meta


def parse_messages(text: str):
    """
    Yield (index, role, timestamp_str, content) tuples from gemini-message blocks.
    Ignores the YAML frontmatter.
    """
    # Strip frontmatter for message parsing
    body = FRONTMATTER_RE.sub("", text, count=1)

    # Find all message blocks by scanning for start/end markers
    pos = 0
    while True:
        start_m = MSG_START_RE.search(body, pos)
        if not start_m:
            break
        index = int(start_m.group(1))
        role = start_m.group(2)
        ts_str = start_m.group(3)
        end_m = MSG_END_RE.search(body, start_m.end())
        if not end_m:
            # No closing tag — look for the next start tag, or end of file
            next_start = MSG_START_RE.search(body, start_m.end())
            if next_start:
                content = body[start_m.end() : next_start.start()].strip()
                pos = next_start.start()
            else:
                # Last message and no closing tag — read to end
                content = body[start_m.end() :].strip()
                pos = len(body)
        else:
            content = body[start_m.end() : end_m.start()].strip()
            pos = end_m.end()

        # Strip injected timestamp prefixes e.g. "[2026-07-11 16:17 MDT-6] "
        content = re.sub(r"^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?:\s+[A-Z]{3,4}[+-]?\d*)?\]\s*", "", content, flags=re.IGNORECASE)
        # Strip injected context tracker e.g. "[context to this point is 5300] "
        content = re.sub(r"^\[context to this point is \d+\]\s*", "", content, flags=re.IGNORECASE)

        # Strip markdown headers like "## User — 2026-07-08 19:43"
        content = re.sub(r"^##\s+(User|Gemini|Assistant|Model)\s+[—\-].*$", "", content, flags=re.MULTILINE)
        content = content.strip()
        yield index, role, ts_str, content


# ── Database operations ────────────────────────────────────────────────


def backup_db(conn: sqlite3.Connection) -> Path:
    """Create a backup of the Hermes database.  Returns the backup path."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.commit()
    shutil.copy2(str(HERMES_DB), str(BACKUP_PATH))
    print(f"  ✓ Backed up to {BACKUP_PATH}")
    return BACKUP_PATH


def session_exists(conn: sqlite3.Connection, session_id: str) -> bool:
    """Check if a session with this ID already exists."""
    cur = conn.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,))
    return cur.fetchone() is not None


def get_or_create_session(conn: sqlite3.Connection, meta: dict, messages: list) -> str:
    """
    Upsert a session row.  Returns the session_id.
    We use INSERT OR IGNORE for the primary key, then update metadata.
    """
    session_id = meta.get("conversation_id", "")
    if not session_id:
        # Fallback: hash the title
        title = meta.get("title", "untitled")
        session_id = hashlib.sha256(title.encode()).hexdigest()[:16]

    started_at = messages[0]["ts"] if messages else time.time()
    title = meta.get("title", None)  # use None so it's stored as NULL (avoids unique-constraint coll)
    if title:
        title = re.sub(r"^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?:\s+[A-Z]{3,4}[+-]?\d*)?\]\s*", "", title)

    conn.execute(
        """INSERT OR IGNORE INTO sessions
           (id, source, title, started_at, message_count, model)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session_id, SOURCE_NAME, title, started_at, len(messages), "gemini-2.0-flash"),
    )
    # Update fields that may have changed
    conn.execute(
        """UPDATE sessions
           SET title = COALESCE(NULLIF(?, ''), title),
               message_count = ?,
               started_at = COALESCE(?, started_at)
           WHERE id = ?""",
        (title, len(messages), started_at, session_id),
    )
    return session_id


def insert_messages(
    conn: sqlite3.Connection, session_id: str, messages: list
) -> int:
    """
    Insert message rows for a session.  Skips messages whose content hasn't
    changed (by comparing content hash of existing rows).
    Returns the count of inserted messages.
    """
    # Get existing messages for this session to avoid duplicates
    existing = set()
    for row in conn.execute(
        "SELECT content FROM messages WHERE session_id = ? AND active = 1",
        (session_id,),
    ):
        existing.add(row[0])

    inserted = 0
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        ts = msg["ts"]

        if content in existing:
            # Update the timestamp just in case it was wrong previously
            conn.execute(
                "UPDATE messages SET timestamp = ? WHERE session_id = ? AND content = ?",
                (ts, session_id, content)
            )
            continue

        conn.execute(
            """INSERT INTO messages (session_id, role, content, timestamp)
               VALUES (?, ?, ?, ?)""",
            (session_id, role, content, ts),
        )
        inserted += 1

    return inserted


def process_archive(dry_run: bool = True, verbose: bool = False):
    """
    Main processing loop: scan archive dir, parse files, insert into DB.

    Returns a summary dict.
    """
    stats = {
        "files_found": 0,
        "files_parsed": 0,
        "files_skipped_empty": 0,
        "files_skipped_exists": 0,
        "files_error": 0,
        "sessions_created": 0,
        "messages_inserted": 0,
        "errors": [],
    }

    if not ARCHIVE_DIR.is_dir():
        print(f"✗ Archive directory not found: {ARCHIVE_DIR}")
        sys.exit(1)

    # Gather all .md files recursively
    md_files = sorted(f for f in ARCHIVE_DIR.rglob("*.md") if f.is_file())

    if not md_files:
        print(f"⚠ No .md files found in {ARCHIVE_DIR}")
        return stats

    stats["files_found"] = len(md_files)

    # Connect to Hermes DB
    db_conn = None
    if not dry_run:
        db_conn = sqlite3.connect(str(HERMES_DB))
        db_conn.execute("PRAGMA journal_mode=WAL")
        db_conn.execute("PRAGMA synchronous=OFF")  # faster bulk insert

    try:
        for i, md_file in enumerate(md_files):
            if verbose:
                print(f"  [{i+1}/{len(md_files)}] {md_file.name}")

            try:
                text = md_file.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ✗ Error reading {md_file.name}: {e}")
                stats["files_error"] += 1
                stats["errors"].append(str(md_file.name))
                continue

            # Parse frontmatter
            meta = parse_yaml_frontmatter(text)
            if not meta or "conversation_id" not in meta:
                if verbose:
                    print(f"    ↪ No conversation_id in frontmatter, skipping")
                stats["files_skipped_empty"] += 1
                continue

            # Parse messages
            msg_list = list(parse_messages(text))
            if not msg_list:
                if verbose:
                    print(f"    ↪ No messages found, skipping")
                stats["files_skipped_empty"] += 1
                continue

            # Build message dicts
            messages = []
            for idx, role, ts_str, content in msg_list:
                messages.append(
                    {
                        "index": idx,
                        "role": role if role != "model" else "assistant",
                        "ts": parse_timestamp(ts_str),
                        "content": content,
                    }
                )

            # Sort by index to maintain order
            messages.sort(key=lambda m: m["index"])

            if dry_run:
                stats["files_parsed"] += 1
                stats["sessions_created"] += 1
                stats["messages_inserted"] += len(messages)
                if verbose:
                    title = meta.get("title", "untitled")
                    print(f"    ↪ Would create session '{title}' "
                          f"({len(messages)} messages)")
                continue

            # ── Write to DB ──
            if session_exists(db_conn, meta["conversation_id"]):
                if verbose:
                    print(f"    ↪ Session {meta['conversation_id']} already exists, skipping")
                stats["files_skipped_exists"] += 1
                continue

            session_id = get_or_create_session(db_conn, meta, messages)
            inserted = insert_messages(db_conn, session_id, messages)

            stats["files_parsed"] += 1
            stats["sessions_created"] += 1
            stats["messages_inserted"] += inserted

            if verbose:
                title = meta.get("title", "untitled")
                print(f"    ✓ '{title}' — {len(messages)} msgs, {inserted} new")

        if not dry_run and db_conn:
            db_conn.commit()

    finally:
        if db_conn:
            db_conn.close()

    return stats


def print_report(stats: dict, dry_run: bool):
    """Print a formatted summary report."""
    mode = "DRY RUN" if dry_run else "LIVE"
    sep = "─" * 50
    print(f"\n{sep}")
    print(f"  {mode} — Report")
    print(sep)
    print(f"  Files found:         {stats['files_found']}")
    print(f"  Files parsed:        {stats['files_parsed']}")
    print(f"  Files skipped (no msg): {stats['files_skipped_empty']}")
    print(f"  Files skipped (exists): {stats['files_skipped_exists']}")
    print(f"  Files error:         {stats['files_error']}")
    print(f"  Sessions created:    {stats['sessions_created']}")
    print(f"  Messages inserted:   {stats['messages_inserted']}")
    if stats["errors"]:
        print(f"  Errors ({len(stats['errors'])}):")
        for e in stats["errors"][:5]:
            print(f"    • {e}")
        if len(stats["errors"]) > 5:
            print(f"    … and {len(stats['errors']) - 5} more")
    print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Gemini chat archives into Hermes Agent's FTS5 search database."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write to the Hermes database (default: dry-run)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show per-file processing details",
    )
    args = parser.parse_args()

    # Sanity check
    if not HERMES_DB.is_file():
        print(f"✗ Hermes database not found at {HERMES_DB}")
        print("  Is Hermes Agent installed and configured?")
        sys.exit(1)

    print(f"📂 Archive: {ARCHIVE_DIR}")
    print(f"🕗 Hermes DB: {HERMES_DB}")
    print(f"{'🔴 DRY RUN — use --write to apply' if not args.write else '🟢 LIVE — will modify database'}")
    print()

    if args.write:
        # Backup
        print("→ Creating backup…")
        conn = sqlite3.connect(str(HERMES_DB))
        backup_db(conn)
        conn.close()
        print()

    stats = process_archive(dry_run=not args.write, verbose=args.verbose)
    print_report(stats, dry_run=not args.write)

    if not args.write:
        print(f"\n💡 To actually write:  python3 {__file__} --write")
    else:
        print(f"\n↩ To undo:  cp {BACKUP_PATH} {HERMES_DB}")

    return 0 if stats["files_error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
