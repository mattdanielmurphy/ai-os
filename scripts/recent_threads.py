#!/usr/bin/env python3
"""
recent_threads.py — Unified Recent Conversation Threads Inspector

Aggregates recent conversation threads across:
  1. Gemini Web / Perplexity chat archives (~/Documents/gemini-archive/threads)
  2. Antigravity coding brain workspaces (~/.gemini/antigravity/brain)
  3. Hermes Agent sessions (~/.hermes/state.db)

Usage:
  recent-threads [--limit 10] [--source all|gemini|antigravity|hermes] [--search QUERY] [--json]
"""

import os
import sys
import json
import re
import sqlite3
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

ARCHIVE_DIR = Path.home() / "Documents/gemini-archive/threads"
BRAIN_DIRS = [
    Path.home() / ".gemini/antigravity/brain",
    Path.home() / ".gemini/antigravity-cli/brain",
]
PB_PATH = Path.home() / ".gemini/antigravity/agyhub_summaries_proto.pb"
HERMES_DB_PATH = Path.home() / ".hermes/state.db"
CODEX_DIR = Path.home() / ".codex"
CODEX_SESSIONS_PATH = CODEX_DIR / "session_index.jsonl"
CODEX_DB_PATH = CODEX_DIR / "thread_history_1.sqlite"


def load_pb_titles() -> Dict[str, str]:
    """Parse Antigravity protobuf conversation summaries."""
    titles = {}
    if not PB_PATH.exists():
        return titles
    try:
        data = PB_PATH.read_bytes()
        i = 0
        while i < len(data):
            tag = data[i]
            if tag != 0x0A:
                break
            i += 1
            l = 0
            s = 0
            while True:
                b = data[i]
                i += 1
                l |= (b & 0x7F) << s
                if not (b & 0x80):
                    break
                s += 7
            chunk = data[i : i + l]
            i += l

            try:
                idx = 0
                if chunk[idx] == 0x0A:
                    idx += 1
                    l1, s1 = 0, 0
                    while True:
                        b = chunk[idx]
                        idx += 1
                        l1 |= (b & 0x7F) << s1
                        if not (b & 0x80):
                            break
                        s1 += 7
                    cid = chunk[idx : idx + l1].decode("utf-8")
                    idx += l1
                    if idx < len(chunk) and chunk[idx] == 0x12:
                        idx += 1
                        l2, s2 = 0, 0
                        while True:
                            b = chunk[idx]
                            idx += 1
                            l2 |= (b & 0x7F) << s2
                            if not (b & 0x80):
                                break
                            s2 += 7
                        sub_bytes = chunk[idx : idx + l2]
                        if sub_bytes and sub_bytes[0] == 0x0A:
                            s_idx = 1
                            lt, ss = 0, 0
                            while True:
                                b = sub_bytes[s_idx]
                                s_idx += 1
                                lt |= (b & 0x7F) << ss
                                if not (b & 0x80):
                                    break
                                ss += 7
                            title = sub_bytes[s_idx : s_idx + lt].decode("utf-8")
                            titles[cid] = title.strip()
            except Exception:
                pass
    except Exception:
        pass
    return titles


def load_json_summaries() -> Dict[str, str]:
    """Load json-based thread summaries from brain dirs."""
    summaries = {}
    for brain_dir in BRAIN_DIRS:
        p = brain_dir / "thread_summaries.json"
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        v_clean = re.sub(r"^\[Gemini\]\s*", "", str(v)).strip()
                        summaries[k] = v_clean
            except Exception:
                pass
    return summaries


