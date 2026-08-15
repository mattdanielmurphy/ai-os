## Goal
Fix the Hermes Agent chat not working at all in the Tauri GUI.

## User Feedback & Decisions
None.

## Changes Made
- Modified [main.rs](file:///Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs):
  - Added `ensure_hermes_serve_running()` helper function to check if the `hermes serve` WebSocket daemon is running on port 9119 by attempting a TCP connection.
  - If the daemon is not running, it spawns `/Users/matt/.local/bin/hermes serve --port 9119` in the background and sleeps for 800ms to allow it to bind.
  - Integrated `ensure_hermes_serve_running()` into the `hermes` engine check inside `ensure_engine_pty()` (for existing projects) and `switch_active_project()` (for new projects).
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Extracted the Hermes chat UI visibility and event wire-up callbacks into a reusable `syncEngineUI(prevEngine?: string)` function.
  - Wired `syncEngineUI` into both the engine radio buttons change event listener and the `switchToProject` function so that switching projects properly configures/deconfigures the Hermes WebSocket connection and listeners.
- Modified [FEATURES.md](file:///Users/matt/projects/ai-os/FEATURES.md):
  - Updated the "Hermes Agent Integration & Bun Migration" feature description to detail the automatic `hermes serve` spawning and UI synchronization logic.

## What Worked
- Rebuilt the frontend successfully using `bun run build` with zero TypeScript or build errors.
- Verified that `hermes serve` successfully starts and listens on port 9119 when run via `/Users/matt/.local/bin/hermes serve --port 9119`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Checking localhost port status with a fast-failing `TcpStream::connect` is a reliable way to detect whether `hermes serve` needs to be spawned, preventing duplicate server launch processes.
- The `switchToProject` path now correctly shares the same engine initialization and WebSocket cleanup routines as the radio buttons, avoiding orphaned WebSocket connections and broken/frozen Hermes chat UI states on workspace switches.
