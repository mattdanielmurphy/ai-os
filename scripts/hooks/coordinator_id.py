#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook: remember the project coordinator's current session id.

Every coordinator relay that reaches a project thread on this Mac is tagged
`<relay from="coordinator" session="session_…">`. The coordinator gets recycled now and then,
so this keeps config/coordinator_session.txt pointing at the live one; scripts/voice_task_inbox.py
reads it to send voice tasks with `claude -p --cloud <id>` instead of pasting into the chat.
Assumes one project (Everything) sends relays here; after a project split this needs a per-project map.
Prints nothing and fails silently: a broken hook must never block a prompt.
"""
import json
import re
import sys
from pathlib import Path

FILE = Path.home() / "projects" / "ai-os" / "config" / "coordinator_session.txt"
RELAY = re.compile(r'<relay from="coordinator" session="session_([A-Za-z0-9]+)"')


def main():
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
        m = RELAY.search(prompt)
        if not m:
            return
        sid = "cse_" + m.group(1)
        if FILE.exists() and FILE.read_text().strip() == sid:
            return
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text(sid + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
