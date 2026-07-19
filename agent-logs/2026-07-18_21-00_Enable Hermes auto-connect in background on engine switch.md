## Goal
Ensure the Hermes WebSocket chat connection is established automatically when switching engines or loading the project, preventing the "Hermes chat not connected, trying to connect..." warning on prompt submission.

## User Feedback & Decisions
- Automatically trigger background connection in `syncEngineUI` when switching to the `hermes` engine.
- Prevent duplicate/overlapping session creation inside `initHermesChat`.

## Changes Made
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Refactored `initHermesChat` to return a resolved promise if already connected with a session ID, preventing duplicate session creation.
  - Updated `syncEngineUI` to call `initHermesChat().catch(...)` immediately in the background on transition to the `hermes` engine.

## What Worked
- Vite frontend compilation (`bun run build`) succeeded without issues.
- Background WebSocket connection successfully triggers on engine switch/project load, removing the delayed warning.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Initializing the connection eagerly on engine selection minimizes user-perceived connection latency and prevents console warnings on prompt submission.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
