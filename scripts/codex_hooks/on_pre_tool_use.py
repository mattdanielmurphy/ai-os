#!/usr/bin/env python3
"""
on_pre_tool_use.py - Codex Hook CLI Entry Point for PreToolUse.

Reads PreToolUseCommandInputWire JSON from stdin, invokes tool_guard.py,
and outputs PreToolUseCommandOutputWire JSON to stdout.
"""

import sys
import json
import traceback
from pathlib import Path

# Add parent directory to path so codex_hooks package can be resolved
CURRENT_DIR = Path(__file__).resolve().parent
AI_OS_SCRIPTS = CURRENT_DIR.parent
if str(AI_OS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(AI_OS_SCRIPTS))

from codex_hooks.tool_guard import evaluate_tool_call

ERROR_LOG = Path.home() / ".codex" / "hooks_error.log"


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            payload = {}
        else:
            payload = json.loads(raw_input)

        output = evaluate_tool_call(payload)
        json.dump(output, sys.stdout)
        sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception as e:
        # Graceful fallback: never crash Codex
        try:
            ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(f"--- [PreToolUse Hook Error] ---\n{traceback.format_exc()}\n")
        except Exception:
            pass

        safe_output = {
            "continue": True,
            "decision": "approve",
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow"
            }
        }
        json.dump(safe_output, sys.stdout)
        sys.stdout.write("\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
