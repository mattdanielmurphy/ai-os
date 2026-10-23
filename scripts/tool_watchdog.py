#!/usr/bin/env python3
"""Toast Matt when a Claude tool command has been running too long.

Runs every minute from launchd (com.matt.agent.tool-watchdog). Finds the shell
commands the Claude Code CLI spawned for its Bash tool (children of a `claude`
process whose command is `... eval '<cmd>'`) that have run longer than WARN_MIN,
and drops a toast in the claude-notify inbox once per process, with the kill
command. It never kills anything itself: background commands look identical to
stuck ones. Usage: tool_watchdog.py [--warn-min N] [--dry-run]
"""
import argparse
import json
import os
import re
import subprocess
import sys

STATE = os.path.expanduser("~/projects/ai-os/tmp/tool-watchdog.json")
NOTIFY = os.path.expanduser("~/.hammerspoon/bin/claude-notify")


def etime_s(e):
    d, _, rest = e.partition("-") if "-" in e else ("0", "", e)
    p = [int(x) for x in rest.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return int(d) * 86400 + p[0] * 3600 + p[1] * 60 + p[2]


def stuck(warn_s):
    out = subprocess.run(["ps", "-axo", "pid=,ppid=,etime=,command="], capture_output=True, text=True).stdout
    rows = []
    for l in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(.*)", l)
        if m:
            rows.append((int(m[1]), int(m[2]), etime_s(m[3]), m[4]))
    claude = {p for p, _, _, c in rows if re.search(r"claude-code/.*/claude\b.*--output-format", c)}
    return [(p, e, c) for p, pp, e, c in rows
            if pp in claude and e >= warn_s and re.search(r"-c\b.*\beval\b", c)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn-min", type=float, default=8)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        seen = json.load(open(STATE))
    except Exception:
        seen = {}
    now = stuck(a.warn_min * 60)
    live = {str(p) for p, _, _ in now}
    seen = {k: v for k, v in seen.items() if k in live}
    for p, e, c in now:
        if str(p) in seen:
            continue
        m = re.search(r"eval\s+'?(.{0,90})", c)
        cmd = (m.group(1) if m else c)[:90]
        body = f"{e // 60} min: {cmd}\nStop it: pkill -TERM -P {p}; kill {p}"
        print(f"pid {p}: {body}")
        if not a.dry_run:
            subprocess.run([NOTIFY, "A Claude command may be stuck", body, "--kind", "needs"], timeout=10)
            seen[str(p)] = e
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(seen, open(STATE, "w"))


if __name__ == "__main__":
    sys.exit(main())
