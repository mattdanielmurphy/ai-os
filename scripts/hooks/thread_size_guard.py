#!/usr/bin/env python3
"""PreToolUse hook: block hand-offs into Code threads at/over 250k tokens.

Matches SendMessage and mcp__ccd_session_mgmt__send_message. For a local_ target it
runs scripts/thread_size.py (reads the transcript, works for idle threads). Over the
limit -> deny with a "start fresh" reason; under -> allow and show the target's title
so the sender can check the task still fits its scope. Any error -> fail open.
"""
import glob, json, os, subprocess, sys

LIMIT = 250
SIZE = os.path.expanduser("~/projects/ai-os/scripts/thread_size.py")

def title(sid):
    meta = glob.glob(os.path.expanduser(
        f"~/Library/Application Support/Claude/claude-code-sessions/*/*/{sid}.json"))
    return json.load(open(meta[0])).get("title") if meta else None

def out(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
        "permissionDecision": decision, "permissionDecisionReason": reason}}))

try:
    inp = json.load(sys.stdin).get("tool_input") or {}
    sid = inp.get("to") or inp.get("session_id") or inp.get("sessionId") or ""
    if not (isinstance(sid, str) and sid.startswith("local_")):
        sys.exit(0)
    r = subprocess.run(["python3", SIZE, sid, "--limit", str(LIMIT)],
                       capture_output=True, text=True, timeout=8)
    t = title(sid) or sid
    if r.returncode == 2:
        k = r.stdout.split("k", 1)[0].strip()
        out("deny", f"This thread ({t}) is {k}k tokens (limit {LIMIT}k): start a fresh "
                    "thread with a self-contained brief and a link to the old one.")
    elif r.returncode == 0:
        # context only, no permission decision: don't auto-approve sends
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "additionalContext": f"Thread size OK ({r.stdout.strip()}). Target: \"{t}\". "
                     "Check the task fits that scope; if not, start a fresh thread."}}))
except Exception:
    pass
sys.exit(0)
