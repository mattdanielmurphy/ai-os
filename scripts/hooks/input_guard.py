#!/usr/bin/env python3
"""PreToolUse guard: Bash commands that grab Matt's screen need a take-control ticket.

Opening/revealing files, launching or activating apps, focusing windows, synthetic
keys/clicks and media play/pause or volume changes all count as input on Matt's
Mac (rule: "Mac Automation: Take-Control Queue"). If a command looks like one of
those and this session doesn't hold a granted `claude-control` ticket, deny it
with instructions. A command that asks for clearance itself (contains
`claude-control`) passes. Fails open if Hammerspoon can't be reached.
"""
import json
import os
import re
import subprocess
import sys

CC = os.path.expanduser("~/.hammerspoon/bin/claude-control")

# Start of a command: line start, or after ; & | ( `$(` `xargs`, optional sudo/command.
START = r"(?:^|[;&|(`]|\$\(|\bxargs\s+(?:-\S+\s+)*)\s*(?:command\s+|sudo\s+)?"
PATTERNS = [
    (START + r"open\s", "`open` (opens/reveals a file or brings an app forward)"),
    (r"\bosascript\b[\s\S]*\b(activate|reveal|keystroke|key code|click|play|pause|playpause|set volume)\b",
     "osascript that activates an app, reveals a file, sends keys/clicks or changes playback/volume"),
    (r"\bhs\b[\s\S]*(eventtap|launchOrFocus|:activate|:focus\(|hs\.application\.open|:becomeMain|setVolume|setMuted)",
     "Hammerspoon call that posts input, focuses an app/window or changes volume"),
    (START + r"(cliclick|nowplaying-cli\s+(play|pause|togglePlayPause|next|previous))\b",
     "synthetic click or media control"),
    (r"\byoutube\.sh\s+(play|pause|toggle)", "YouTube play/pause"),
]


def matches(cmd):
    for pat, why in PATTERNS:
        if re.search(pat, cmd, re.IGNORECASE | re.MULTILINE):
            return why
    return None


def held(session):
    try:
        out = subprocess.run([CC, "held", session], capture_output=True, text=True, timeout=6)
        lines = out.stdout.strip().splitlines()
        return lines[-1].strip() if lines else ""
    except Exception:
        return ""


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    why = matches(cmd)
    if not why or "claude-control" in cmd:
        return 0
    session = re.sub(r"[^A-Za-z0-9_-]", "", data.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
    state = held(session) if session else ""
    if state in ("granted", "pending"):
        return 0
    if state != "none":  # Hammerspoon unreachable or odd answer: warn, don't block work.
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
              "additionalContext": f"Input guard couldn't reach Hammerspoon. This command looks like input on Matt's Mac ({why}); it still needs a claude-control ticket."}}))
        return 0
    reason = (f"Blocked by the take-control guard: this looks like input on Matt's Mac ({why}). "
              "Get clearance first: ~/.hammerspoon/bin/claude-control ask \"<what and why>\" 3 "
              "(exit 1 = not now: don't re-ask, tell Matt; exit 3 = stopped: end the task), "
              "run it, then claude-control done <ticket>. If this command truly doesn't touch the "
              "screen, say so to Matt instead of working around the guard.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
