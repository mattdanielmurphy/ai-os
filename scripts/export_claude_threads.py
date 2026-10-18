#!/usr/bin/env python3
"""Export Claude Code transcripts (~/.claude/projects/*/*.jsonl) to markdown for QMD.

Keeps only the human-readable conversation: Matt's prompts and Claude's text replies.
Tool calls, tool output, system reminders and bookkeeping records are dropped.
Output goes to private/claude-threads/ (gitignored); only changed sessions are rewritten.

  python3 scripts/export_claude_threads.py [--force]
"""
import json
import os
import re
import sys
from pathlib import Path

SRC = Path.home() / ".claude" / "projects"
OUT = Path(__file__).resolve().parent.parent / "private" / "claude-threads"
SKIP_PREFIXES = ("<system-reminder>", "<task-notification>", "<command-", "<local-command", "[Request interrupted")


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def slug(s, n=40):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rstrip("-") or "untitled"


def export(path):
    title, cwd, date, turns = None, None, None, []
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = d.get("type")
        if t == "custom-title":
            title = d.get("customTitle") or title
        if t not in ("user", "assistant") or d.get("isSidechain"):
            continue
        cwd = cwd or d.get("cwd")
        date = date or (d.get("timestamp") or "")[:10]
        msg = d.get("message") or {}
        txt = text_of(msg.get("content")).strip()
        if not txt or txt.startswith(SKIP_PREFIXES):
            continue
        if t == "user" and d.get("origin", {}).get("kind") not in (None, "human"):
            continue
        turns.append(("Matt" if t == "user" else "Claude", txt))
    if not any(who == "Matt" for who, _ in turns):
        return None
    first = next(txt for who, txt in turns if who == "Matt")
    title = title or first.splitlines()[0][:80]
    sid = path.stem
    body = [
        "---",
        f"title: {json.dumps(title)}",
        f"date: \"{date}\"",
        f"cwd: {json.dumps(cwd or '')}",
        f"session_id: \"{sid}\"",
        "source: \"claude-code\"",
        "---",
        "",
        f"# {title}",
        "",
    ]
    for who, txt in turns:
        body += [f"## {who}", "", txt, ""]
    return f"{date}-{slug(title)}--[{sid[:8]}].md", "\n".join(body)


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    existing = {p.name.rsplit("--[", 1)[-1][:8]: p for p in OUT.glob("*.md")}
    written = 0
    for path in SRC.glob("*/*.jsonl"):
        old = existing.get(path.stem[:8])
        if old and not force and old.stat().st_mtime >= path.stat().st_mtime:
            continue
        result = export(path)
        if not result:
            continue
        name, md = result
        if old and old.name != name:
            os.replace(old, OUT / name)  # title changed; keep one file per session
        (OUT / name).write_text(md, encoding="utf-8")
        written += 1
    print(f"exported {written} session(s) to {OUT}")


if __name__ == "__main__":
    main()
