#!/usr/bin/env python3
"""
sync_threads.py — Read Hermes SQLite sessions and sync them to the Gemini
antigravity-cli brain transcript format.

Usage:
    python3 scripts/sync_threads.py --oneshot
    python3 scripts/sync_threads.py --watch
    python3 scripts/sync_threads.py --oneshot --verbose
"""

import argparse
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
HERMES_DB = Path.home() / ".hermes" / "state.db"
BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"

# Message-type mapping
ROLE_TO_TYPE = {
    "user": "USER_INPUT",
    "assistant": "PLANNER_RESPONSE",
    "tool": "RUN_COMMAND",
}
ROLE_TO_SOURCE = {
    "user": "USER_EXPLICIT",
    "assistant": "MODEL",
    "tool": "MODEL",
}


def verbose(msg: str, flag: bool) -> None:
    if flag:
        print(f"[sync] {msg}")


def format_timestamp(ts: float) -> str:
    """Convert a unix-epoch float to RFC 3339 string."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_transcript_entry(
    step_index: int,
    role: str,
    content: str | None,
    timestamp: float,
    session_title: str | None,
    is_first_assistant: bool,
) -> dict:
    """Build a transcript JSONL entry for a single message."""
    entry_type = ROLE_TO_TYPE.get(role, "UNKNOWN")
    source = ROLE_TO_SOURCE.get(role, "SYSTEM")

    entry = {
        "step_index": step_index,
        "source": source,
        "type": entry_type,
        "status": "DONE",
        "created_at": format_timestamp(timestamp),
        "content": content or "",
    }

    # Wrap user message content in <USER_REQUEST> tags
    if role == "user":
        entry["content"] = f"<USER_REQUEST>\n{content or ''}\n</USER_REQUEST>"

    # Prepend <THREAD_NAME> to the first assistant message
    if role == "assistant" and is_first_assistant and session_title:
        entry["content"] = (
            f"<THREAD_NAME>{session_title}</THREAD_NAME>\n{content or ''}"
        )

    return entry


def sync_session(session_row: tuple, verbose_flag: bool) -> bool:
    """Sync one Hermes session to the Gemini brain transcript files.
    Returns True if any new content was written.
    """
    session_id, title, started_at, ended_at = session_row
    title = title or ""

    # ── fetch messages (active only, chronological) ────────────────────
    conn = sqlite3.connect(str(HERMES_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT role, content, timestamp FROM messages "
            "WHERE session_id = ? AND active = 1 "
            "ORDER BY timestamp ASC, id ASC",
            (session_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        verbose(f"Skipping {session_id}: no active messages", verbose_flag)
        return False

    # ── build transcript entries ───────────────────────────────────────
    entries = []
    step_index = 0
    first_assistant_seen = False

    for row in rows:
        role = row["role"]
        if role == "session_meta":
            continue  # skip internal metadata

        is_first = role == "assistant" and not first_assistant_seen
        if is_first:
            first_assistant_seen = True

        entry = build_transcript_entry(
            step_index=step_index,
            role=role,
            content=row["content"],
            timestamp=row["timestamp"],
            session_title=title,
            is_first_assistant=is_first,
        )
        entries.append(entry)
        step_index += 1

    # ── target directory ────────────────────────────────────────────────
    log_dir = BRAIN_DIR / session_id / ".system_generated" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = log_dir / "transcript.jsonl"
    transcript_full_path = log_dir / "transcript_full.jsonl"

    # ── read existing lines to detect changes ──────────────────────────
    existing_lines: list[str] = []
    if transcript_path.exists():
        existing_lines = transcript_path.read_text().splitlines(keepends=False)

    new_lines = [json.dumps(e, ensure_ascii=False) for e in entries]

    if new_lines == existing_lines:
        verbose(f"{session_id}: no changes", verbose_flag)
        return False

    # ── write both files ────────────────────────────────────────────────
    # transcript.jsonl — standard format (same as existing)
    transcript_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # transcript_full.jsonl — may include extra fields; for now identical
    transcript_full_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    verbose(
        f"Wrote {len(new_lines)} entries to {log_dir} (was {len(existing_lines)} lines)",
        verbose_flag,
    )
    return True


def get_db_mtime() -> float:
    """Return the modification time of the Hermes database."""
    return HERMES_DB.stat().st_mtime if HERMES_DB.exists() else 0.0


def run_oneshot(verbose_flag: bool) -> int:
    """Sync all sessions. Returns count of sessions updated."""
    verbose("Starting oneshot sync", verbose_flag)

    if not HERMES_DB.exists():
        print(f"Error: Hermes database not found at {HERMES_DB}")
        return 0

    conn = sqlite3.connect(str(HERMES_DB))
    try:
        rows = conn.execute(
            "SELECT id, title, started_at, ended_at FROM sessions "
            "ORDER BY started_at ASC"
        ).fetchall()
    finally:
        conn.close()

    updated = 0
    for row in rows:
        try:
            if sync_session(row, verbose_flag):
                updated += 1
        except Exception as e:
            print(f"Error syncing session {row[0]}: {e}")

    verbose(f"Done. {updated}/{len(rows)} sessions updated", verbose_flag)
    return updated


def run_watch(verbose_flag: bool) -> None:
    """Watch the Hermes database for changes and sync continuously."""
    verbose("Starting watch mode on Hermes DB", verbose_flag)
    last_mtime = get_db_mtime()

    # Initial sync
    run_oneshot(verbose_flag)

    while True:
        time.sleep(5)
        try:
            current_mtime = get_db_mtime()
            if current_mtime != last_mtime:
                verbose(
                    f"DB modified (mtime {last_mtime} → {current_mtime}), re-syncing",
                    verbose_flag,
                )
                run_oneshot(verbose_flag)
                last_mtime = current_mtime
        except KeyboardInterrupt:
            verbose("Interrupted, exiting", verbose_flag)
            break
        except Exception as e:
            print(f"Error in watch loop: {e}")
            # Continue watching despite transient errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Hermes sessions to Gemini brain transcript format."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--oneshot",
        action="store_true",
        help="Run once and exit",
    )
    group.add_argument(
        "--watch",
        action="store_true",
        help="Watch ~/.hermes/state.db for changes and sync continuously",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information",
    )
    args = parser.parse_args()

    if args.watch:
        run_watch(args.verbose)
    else:
        # Default to oneshot if no mode specified
        run_oneshot(args.verbose)


if __name__ == "__main__":
    main()