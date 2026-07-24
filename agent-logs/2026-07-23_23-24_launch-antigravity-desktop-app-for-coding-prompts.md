## Goal
Update `triage_router.py` so that coding, file, and codebase search prompts open `/Applications/Antigravity.app` (the Antigravity IDE desktop application), rather than launching `agy` in terminal.

## User Feedback & Decisions
- "Antigravity" refers to `/Applications/Antigravity.app`, not `agy` in terminal.
- When asking for files, codebase search, or coding tasks, triage should activate `/Applications/Antigravity.app` and start a new conversation.

## Changes Made
- Updated `scripts/triage_router.py`:
  - Replaced terminal launcher with `launch_antigravity_app(query, model)`.
  - Places the prompt onto the macOS system clipboard (`pbcopy`).
  - Executes AppleScript to activate `/Applications/Antigravity.app`, send `Cmd + N` (New Conversation), `Cmd + V` (Paste prompt), and `Return`.
  - Maintains dual routing: coding/file prompts -> `/Applications/Antigravity.app`, general questions -> `ai-os` Gemini Webview.

## What Worked
- Verified `/Applications/Antigravity.app` (bundle ID `com.google.antigravity`) activates and handles UI automation cleanly.
- `test_triage.py` unit checks passed.
