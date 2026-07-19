## Goal
Prevent "Could not connect to the server" failures on subsequent WebSocket auto-connections if the background `hermes serve` daemon dies or is killed.

## User Feedback & Decisions
- Expose a Tauri command `ensure_hermes_running` that enables the frontend TypeScript initialization chain to eagerly check and boot the backend daemon if it is not responsive on port 9119.

## Changes Made
- Modified [main.rs](file:///Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs):
  - Defined the `ensure_hermes_running` Tauri command, invoking `ensure_hermes_serve_running()` internally.
  - Registered `ensure_hermes_running` inside `tauri::generate_handler!`.
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Updated `initHermesChat(cwd)` to invoke `ensure_hermes_running` before initiating the client's `hermesChat.connect()` WebSocket promise chain.

## What Worked
- Rebuild via `bun run build` completed successfully.
- Rust compilation check (`cargo check`) succeeded.
- Dynamic auto-restarting of the background daemon works on connection attempts when port 9119 is closed.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Linking daemon health checks to the frontend `initHermesChat` initialization logic guarantees that client-side WebSocket retries gracefully recover even if the user manually kills the background python process.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
