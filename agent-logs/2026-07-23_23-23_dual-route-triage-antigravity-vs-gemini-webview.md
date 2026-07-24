## Goal
Refine `triage_router.py` to intelligently dual-route prompts based on intent:
1. Coding / file / codebase tasks -> Launch a new interactive conversation in Antigravity in Terminal.
2. Non-coding general questions -> Open a new Gemini Webview thread in `ai-os`.

## User Feedback & Decisions
- Triage should not always go to Gemini Webview.
- Prompts asking for files, codebase search, code writing, or refactoring should open a new conversation in Antigravity.
- Antigravity sessions are spawned in a new Terminal window via AppleScript (`osascript`).

## Changes Made
- Added `launch_antigravity_terminal(query, model)` in `scripts/triage_router.py`:
  - Constructs `agy --model "<model>" -p "<query>"` command.
  - Runs AppleScript (`tell application "Terminal" to do script ... activate`) to spawn a new Terminal window running `agy` interactively and focusing the Terminal.
- Refined routing logic in `triage_router.py`:
  - `is_coding_intent` detects `coding_standard`, `coding_complex`, or keywords (`file`, `find`, `search`, `code`, `repo`, `script`, `fix`, `debug`, `refactor`, `build`, `run`, `git`).
  - If `is_coding_intent` is True -> Calls `launch_antigravity_terminal(query, selected_model)`.
  - If general non-coding query -> Calls `open_gemini_webview_thread(query, selected_model)`.

## What Worked
- Verified AppleScript launches a fresh Terminal window running `agy -p "..."` instantly.
- Tested prompt triage classification and unit checks in `test_triage.py`.
