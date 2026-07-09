## Goal
Fix the bug where clicking a tab sometimes gets stuck on "[ai-os] Connecting to Engine session at..." and nothing happens.

## Changes Made
- Modified `src-tauri/src/main.rs`: Added an `is_process_alive` check to `ensure_engine_pty`.
- The Rust backend uses a PTY that connects to an underlying tmux session. If the `tmux` client attached to the PTY dies (for example, via user detachment), the PTY reader thread exits, but the background tmux session remains active.
- Previously, `ensure_engine_pty` only checked if the *engine* (e.g. `agy`) was running inside tmux, and if it was, it skipped respawning the `tmux` client, causing the UI to never receive PTY output.
- Now, it independently verifies both if the engine is alive (`agy_alive`) and if the client PTY process is alive (`client_alive`). If the client is dead but the engine is alive, it respawns the PTY (which re-attaches to tmux without killing it).
- Also added `ensure_mini_pty` to correctly respawn the mini shell client if its PTY process dies.

## What Worked
- Differentiated between engine death and client detachment.
- Preserved existing sessions when only the PTY detached.

## What Didn't Work / Known Issues
- None

## Architecture Notes
- Tauri uses `tmux` for multiplexing PTY sessions behind the scenes.
- State is preserved on UI reload because the Rust backend stays alive and maintains `state.sessions`.
