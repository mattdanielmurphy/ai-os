## Goal
Ensure a fresh, interactive `agy` agent instance is spawned whenever the client process is not running inside the project PTY session, rather than executing prompts as a non-interactive one-off command.

## Changes Made
- **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**:
  - Updated `ensure_engine_pty` to check if the engine process (`agy` or `claude`) is actually running inside the session using `is_engine_running_proc` instead of just checking if the tmux session exists via `is_session_alive`.
  - Configured `ensure_engine_pty` to clean up and terminate the stale tmux session (`tmux kill-session -t ...`) if the engine process is not running, so that `spawn_single_pty` creates a clean, fresh session executing the interactive orchestrator.
  - Implemented `spawn_fresh_engine` Tauri command which terminates any active tmux session for the engine and spawns a new single PTY session executing the interactive engine. Registered the new command inside the Tauri generate handler.
  - Cleaned up unused legacy helper functions `is_pid_alive` and `is_session_alive`.
- **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  - Updated prompt submission handler so that when `is_engine_running` returns `false` (meaning the active interactive client process was not found) and `currentEngine` is `agy`, the frontend invokes `spawn_fresh_engine` to spawn a new fresh interactive instance of `agy`, waits 1000ms for initialization, and writes the prompt input directly to the new session's PTY.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Added entry documenting the fresh agent client spawning capabilities.

## What Worked
- Tauri compilation (`cargo check`) and frontend build (`pnpm build`) pass cleanly.
- Detection of dead client processes inside active tmux windows allows self-healing and automatic session recreation.
- Interactive routing logic ensures `agy` is always run as a persistent agent session.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Checking whether the engine process is running via process tree inspection (`is_engine_running_proc`) ensures we detect when the agent crashes or terminates even if the tmux window/pane wrapper is still active.
- Killing stale tmux sessions before calling `spawn_single_pty` avoids conflicts with the `-A` (attach) flag which would otherwise connect to a dead shell prompt session without restarting the agent.
