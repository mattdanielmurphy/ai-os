## Goal
When a prompt is escalated or routed to Gemini, open the `ai-os` Tauri app / `gemini.google.com` webview with a new conversation thread containing the prompt, rather than opening `agy` CLI in terminal.

## User Feedback & Decisions
- Opening `agy` CLI for escalated prompts is a poor user experience.
- Prompts routed to Gemini should open the `ai-os` Tauri app / `gemini.google.com` as a new webview thread with the prompt auto-populated and sent.

## Changes Made
- Updated `userscripts/gemini.js` with `checkUrlPromptAndAutoSend()`:
  - Parses `?prompt=` / `?q=` URL parameters.
  - Automatically inserts the prompt into Gemini's rich input element, triggers DOM events, and clicks the Send button to start a new webview conversation thread.
  - Cleans up `?prompt=` from `window.location`.
- Updated `scripts/triage_router.py`:
  - Added `open_gemini_webview_thread(query, model)` function.
  - Copies prompt to macOS system clipboard (`pbcopy`).
  - Launches `open "https://gemini.google.com/app?prompt=<encoded_prompt>"`.
  - Preserved CLI mode (`--cli`, `--terminal`, `--agy`) if user explicitly requests terminal execution.

## What Worked
- Queries that escalate to Gemini automatically launch the `ai-os` webview thread with the prompt populated and submitted instantly.
- `test_triage.py` unit checks passed cleanly.
