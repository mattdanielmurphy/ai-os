#!/usr/bin/env python3
"""
Ingest Antigravity.app and Antigravity CLI sessions into Hermes Agent's state.db.

Scans:
  1. ~/.gemini/antigravity/brain/ (Antigravity.app -> source="antigravity-app")
  2. ~/.gemini/antigravity-cli/brain/ (Antigravity CLI -> source="antigravity-cli")

Parses transcript.jsonl / transcript_full.jsonl / history / thread.md and inserts
sessions and messages into ~/.hermes/state.db. Trigger-based FTS5 auto-indexes
all inserted content.

Usage:
    python3 scripts/ingest_antigravity_sessions.py              # dry-run
    python3 scripts/ingest_antigravity_sessions.py --write       # execute write
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

HERMES_DB = Path.home() / ".hermes" / "state.db"
BACKUP_PATH = HERMES_DB.with_suffix(".db.bak.antigravity-import")

APP_BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
CLI_BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"


def parse_iso(ts_str: str | None) -> float | None:
    if not ts_str:
        return None
    try:
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str).timestamp()
    except Exception:
        return None


def parse_brain_dir(d: Path) -> dict:
    session_id = d.name
    messages = []
    title = None
    started_at = None

    t_file = d / ".system_generated" / "logs" / "transcript.jsonl"
    if not t_file.exists():
        t_file = d / ".system_generated" / "logs" / "transcript_full.jsonl"

    if t_file.exists():
        try:
            with open(t_file, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue

                    ts = parse_iso(data.get("created_at"))
                    if not started_at and ts:
                        started_at = ts

                    stype = data.get("type")
                    source = data.get("source")

                    if stype == "USER_INPUT":
                        raw_content = data.get("content") or ""
                        clean_content = re.sub(
                            r"^<USER_REQUEST>\s*", "", raw_content
                        )
                        clean_content = re.sub(
                            r"\s*</USER_REQUEST>$", "", clean_content
                        ).strip()
                        if clean_content:
                            messages.append(
                                {"role": "user", "content": clean_content, "ts": ts}
                            )
                            if not title:
                                first_line = clean_content.split("\n")[0][:80].strip()
                                title = first_line
                    elif stype in ("PLANNER_RESPONSE", "ASSISTANT_RESPONSE") or source == "MODEL":
                        content = data.get("content") or data.get("response") or ""
                        if isinstance(content, str) and content.strip():
                            clean_resp = re.sub(
                                r"^<THREAD_NAME>.*?</THREAD_NAME>\s*",
                                "",
                                content,
                                flags=re.DOTALL,
                            ).strip()
                            if clean_resp:
                                messages.append(
                                    {"role": "assistant", "content": clean_resp, "ts": ts}
                                )
        except Exception:
            pass

    # Fallback 1: history/turn_*.md
    if not messages:
        turn_dir = d / "history"
        if turn_dir.exists():
            def get_turn_num(p):
                m = re.search(r"\d+", p.name)
                return int(m.group()) if m else 0
            turns = sorted(list(turn_dir.glob("turn_*.md")), key=get_turn_num)
            for tf in turns:
                try:
                    txt = tf.read_text(encoding="utf-8", errors="replace").strip()
                    if txt:
                        messages.append(
                            {"role": "user", "content": txt, "ts": tf.stat().st_mtime}
                        )
                        if not title:
                            title = txt.split("\n")[0][:80].strip()
                except Exception:
                    pass

    # Fallback 2: thread.md
    if not messages:
        tm_file = d / "thread.md"
        if tm_file.exists():
            try:
                txt = tm_file.read_text(encoding="utf-8", errors="replace").strip()
                if txt:
                    messages.append(
                        {"role": "user", "content": txt, "ts": tm_file.stat().st_mtime}
                    )
                    if not title:
                        title = txt.split("\n")[0][:80].strip()
            except Exception:
                pass

    if not started_at:
        try:
            started_at = d.stat().st_mtime
        except Exception:
            started_at = time.time()

    if title:
        title = re.sub(r"[\r\n]+", " ", title).strip()
        if len(title) > 120:
            title = title[:120] + "..."

    return {
        "id": session_id,
        "title": title or None,
        "started_at": started_at,
        "messages": messages,
    }


def make_unique_title(raw_title: str | None, session_id: str, used_titles: set) -> str | None:
    if not raw_title or not raw_title.strip():
        return None
    title = raw_title.strip()
    if title not in used_titles:
        used_titles.add(title)
        return title
    
    # Title collision: append suffix
    candidate = f"{title} [{session_id[:6]}]"
    if candidate not in used_titles:
        used_titles.add(candidate)
        return candidate
        
    candidate = f"{title} [{session_id[:10]}]"
    used_titles.add(candidate)
    return candidate


def main():
    parser = argparse.ArgumentParser(description="Ingest Antigravity sessions into Hermes state.db")
    parser.add_argument("--write", action="store_true", help="Perform database writes")
    args = parser.parse_args()

    if not HERMES_DB.exists():
        print(f"Error: Database not found at {HERMES_DB}")
        sys.exit(1)

    print(f"Connecting to {HERMES_DB}...")
    conn = sqlite3.connect(str(HERMES_DB))
    
    # Load existing sessions and used titles
    cur = conn.cursor()
    cur.execute("SELECT id FROM sessions;")
    existing_ids = set(r[0] for r in cur.fetchall())
    
    cur.execute("SELECT title FROM sessions WHERE title IS NOT NULL;")
    used_titles = set(r[0] for r in cur.fetchall())
    
    print(f"Existing sessions in state.db: {len(existing_ids)}")
    print(f"Existing unique titles in state.db: {len(used_titles)}")

    # Scan Antigravity.app dirs
    app_dirs = [p for p in APP_BRAIN_DIR.glob("*") if p.is_dir()] if APP_BRAIN_DIR.exists() else []
    missing_app_dirs = [p for p in app_dirs if p.name not in existing_ids]

    # Scan Antigravity CLI dirs
    cli_dirs = [p for p in CLI_BRAIN_DIR.glob("*") if p.is_dir()] if CLI_BRAIN_DIR.exists() else []
    missing_cli_dirs = [p for p in cli_dirs if p.name not in existing_ids]

    print(f"\nAntigravity.app brain dirs total: {len(app_dirs)}, to ingest: {len(missing_app_dirs)}")
    print(f"Antigravity CLI brain dirs total: {len(cli_dirs)}, to ingest: {len(missing_cli_dirs)}")

    app_sessions = [parse_brain_dir(d) for d in missing_app_dirs]
    cli_sessions = [parse_brain_dir(d) for d in missing_cli_dirs]

    valid_app = [s for s in app_sessions if len(s["messages"]) > 0]
    valid_cli = [s for s in cli_sessions if len(s["messages"]) > 0]

    total_app_msgs = sum(len(s["messages"]) for s in valid_app)
    total_cli_msgs = sum(len(s["messages"]) for s in valid_cli)

    print(f"\nParsed Antigravity.app sessions: {len(valid_app)} valid ({total_app_msgs} msgs)")
    print(f"Parsed Antigravity CLI sessions: {len(valid_cli)} valid ({total_cli_msgs} msgs)")

    if not args.write:
        print("\n--- DRY RUN COMPLETE ---")
        print("Run with `--write` to perform the ingestion.")
        conn.close()
        return

    # Perform writes
    print("\n--- EXECUTING INGESTION ---")
    # 1. Backup DB
    print(f"Creating DB backup at {BACKUP_PATH}...")
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    shutil.copy2(str(HERMES_DB), str(BACKUP_PATH))
    print("Backup created.")

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    inserted_sessions = 0
    inserted_messages = 0

    items_to_ingest = [(s, "antigravity-app") for s in valid_app] + [(s, "antigravity-cli") for s in valid_cli]

    for session_data, source_tag in items_to_ingest:
        s_id = session_data["id"]
        title = make_unique_title(session_data["title"], s_id, used_titles)
        started_at = session_data["started_at"]
        msgs = session_data["messages"]

        cur.execute(
            """INSERT OR IGNORE INTO sessions 
               (id, source, title, started_at, message_count, model)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (s_id, source_tag, title, started_at, len(msgs), "gemini-2.5-pro"),
        )
        inserted_sessions += 1

        for idx, m in enumerate(msgs):
            m_ts = m.get("ts") or (started_at + idx * 0.1)
            m_role = m["role"]
            m_content = m["content"]

            cur.execute(
                """INSERT INTO messages 
                   (session_id, role, content, timestamp, active)
                   VALUES (?, ?, ?, ?, 1)""",
                (s_id, m_role, m_content, m_ts),
            )
            inserted_messages += 1

    conn.commit()
    conn.close()

    print(f"\nIngestion successful!")
    print(f"Sessions inserted: {inserted_sessions}")
    print(f"Messages inserted: {inserted_messages}")


if __name__ == "__main__":
    main()
