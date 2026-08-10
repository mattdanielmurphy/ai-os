#!/usr/bin/env python3
"""
Extract and refine Antigravity session titles in Hermes Agent's state.db.

Sources:
  1. ~/.gemini/antigravity-cli/conversation_summaries.db (title / preview)
  2. ~/.gemini/antigravity/agyhub_summaries_proto.pb (Protobuf summary store)
  3. Smart title cleaning from transcript content / first user message

Ensures all session titles in Hermes Desktop are readable, clean, and unique.
"""

import json
import re
import sqlite3
from pathlib import Path

STATE_DB = Path.home() / ".hermes" / "state.db"
SUMMARIES_DB = Path.home() / ".gemini" / "antigravity-cli" / "conversation_summaries.db"
PROTO_PB = Path.home() / ".gemini" / "antigravity" / "agyhub_summaries_proto.pb"

APP_BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
CLI_BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"


def get_titles_from_summaries_db() -> dict[str, str]:
    titles = {}
    if not SUMMARIES_DB.exists():
        return titles

    conn = sqlite3.connect(SUMMARIES_DB)
    c = conn.cursor()
    c.execute("SELECT conversation_id, title, preview FROM conversation_summaries;")
    for cid, title, preview in c.fetchall():
        t = (title or preview or "").strip()
        if t:
            titles[cid] = t
    conn.close()
    return titles


def get_titles_from_proto_pb() -> dict[str, str]:
    titles = {}
    if not PROTO_PB.exists():
        return titles

    data = PROTO_PB.read_bytes()
    pattern = re.compile(
        rb'\n\$([0-9a-f\-]{36}).{1,150}?\n"([A-Za-z0-9 _\-\:\.\,/\(\)\'\?\!\+\=\@\#\$\%\^\&\*\[\]\{\}\<\>]{3,120})'
    )
    for m in pattern.finditer(data):
        cid = m.group(1).decode("ascii")
        title = m.group(2).decode("utf-8", errors="ignore").strip()
        if title and len(title) > 2 and cid not in titles:
            titles[cid] = title

    return titles


def clean_title(title_text: str, sid: str = "") -> str:
    text = (title_text or "").strip()
    if not text:
        return "Antigravity Session"

    # Remove trailing ID tags e.g. [047b7e]
    text = re.sub(r"\s*\[[0-9a-f]{6,10}\]$", "", text, flags=re.IGNORECASE)

    # 1. Handle Subagent boilerplate
    if "file editor subagent" in text.lower() or "leaf agent" in text.lower() or text.startswith("You are a"):
        m_file = re.search(
            r"(/Users/[^\s'\"`]+|/Volumes/[^\s'\"`]+|\b[\w\-\./]+\.(?:ts|js|py|lua|rs|json|sh|md))\b",
            text,
        )
        if m_file:
            fname = Path(m_file.group(1)).name
            return f"Subagent Edit: {fname}"
        m_proj = re.search(r"projects/([\w\-]+)", text)
        if m_proj:
            return f"Subagent Task ({m_proj.group(1)})"
        return "Subagent Task"

    # 2. Extract project + file path if present
    m_path = re.search(
        r"(?:projects/|CloudStorage/[^/]+/projects/)([\w\-]+)/?([\w\-\./]*\.(?:ts|js|py|lua|rs|json|sh|md))?",
        text,
    )
    if m_path:
        proj = m_path.group(1)
        filepath = m_path.group(2)
        if filepath:
            fname = Path(filepath).name
            return f"{proj}: {fname}"
        else:
            return f"Project: {proj}"

    # 3. Strip leading command prefixes
    text = re.sub(
        r"^(Please|In|Update|Modify|Fix|Create|Add|Refactor)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^<USER_REQUEST>\s*", "", text, flags=re.IGNORECASE)

    # 4. Clean formatting
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if text:
        text = text[0].upper() + text[1:]

    if len(text) > 65:
        text = text[:65].rstrip() + "..."

    return text or "Antigravity Session"


def make_unique_title(
    raw_title: str | None, session_id: str, used_titles: set
) -> str | None:
    if not raw_title or not raw_title.strip():
        return None
    title = raw_title.strip()
    if title not in used_titles:
        used_titles.add(title)
        return title

    candidate = f"{title} [{session_id[:6]}]"
    if candidate not in used_titles:
        used_titles.add(candidate)
        return candidate

    candidate = f"{title} [{session_id[:10]}]"
    used_titles.add(candidate)
    return candidate


def main():
    db_titles = get_titles_from_summaries_db()
    pb_titles = get_titles_from_proto_pb()

    merged_titles = {}
    merged_titles.update(pb_titles)
    merged_titles.update(db_titles)

    print(f"Loaded {len(db_titles)} titles from conversation_summaries.db")
    print(f"Loaded {len(pb_titles)} titles from agyhub_summaries_proto.pb")
    print(f"Merged explicit generated titles count: {len(merged_titles)}")

    if not STATE_DB.exists():
        print(f"Error: {STATE_DB} does not exist.")
        return

    conn = sqlite3.connect(STATE_DB)
    c = conn.cursor()

    c.execute(
        'SELECT id, title, source FROM sessions WHERE source IN ("antigravity-app", "antigravity-cli");'
    )
    ag_sessions = c.fetchall()

    # Load used titles
    c.execute("SELECT title FROM sessions WHERE title IS NOT NULL;")
    used_titles = set(r[0] for r in c.fetchall())

    updated_count = 0
    for sid, old_title, source in ag_sessions:
        if old_title and old_title in used_titles:
            used_titles.remove(old_title)

        if sid in merged_titles:
            raw_t = merged_titles[sid]
        else:
            raw_t = clean_title(old_title or "", sid)

        unique_t = make_unique_title(raw_t, sid, used_titles)
        if unique_t and unique_t != old_title:
            c.execute(
                "UPDATE sessions SET title = ? WHERE id = ?;", (unique_t, sid)
            )
            updated_count += 1

    conn.commit()
    conn.close()

    print(f"Successfully refined and updated {updated_count} Antigravity session titles in state.db!")


if __name__ == "__main__":
    main()
