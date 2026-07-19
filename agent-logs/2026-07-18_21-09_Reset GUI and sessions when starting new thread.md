## Goal
Fix the bug where starting a new thread/conversation does not clear the previous thread's messages or terminal buffer from the GUI view.

## User Feedback & Decisions
- Create a dedicated `setupNewThreadUI` utility to clear all thread UI states (terminal screen, markdown preview pane, and Hermes messages container) when starting a new thread.
- For Hermes, start a fresh session instead of continuing the previous session in the backend.

## Changes Made
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Defined the `setupNewThreadUI()` helper:
    - Clears the terminal screen (`term.reset()`) and prints a welcome message.
    - Resets the Markdown preview pane.
    - Resets the Hermes chat UI's messages list back to the welcome state.
    - Closes the active Hermes WebSocket session (`hermesChat.closeSession()`) and initializes a fresh session (`initHermesChat(activeProject)`).
  - Invoked `setupNewThreadUI()` in:
    - The "+" start new thread button click handler.
    - The "New Thread" sidebar placeholder click handler.

## What Worked
- Rebuild via `bun run build` completed successfully.
- Clicking the "+" button now successfully wipes the terminal buffer, clears prior Hermes logs, and initiates a clean workspace session.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Eagerly resetting session state in the client ensures that conversation history is cleared locally and is structurally isolated from previous threads in the backend agent runtime.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
