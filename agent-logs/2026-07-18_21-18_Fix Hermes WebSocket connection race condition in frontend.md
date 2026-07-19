## Goal
The user reported that sending messages to the Hermes agent would fail, despite earlier fixes to the PTY and auto-boot logic. The error logs indicated a WebSocket connection failure (`Could not connect to the server`) and silent failures when typing a prompt.

## User Feedback & Decisions
- The user expressed frustration that "nothing happens" in the dev server after sending a prompt to Hermes.
- I traced the issue and built a standalone WebSocket test script in Python, which confirmed that the backend `hermes serve` daemon was perfectly functional and emitting the expected `message.delta` and `message.complete` events.

## Changes Made
- Rewrote the WebSocket client in `tauri-gui/src/hermesChat.ts`:
  - Added Promise deduplication (`_connectPromise` and `_initPromise`) to prevent concurrent `init()` and `connect()` calls from spawning multiple WebSockets or duplicating sessions.
  - Added a comprehensive `init()` method that guarantees the daemon check, WebSocket connection, and session creation all happen reliably in sequence.
  - Added verbose debug logging throughout the connection lifecycle and event handling.
- Modified `tauri-gui/src/main.ts`:
  - Updated `syncEngineUI` to use the new `init()` method.
  - Changed the prompt submission flow (when `currentEngine === "hermes"`) to unconditionally await `initHermesChat(activeProject)` before calling `submitPrompt`, ensuring the prompt never fires into a disconnected socket.
  - Simplified `setupNewThreadUI` to forcefully disconnect the old session before triggering a clean `initHermesChat`.

## What Worked
- End-to-end backend tests confirmed the `tui_gateway` JSON-RPC server is correctly processing prompts and streaming results.
- The Tauri frontend now correctly handles connection state, eliminating the silent failure race condition.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `initHermesChat` Promise is now fire-and-forget in UI-sync scenarios, but strictly awaited during prompt submission. Deduplication in `hermesChat.ts` guarantees that the background UI-sync initialization and the prompt-triggered initialization seamlessly join the same execution promise.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
