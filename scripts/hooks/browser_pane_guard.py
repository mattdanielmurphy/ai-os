#!/usr/bin/env python3
"""PreToolUse guard for the built-in browser pane (mcp__Claude_Browser__*).

Opening a heavy page (reels, video, audio) in the pane hung a thread for 20+ min,
and a hook can't time-limit an MCP call. So navigate/preview_start to local, reel
or media URLs are denied unless the URL carries ?mute (the user wants to watch it);
automated checks should run headless from Bash with an `alarm` cap instead.
"""
import json
import re
import sys

try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input") or {}
    url = ti.get("url", "") or ""
except Exception:
    sys.exit(0)
heavy = re.search(r"reel|\.(mp4|mov|webm|mp3|wav)\b|localhost|127\.0\.0\.1|\.test\b", url, re.I)
if heavy and not re.search(r"[?&]mute", url):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
          "permissionDecisionReason": "Blocked: local/reel/media pages in the browser pane have hung threads for 20+ min "
          "and MCP calls have no timeout. Check pages headless from Bash (playwright/chromium, "
          "`perl -e 'alarm 60; exec @ARGV' --`, log to tmp/). If Matt asked to see it in the pane, add ?mute to the URL."}}))
