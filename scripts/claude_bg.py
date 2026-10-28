#!/usr/bin/env python3
"""List the shell commands Claude Code sessions are running, by session title.

  claude_bg.py            list every running Claude shell command (oldest first)
  claude_bg.py --min 8    only ones running 8+ minutes
  claude_bg.py stop N     stop row N from the last list (or a pid)
  claude_bg.py --json     machine-readable (for the watchdog / HUDs)

The session is found by matching the command text against recent Claude
transcripts, then looking up that transcript's title in the desktop app's
session files. Unknown sessions show as "(unknown session)".
"""
import glob
import json
import os
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from tool_watchdog import etime_s  # noqa: E402

PROJECTS = os.path.expanduser("~/.claude/projects")
APP_SESSIONS = os.path.expanduser("~/Library/Application Support/Claude/claude-code-sessions")
LAST = os.path.expanduser("~/projects/ai-os/tmp/claude-bg-last.json")


def shells():
    out = subprocess.run(["ps", "-axo", "pid=,ppid=,etime=,command="], capture_output=True, text=True).stdout
    rows = []
    for l in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(.*)", l)
        if m:
            rows.append((int(m[1]), int(m[2]), etime_s(m[3]), m[4]))
    claude = {p for p, _, _, c in rows if re.search(r"claude-code/.*/claude\b.*--output-format", c)}
    res = []
    for p, pp, e, c in rows:
        if pp in claude and re.search(r"-c\b.*\beval\b", c):
            m = re.search(r"eval '(.*?)' && pwd -P", c, re.S)
            cmd = (m.group(1) if m else c).replace("'\"'\"'", "'").replace("\\012", "\n")
            res.append({"pid": p, "secs": e, "cmd": cmd})
    return sorted(res, key=lambda r: -r["secs"])


def titles():
    t = {}
    for f in glob.glob(os.path.join(APP_SESSIONS, "*", "*", "local_*.json")):
        try:
            d = json.load(open(f))
            t[d.get("cliSessionId")] = (d.get("title") or "untitled", d.get("sessionId"))
        except Exception:
            pass
    return t


def session_of(cmd, files):
    # The longest single line of the command is distinctive enough; JSON-escape it like the transcript does.
    probe = max(cmd.splitlines() or [cmd], key=len)[:80]
    needle = json.dumps(probe)[1:-1].encode()
    for f in files:
        try:
            if needle in open(f, "rb").read():
                return os.path.basename(f)[:-6]
        except OSError:
            pass
    return None


def listing(min_s=0):
    rows = [r for r in shells() if r["secs"] >= min_s]
    if rows:
        oldest = time.time() - max(r["secs"] for r in rows) - 600
        files = [f for f in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")) if os.path.getmtime(f) >= oldest]
        files.sort(key=os.path.getmtime, reverse=True)
        t = titles()
        for r in rows:
            sid = session_of(r["cmd"], files)
            r["title"], r["session"] = t.get(sid, ("(unknown session)", None))
    return rows


def stop(pid):
    subprocess.run(["pkill", "-TERM", "-P", str(pid)])
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


def main(argv):
    if argv[:1] == ["stop"] and len(argv) > 1:
        n = int(argv[1])
        try:
            last = json.load(open(LAST))
        except Exception:
            last = []
        pid = last[n - 1]["pid"] if 0 < n <= len(last) else n
        stop(pid)
        print(f"stopped {pid}")
        return 0
    min_s = float(argv[argv.index("--min") + 1]) * 60 if "--min" in argv else 0
    rows = listing(min_s)
    os.makedirs(os.path.dirname(LAST), exist_ok=True)
    json.dump(rows, open(LAST, "w"))
    if "--json" in argv:
        print(json.dumps(rows))
        return 0
    if not rows:
        print("No Claude shell commands running.")
    for i, r in enumerate(rows, 1):
        first = r["cmd"].strip().splitlines()[0][:70] if r["cmd"].strip() else ""
        print(f"{i}. {r['secs'] // 60} min · {r['title']} · {first}")
    if rows:
        print("\nStop one: claude-bg stop <number>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
