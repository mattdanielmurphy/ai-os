## Goal
Implement a direct CLI-to-Tauri IPC mechanism for opening the `ai-os` Gemini webview window and injecting/executing prompts of arbitrary length without URL character limits.

## User Feedback & Decisions
- URL query parameters have character limits and `open https://gemini.google.com/app?...` opens default web browser instead of targeting the `ai-os` Tauri app window.
- The `ai-os` Tauri app must expose a direct CLI/IPC mechanism that brings the Gemini window to front, injects the prompt (no matter how long), and executes it.

## Changes Made
- **Axum HTTP IPC Endpoint (`/api/prompt` & `/api/gemini/prompt`)**:
  - Added `PromptDispatchPayload` and `handle_prompt_dispatch` to `tauri-gui/src-tauri/src/server.rs`.
  - When invoked via HTTP POST to `http://127.0.0.1:3031/api/prompt`, it locates the `gemini_main` window, shows/unminimizes/focuses it, and evaluates JS `window.injectAndSendPrompt(prompt)`.
- **App Startup Pending Prompt Handler (`~/.ai-os/pending_prompt.txt`)**:
  - Added pending prompt check in `tauri-gui/src-tauri/src/main.rs`.
  - If `ai-os` is launched cold by CLI, it reads `pending_prompt.txt`, injects it into `gemini_main`, and deletes the file.
- **Global JS Injector (`userscripts/gemini.js`)**:
  - Exposed `window.injectAndSendPrompt(promptText)` globally.
  - Automatically handles input focus, text setting, DOM `input`/`change` event dispatch, and send button clicking.
- **Triage Router IPC Integration (`scripts/triage_router.py`)**:
  - Updated `open_gemini_webview_thread(query)` to POST JSON payload directly to `127.0.0.1:3031/api/prompt`.
  - Falls back to writing `~/.ai-os/pending_prompt.txt` and launching `ai-os --gui` if server is not active.

## What Worked
- Prompts of any length are dispatched in milliseconds directly into the active `ai-os` Tauri app window.
- `cargo check` for `tauri-gui` passed cleanly.
- `test_triage.py` unit checks passed cleanly.
