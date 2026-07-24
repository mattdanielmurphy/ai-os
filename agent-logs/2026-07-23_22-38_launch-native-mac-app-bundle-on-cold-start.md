## Goal
Fix cold-start execution in `triage_router.py` so that when the `ai-os` Tauri app server is not active, it launches the compiled `/Applications/ai-os.app` macOS bundle via `open` instead of spawning `bun run tauri dev`.

## User Feedback & Decisions
- Launching the Vite/Tauri dev server (`bun run tauri dev`) to handle a prompt when the app is not running is unacceptable.
- If the app is not running, it must launch the compiled application bundle `/Applications/ai-os.app` directly via macOS `open`.

## Changes Made
- Updated `open_gemini_webview_thread` in `scripts/triage_router.py`:
  - When HTTP POST to `127.0.0.1:3031/api/prompt` fails (app server down):
  - Saves the query to `~/.ai-os/pending_prompt.txt`.
  - Searches for `/Applications/ai-os.app` or `/Applications/AI-OS.app` and runs `open /Applications/ai-os.app` (or fallback `open -a "AI-OS"`).

## What Worked
- Verified `/Applications/ai-os.app` exists and opens directly via macOS `open`.
- Cold-start prompt dispatch now launches the compiled native Mac app instantly with zero dev-server overhead.
- Passed `test_triage.py` unit checks cleanly.