def get_gemini_archive_threads(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent web chat archives."""
    threads = []
    if not ARCHIVE_DIR.exists():
        return threads

    files = sorted(ARCHIVE_DIR.rglob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]
    for f in files:
        mtime = f.stat().st_mtime
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        meta = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip(" \"'")

        title = meta.get("title", f.stem)
        source_url = meta.get("source_url", "")
        archived_at = meta.get("archived_at", "")
        msg_count = meta.get("message_count", None)

        # Clean title quotes
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]

        # Extract first user query snippet
        prompt_snippet = ""
        user_match = re.search(r"## User [^\n]*\n\n(.*?)(?=\n<!-- |\n## |\Z)", text, re.DOTALL)
        if user_match:
            raw = user_match.group(1)
            # Remove <context> blocks
            clean = re.sub(r"<context>.*?</context>", "", raw, flags=re.DOTALL)
            clean = re.sub(r"\[Attached Context:[^\]]*\]", "", clean)
            clean = re.sub(r"<[^>]+>", " ", clean)
            if "…\n\n" in clean:
                clean = clean.split("…\n\n", 1)[1]
            prompt_snippet = " ".join(clean.split())[:140]

        # Determine source platform
        src_tag = "gemini-web"
        if "perplexity.ai" in source_url:
            src_tag = "perplexity"

        threads.append({
            "source": src_tag,
            "id": meta.get("conversation_id", f.stem),
            "title": title,
            "timestamp": mtime,
            "archived_at": archived_at,
            "url": source_url,
            "file_path": str(f),
            "snippet": prompt_snippet,
            "message_count": int(msg_count) if msg_count and msg_count.isdigit() else None,
        })

    return threads


def get_antigravity_brain_threads(pb_titles: Dict[str, str], json_summaries: Dict[str, str], limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent Antigravity brain sessions."""
    threads = []
    candidates = []
    for brain_dir in BRAIN_DIRS:
        if brain_dir.exists():
            for d in brain_dir.iterdir():
                if d.is_dir() and not d.name.startswith("."):
                    candidates.append(d)

    candidates.sort(key=lambda d: d.stat().st_mtime, reverse=True)

    for d in candidates[:limit]:
        cid = d.name
        mtime = d.stat().st_mtime
        title = pb_titles.get(cid) or json_summaries.get(cid)

        # Fallback to thread.md or task.md
        prompt_snippet = ""
        thread_md = d / "thread.md"
        if thread_md.exists():
            try:
                raw_text = thread_md.read_text(encoding="utf-8", errors="ignore")
                clean = re.sub(r"<[^>]+>", " ", raw_text)
                # Remove header boilerplate
                clean = re.sub(r"Thread Started — [^\n]+", "", clean)
                prompt_snippet = " ".join(clean.split())[:140]
            except Exception:
                pass

        if not title:
            task_md = d / "task.md"
            if task_md.exists():
                try:
                    title = task_md.read_text(encoding="utf-8", errors="ignore").splitlines()[0][:80]
                except Exception:
                    pass

        if not title:
            title = prompt_snippet[:60] if prompt_snippet else f"Antigravity Session {cid[:8]}"

        threads.append({
            "source": "antigravity",
            "id": cid,
            "title": title,
            "timestamp": mtime,
            "archived_at": None,
            "url": None,
            "file_path": str(thread_md if thread_md.exists() else d),
            "snippet": prompt_snippet,
            "message_count": None,
        })

    return threads


def get_hermes_sessions(limit: int = 30) -> List[Dict[str, Any]]:
    """Fetch recent Hermes CLI / ACP / WebUI sessions from state.db."""
    threads = []
    if not HERMES_DB_PATH.exists():
        return threads

    try:
        conn = sqlite3.connect(f"file:{HERMES_DB_PATH}?mode=ro", uri=True)
        c = conn.cursor()
        query = """
            SELECT id, source, title, started_at, message_count
            FROM sessions
            WHERE source NOT IN ('gemini-archive') AND message_count > 0
            ORDER BY started_at DESC
            LIMIT ?
        """
        for row in c.execute(query, (limit,)):
            sid, src, title, started_at, msg_count = row
            threads.append({
                "source": f"hermes-{src}",
                "id": sid,
                "title": title or f"Hermes Session ({sid[:8]})",
                "timestamp": started_at or 0.0,
                "archived_at": None,
                "url": None,
                "file_path": None,
                "snippet": None,
                "message_count": msg_count,
            })
        conn.close()
    except Exception:
        pass

    return threads


def get_codex_threads(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent ChatGPT / Codex CLI sessions."""
    threads = []
    if not CODEX_SESSIONS_PATH.exists():
        return threads

    raw_sessions = []
    try:
        with open(CODEX_SESSIONS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    raw_sessions.append(json.loads(line))
    except Exception:
        return threads

    def parse_ts(iso_str):
        if not iso_str:
            return 0.0
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            return 0.0

    raw_sessions.sort(key=lambda s: parse_ts(s.get("updated_at")), reverse=True)

    db_conn = None
    if CODEX_DB_PATH.exists():
        try:
            db_conn = sqlite3.connect(f"file:{CODEX_DB_PATH}?mode=ro", uri=True)
        except Exception:
            db_conn = None

    for s in raw_sessions[:limit]:
        sid = s.get("id")
        title = s.get("thread_name") or f"Codex Session {sid[:8]}"
        ts = parse_ts(s.get("updated_at"))

        snippet = ""
        msg_count = 0
        if db_conn and sid:
            try:
                cur = db_conn.cursor()
                cur.execute(
                    "SELECT item_type, item_json FROM thread_items WHERE thread_id = ? ORDER BY rollout_ordinal ASC",
                    (sid,),
                )
                items = cur.fetchall()
                msg_count = len(items)
                for item_type, item_json in items:
                    if item_type == "userMessage":
                        data = json.loads(item_json)
                        content = data.get("content", [])
                        if isinstance(content, list):
                            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                            clean = " ".join(texts).strip()
                        elif isinstance(content, str):
                            clean = content.strip()
                        else:
                            clean = ""
                        snippet = " ".join(clean.split())[:140]
                        break
            except Exception:
                pass

        threads.append({
            "source": "chatgpt",
            "id": sid,
            "title": title,
            "timestamp": ts,
            "archived_at": s.get("updated_at"),
            "url": None,
            "file_path": None,
            "snippet": snippet,
            "message_count": msg_count,
        })

    if db_conn:
        db_conn.close()

    return threads


def format_relative_time(ts: float) -> str:
    """Format timestamp into human-readable relative time."""
    if not ts:
        return "Unknown"
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - dt
    secs = int(diff.total_seconds())

    if secs < 60:
        return "just now"
    if secs < 3600:
        mins = secs // 60
        return f"{mins}m ago"
    if secs < 86400:
        hours = secs // 3600
        return f"{hours}h ago"
    days = secs // 86400
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days}d ago"
    return dt.strftime("%Y-%m-%d")


def generate_handoff_card(thread: Dict[str, Any]) -> str:
    """Generate a clean, compact semantic handoff card for a thread."""
    sid = thread.get("id", "")
    src = thread.get("source", "").lower()
    title = thread.get("title", "Untitled")
    rel_time = format_relative_time(thread.get("timestamp", 0.0))

    first_user = thread.get("snippet", "")
    last_resolution = ""
    resume_hint = ""

    if src in ("gemini-web", "perplexity"):
        fpath = thread.get("file_path")
        if fpath and os.path.exists(fpath):
            try:
                text = Path(fpath).read_text(encoding="utf-8", errors="ignore")
                user_match = re.search(r"## User [^\n]*\n\n(.*?)(?=\n<!-- |\n## |\Z)", text, re.DOTALL)
                if user_match:
                    clean_u = re.sub(r"<context>.*?</context>", "", user_match.group(1), flags=re.DOTALL)
                    clean_u = re.sub(r"\[Attached Context:[^\]]*\]", "", clean_u)
                    clean_u = re.sub(r"<[^>]+>", " ", clean_u)
                    first_user = " ".join(clean_u.split())[:350]
                model_matches = re.findall(r"## (?:Gemini|Assistant) [^\n]*\n\n(.*?)(?=\n<!-- |\n## |\Z)", text, re.DOTALL)
                if model_matches:
                    clean_m = re.sub(r"<[^>]+>", " ", model_matches[-1])
                    last_resolution = " ".join(clean_m.split())[:350]
            except Exception:
                pass
        resume_hint = f"**Native URL:** {thread.get('url') or 'N/A'}"

    elif src == "chatgpt":
        if CODEX_DB_PATH.exists() and sid:
            try:
                conn = sqlite3.connect(f"file:{CODEX_DB_PATH}?mode=ro", uri=True)
                cur = conn.cursor()
                cur.execute(
                    "SELECT item_type, item_json FROM thread_items WHERE thread_id = ? ORDER BY rollout_ordinal ASC",
                    (sid,),
                )
                items = cur.fetchall()
                for item_type, item_json in items:
                    data = json.loads(item_json)
                    if item_type == "userMessage" and not first_user:
                        c = data.get("content", [])
                        if isinstance(c, list):
                            texts = [x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"]
                            first_user = " ".join(" ".join(texts).split())[:350]
                        elif isinstance(c, str):
                            first_user = " ".join(c.split())[:350]
                    elif item_type == "agentMessage":
                        t = data.get("text", "")
                        if t:
                            last_resolution = " ".join(t.split())[:350]
                conn.close()
            except Exception:
                pass
        resume_hint = f"**Resume Command:** `codex resume {sid}`"

    elif src == "antigravity":
        fpath = thread.get("file_path")
        transcript_path = None
        if fpath:
            p = Path(fpath)
            if p.is_file() and p.name == "thread.md":
                transcript_path = p.parent / ".system_generated" / "logs" / "transcript.jsonl"
            elif p.is_dir():
                transcript_path = p / ".system_generated" / "logs" / "transcript.jsonl"

        if transcript_path and transcript_path.exists():
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        obj = json.loads(line)
                        typ = obj.get("type")
                        content = obj.get("content", "")
                        if typ == "USER_INPUT" and not first_user:
                            clean = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "")
                            first_user = " ".join(clean.split())[:350]
                        elif typ in ("PLANNER_RESPONSE", "ASSISTANT_RESPONSE") and content:
                            clean = re.sub(r"<[^>]+>", " ", content)
                            last_resolution = " ".join(clean.split())[:350]
            except Exception:
                pass
        resume_hint = f"**Workspace Brain Path:** `file://{fpath}`"

    elif "hermes" in src:
        resume_hint = f"**Session ID:** `{sid}`"

    card = f"""<prior_thread_context source="{src.upper()}" id="{sid}" title="{title}" updated="{rel_time}">
**Original Thread:** [{src.upper()}] {title} ({rel_time})
**Initial Objective:**
"{first_user or 'No user query recorded.'}"

**Latest Resolution / Context:**
"{last_resolution or 'Session in progress / context concluded.'}"

{resume_hint}
**Handoff Directive:** Seamlessly resume context and tasks from this prior conversation.
</prior_thread_context>"""
    return card


def open_thread_native(thread: Dict[str, Any]) -> bool:
    """Launch or resume the thread in its native application."""
    import subprocess
    src = thread.get("source", "").lower()
    sid = thread.get("id", "")

    if src in ("gemini-web", "perplexity") and thread.get("url"):
        subprocess.run(["open", thread["url"]])
        return True
    elif src == "chatgpt" and sid:
        applescript = f'''tell application "Terminal"
            activate
            do script "codex resume {sid}"
        end tell'''
        subprocess.run(["osascript", "-e", applescript])
        return True
    elif src == "antigravity":
        fpath = thread.get("file_path")
        if fpath:
            subprocess.run(["open", fpath])
            return True
    return False


def copy_to_clipboard(text: str):
    """Copy text to macOS pasteboard."""
    import subprocess
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(input=text.encode("utf-8"))
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Unified recent conversation threads viewer.")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Number of threads to return (default: 10)")
    parser.add_argument("-s", "--source", choices=["all", "gemini", "antigravity", "hermes", "chatgpt"], default="all", help="Filter by source")
    parser.add_argument("-q", "--search", type=str, default="", help="Search query filter")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of formatted text")
    parser.add_argument("--handoff", type=str, default="", help="Thread ID or search query to generate a handoff card for")
    parser.add_argument("--open", type=str, default="", help="Thread ID or search query to open/resume natively")
    parser.add_argument("--copy", action="store_true", help="When using --handoff, also copy the card to the clipboard")

    args = parser.parse_args()

    all_threads: List[Dict[str, Any]] = []

    # Gather requested sources
    if args.source in ("all", "gemini"):
        all_threads.extend(get_gemini_archive_threads(limit=max(args.limit * 2, 50)))

    if args.source in ("all", "antigravity"):
        pb_titles = load_pb_titles()
        json_summaries = load_json_summaries()
        all_threads.extend(get_antigravity_brain_threads(pb_titles, json_summaries, limit=max(args.limit * 2, 50)))

    if args.source in ("all", "chatgpt"):
        all_threads.extend(get_codex_threads(limit=max(args.limit * 2, 50)))

    if args.source in ("all", "hermes"):
        all_threads.extend(get_hermes_sessions(limit=max(args.limit * 2, 50)))

    # Handle --handoff mode
    if args.handoff:
        target_q = args.handoff.lower()
        matched = [
            t for t in all_threads
            if target_q == t.get("id", "").lower()
            or target_q in t.get("id", "").lower()
            or target_q in t.get("title", "").lower()
        ]
        if not matched:
            print(f"Error: No thread matching '{args.handoff}' found.", file=sys.stderr)
            sys.exit(1)
        card = generate_handoff_card(matched[0])
        print(card)
        if args.copy:
            copy_to_clipboard(card)
            print("[Copied handoff card to clipboard]", file=sys.stderr)
        return

    # Handle --open mode
    if args.open:
        target_q = args.open.lower()
        matched = [
            t for t in all_threads
            if target_q == t.get("id", "").lower()
            or target_q in t.get("id", "").lower()
            or target_q in t.get("title", "").lower()
        ]
        if not matched:
            print(f"Error: No thread matching '{args.open}' found.", file=sys.stderr)
            sys.exit(1)
        ok = open_thread_native(matched[0])
        if ok:
            print(f"Opened thread '{matched[0]['title']}' ({matched[0]['source']})")
        else:
            print(f"Could not open thread '{matched[0]['title']}' natively.", file=sys.stderr)
        return

    # Filter by search term if provided
    if args.search:
        term = args.search.lower()
        all_threads = [
            t for t in all_threads
            if term in t.get("title", "").lower()
            or term in (t.get("snippet") or "").lower()
            or term in (t.get("id") or "").lower()
        ]

    # Sort descending by timestamp
    all_threads.sort(key=lambda t: t.get("timestamp") or 0.0, reverse=True)
    all_threads = all_threads[:args.limit]

    if args.json:
        print(json.dumps({"count": len(all_threads), "threads": all_threads}, indent=2))
        return

    # Formatted output
    print(f"=== RECENT THREADS ({len(all_threads)} results) ===")
    for i, t in enumerate(all_threads, 1):
        rel = format_relative_time(t["timestamp"])
        src = t["source"].upper()
        title = t["title"]
        msg_str = f" • {t['message_count']} msgs" if t.get("message_count") else ""
        print(f"{i}. [{src}] {title} ({rel}{msg_str})")

        if t.get("snippet"):
            print(f"   💬 \"{t['snippet']}\"")
        if t.get("url"):
            print(f"   🔗 {t['url']}")
        if t.get("file_path"):
            print(f"   📁 file://{t['file_path']}")
        print()


if __name__ == "__main__":
    main()

