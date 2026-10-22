#!/usr/bin/env python3
"""Threads that are waiting on Matt and whose prompt cache is about to go cold.

Used by ~/.hammerspoon/modules/claude_warm.lua to nudge Matt before a big thread's
1-hour cache expires (re-reading a cold thread costs ~20x a warm reply).

  python3 scripts/warm_threads.py [--min-tokens 50000] [--all]

Prints a JSON list, soonest first:
  [{"session", "title", "lastAt", "expiresAt", "ttlSec", "tokens", "asked", "url"}]

"url" opens the thread when Matt clicks the toast: a claude:// project-thread link for
Claude project threads (same form as claude-control --thread), null otherwise.

"Waiting on Matt" = the last thing he was shown (a project-thread reply, a decision
card, a question menu, or a Code-tab answer) asks him something (a "?" or a 👍 offer
near the end), and nothing has come in since. --all also lists threads that didn't ask.
"""
import argparse
import html
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cold_handoff import status  # noqa: E402  (last reply time, TTL, context size)

LOOKBACK = 3700  # a transcript untouched for longer than the cache lifetime is already cold
DEFAULT_PROJECT = "chan_01CUPXyY9oUwKVDFREVDpYDr"  # Everything
THREAD_RE = re.compile(r'<thread (?:ts|id)=\\?"(cmsg_\w{20,})|\\?"thread_id\\?"\s*:\s*\\?"(cmsg_\w{20,})')
PROJECT_RE = re.compile(r'<project id=\\?"(chan_\w+)')


def thread_url(project, thread):
    # Path form: the desktop app keeps only the path of a claude://claude.ai/epitaxy link and
    # drops ?thread=, which landed on the project's thread list. (project is implied by the id.)
    return f"claude://claude.ai/epitaxy/project/thread/{thread}" if thread else None


def clean_title(text):
    """A readable title from a first prompt: drops attachment paths (@"/Users/…") and
    the <wake>/<relay> envelope, keeping the person's words (or the coordinator's note)."""
    text = re.sub(r'@"[^"]*"', " ", text or "")
    m = re.search(r"<message\b[^>]*>(.*?)</message>", text, re.S) or re.search(r"<note>(.*?)</note>", text, re.S)
    if m:
        text = m.group(1)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text[:60].rstrip() + ("…" if len(text) > 60 else "")


def asks(text):
    """True when the end of a message asks Matt something."""
    lines = [l.strip() for l in (text or "").strip().splitlines() if l.strip()]
    lines = [l for l in lines if not l.startswith("Details:")]  # every reply ends with its details link
    tail = " ".join(lines[-2:])
    return "?" in tail or "👍" in tail


def scan(path):
    """(title, asked, url) from a transcript; asked is None when Matt has answered since."""
    title, ai_title, first_prompt, label = None, None, None, None
    thread, project, reply_ids = None, None, set()
    shown, answered, hearth, status_title = None, False, False, None
    turn_text = None
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = d.get("type")
        if kind == "custom-title":
            title = d.get("customTitle") or title
        elif kind == "ai-title":
            ai_title = d.get("aiTitle") or d.get("title") or ai_title
        if kind not in ("user", "assistant") or d.get("isSidechain") or d.get("isMeta"):
            continue
        content = (d.get("message") or {}).get("content")
        if kind == "user":
            blocks = content if isinstance(content, list) else [{"type": "text", "text": content or ""}]
            results = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_result"]
            if results:
                for b in results:  # a reply's result names its thread: {"thread_id": "cmsg_…"}
                    if not thread and b.get("tool_use_id") in reply_ids:
                        m = THREAD_RE.search(json.dumps(b.get("content")))
                        thread = m and (m.group(1) or m.group(2))
                continue
            text = " ".join(b.get("text", "") for b in blocks if isinstance(b, dict))
            if first_prompt is None and text.strip():
                first_prompt = text.strip()
            if text.lstrip().startswith(("<wake", "@")) or "<wake " in text[:600]:
                m = THREAD_RE.search(text)  # the wake envelope: <thread ts="cmsg_…">
                thread = thread or (m and (m.group(1) or m.group(2)))
                m = PROJECT_RE.search(text)
                project = project or (m and m.group(1))
            answered = True  # Matt (or a wake carrying his message/reaction) came in
            turn_text = None
            continue
        for b in content if isinstance(content, list) else []:
            if b.get("type") == "text" and b.get("text", "").strip():
                turn_text = b["text"]
                if not hearth:
                    shown, answered = turn_text, False
            elif b.get("type") == "tool_use":
                name, inp = b.get("name", ""), b.get("input") or {}
                if name.startswith("mcp__hearthbot__"):
                    hearth = True
                if name == "mcp__hearthbot__reply":
                    reply_ids.add(b.get("id"))
                    shown, answered = inp.get("text", ""), False
                elif name.endswith("ask_decision") or name == "AskUserQuestion":
                    shown, answered = "?", False
                elif name == "mcp__hearthbot__set_thread_label":
                    label = (inp.get("label") or "").strip() or label
                elif name == "mcp__hearthbot__update_status":
                    first = (inp.get("text") or "").strip().splitlines()
                    status_title = first[0] if first else status_title
    name = title or label or ai_title or status_title or clean_title(first_prompt) or path.stem[:8]
    url = thread_url(project, thread) if hearth else None
    if shown is None or answered:
        return name, None, url
    return name, asks(shown), url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-tokens", type=int, default=50000)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    now = time.time()
    out = []
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        try:
            if now - os.path.getmtime(f) > LOOKBACK:
                continue
        except OSError:
            continue
        p = Path(f)
        s = status(p)
        if s["lastAt"] is None:
            continue
        expires = s["lastAt"] + s["ttlSec"] * 1000
        if expires <= now * 1000 or s["tokens"] < args.min_tokens:
            continue
        title, asked, url = scan(p)
        if not asked and not args.all:
            continue
        out.append({"session": p.stem, "title": title, "lastAt": s["lastAt"], "expiresAt": expires,
                    "ttlSec": s["ttlSec"], "tokens": s["tokens"], "asked": bool(asked), "url": url})
    out.sort(key=lambda t: t["expiresAt"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
