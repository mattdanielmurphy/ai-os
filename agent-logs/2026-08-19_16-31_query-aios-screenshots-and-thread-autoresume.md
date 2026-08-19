# `query_aios.js` Screenshot Attachments & Context-Aware Thread Auto-Resumption

## Summary
Resolved two core usability issues with `query_aios.js`:
1. **Screenshot / Image Attachments**:
   - `extractAndInlineReferencedFiles()` now detects binary image files (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tiff`, `.heic`) referenced in prompt text or URLs and routes them directly to the `filePath` parameter instead of trying to read/inline binary bytes as UTF-8 text strings.
   - Added explicit CLI flags `--screenshot <path>`, `--image <path>`, `--files <path>`, and `-f <path>`.
   - Validates existence and logs confirmed attachments before dispatching to the companion server.
2. **Context-Aware Antigravity Thread Auto-Resumption**:
   - Implemented thread state registry at `~/.ai-os/thread_map.json`.
   - Binds planner threads to `ANTIGRAVITY_CONVERSATION_ID` (or `--ag-thread <id>`).
   - Default on turn 1 of an Antigravity thread: provisions a new planner session ID and records the mapping.
   - Default on turn 2+ of the same Antigravity thread: automatically retrieves and reuses the active planner thread, incrementing turn count.
   - User/Agent override flags:
     - `--new-thread` / `-n` / `--new`: Forces creation of a fresh planner thread and updates the mapped session.
     - `--resume <id>` / `-r <id>` / `--thread <id>`: Forces resumption of a specific planner thread.
     - `--no-resume`: Disables registry reading/updating for standalone one-off executions.

## Verification
- Verified turn 1 provisions a new session ID for a conversation ID.
- Verified turn 2 automatically resumes the established session ID.
- Verified `--new-thread` cleanly overrides and resets the active session.
- Verified `--screenshot` and prompt image URI auto-detection cleanly passes paths to AI-OS without encoding errors.
