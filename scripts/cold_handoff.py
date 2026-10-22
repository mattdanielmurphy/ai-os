#!/usr/bin/env python3
"""Hand off a thread whose prompt cache has gone cold, without reloading it.

Resuming a long thread after its cache expires re-sends the whole conversation at full
price. This reads the thread straight from its transcript file instead, has Haiku write a
/_handoff-style brief in a throwaway session, and gives back a one-line paste prompt for a
new thread. The old thread is never sent to its own model again.

  python3 scripts/cold_handoff.py status <session_id>          # JSON: lastAt, ttlSec, tokens, project
  python3 scripts/cold_handoff.py write <session_id> [--open]  # JSON: path, prompt

`write --open` also copies the paste prompt to the clipboard and opens a new Code thread
in the desktop app. Used by the context-alert mod (mods/context-alert).
"""
import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_claude_threads import export, slug  # noqa: E402

MAX_CHARS = 400_000  # newest part of the conversation Haiku reads (~100k tokens)
DEFAULT_TTL = 3600   # every request on this Mac so far used the 1-hour cache

BRIEF = """You are writing a handoff brief so a fresh Claude Code thread can continue the work in
the conversation below. The old thread will not be reloaded; this brief is all the next
thread gets, plus any files it names. Write markdown, 60-150 lines, concrete over complete
(file paths, commands, numbers, exact errors). Refer to people as they are named; the
user is Matt. Use exactly these sections:

# Handoff: <what we're working on> ({date}, cold)

## Chain
- Old thread: {sid} ({title}). Reopen with `claude --resume {sid}` (expensive: cold cache).
- Earlier handoff files the conversation mentions under docs/handoffs/, if any.

## Chain summary
3-8 bullets: what has been built or decided so far.

## This thread
- What got done (files, commits, results).
- What was tried that didn't work, and why.

## Working on now
The current task in 2-4 sentences, and where exactly it stopped.

## Keep in mind
- Matt's corrections and preferences, in his words where possible.
- Gotchas, decisions, rejected options (with the reason); uncommitted or untested work.

## Next steps
1. The single next action, concrete enough to start without asking.

## Read first
- 2-5 key files, with why.

Output only the brief. The conversation{cut}:

"""


def find_transcript(sid):
    hits = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl"))
    if not hits:
        sys.exit(f"No transcript found for session {sid}")
    return Path(max(hits, key=os.path.getmtime))


def status(path):
    """Time of the last model response, its cache lifetime and the context it carried."""
    last_at, ttl, tokens, project = None, None, 0, False
    for line in path.open(encoding="utf-8", errors="replace"):
        # A Claude project thread: its messages arrive wrapped in <wake> envelopes.
        if not project and '"type":"user"' in line.replace(" ", "") and "<wake " in line:
            project = True
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        u = (d.get("message") or {}).get("usage") or {}
        if not u:
            continue
        last_at = d.get("timestamp") or last_at
        tokens = sum(u.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens",
                                             "cache_creation_input_tokens", "output_tokens"))
        cc = u.get("cache_creation") or {}
        if cc.get("ephemeral_1h_input_tokens"):
            ttl = 3600
        elif cc.get("ephemeral_5m_input_tokens"):
            ttl = 300
    ms = None
    if last_at:
        ms = int(datetime.datetime.fromisoformat(last_at.replace("Z", "+00:00")).timestamp() * 1000)
    return {"lastAt": ms, "ttlSec": ttl or DEFAULT_TTL, "tokens": tokens, "project": project}


def project_root(cwd):
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.home() / "projects" / "ai-os"


def write(path, sid, open_app, then=""):
    result = export(path)
    if not result:
        sys.exit("Transcript has no conversation to hand off")
    md = result[1]
    meta = dict(re.findall(r'^(\w+): "?(.*?)"?$', md.split("\n---\n", 1)[0], re.M))
    title, cwd = meta.get("title", "untitled"), meta.get("cwd") or os.getcwd()
    convo = md.split("\n---\n", 1)[-1]
    cut = ""
    if len(convo) > MAX_CHARS:
        convo, cut = convo[-MAX_CHARS:], " (oldest part cut; newest kept)"
    today = datetime.date.today().isoformat()
    prompt = BRIEF.format(date=today, sid=sid, title=title, cut=cut) + convo

    run = subprocess.run(
        ["claude", "-p", "--model", "haiku", "--no-session-persistence", "--tools", ""],
        input=prompt, capture_output=True, text=True, timeout=600)
    brief = run.stdout.strip()
    if run.returncode != 0 or not brief.startswith("#"):
        sys.exit(f"Haiku did not write a brief: {(run.stderr or run.stdout).strip()[:300]}")

    out_dir = project_root(cwd) / "docs" / "handoffs"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"{today}_{slug(title, 30)}-cold"
    dest, n = out_dir / f"{name}.md", 2
    while dest.exists():
        dest, n = out_dir / f"{name}_{n}.md", n + 1
    paste = f"Read {dest} and continue."
    if then:
        paste += f" Then: {then}"
    dest.write_text(f"{brief}\n\nPaste into a new thread: \"{paste}\"\n", encoding="utf-8")

    # The desktop app's new-thread link fills the prompt box (it never sends on its own).
    link = "claude://code/new?" + urllib.parse.urlencode({"q": paste}, quote_via=urllib.parse.quote)
    if open_app:
        subprocess.run(["pbcopy"], input=paste, text=True)  # fallback if the box comes up empty
        subprocess.run(["open", link])
    return {"path": str(dest), "prompt": paste, "link": link}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["status", "write"])
    ap.add_argument("session_id")
    ap.add_argument("--open", action="store_true", help="copy the paste prompt, open a new thread")
    ap.add_argument("--then", default="", help="the message to send after the handoff is read")
    a = ap.parse_args()
    path = find_transcript(a.session_id)
    out = status(path) if a.action == "status" else write(path, a.session_id, a.open, a.then.strip())
    print(json.dumps(out))


if __name__ == "__main__":
    main()
