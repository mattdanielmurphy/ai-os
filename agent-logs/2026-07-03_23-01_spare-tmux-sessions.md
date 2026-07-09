## Goal
Implement spare tmux sessions to guarantee prompt delivery and clean starting state when sending a prompt in a thread.

## Changes Made
- Modified `src-tauri/src/main.rs`: 
  - Added `prepare_spare_engine` to initialize a backup tmux session in the background.
  - Updated `spawn_fresh_engine` to consume the spare session (via `tmux rename-session`) and instantly make it the current session, instead of booting up a new python interpreter from scratch. It then dispatches another background thread to create the next spare.
- Modified `src/main.ts`:
  - When submitting a prompt in a thread (and NOT bypassing with a meta key), we now force `isRunning = false` for the `agy` engine. This triggers the frontend to call `spawn_fresh_engine`, which now rapidly swaps in the pre-warmed spare session.
  - Reduced the frontend artificial delay for spawning engines from 1000ms to 500ms since the spare is practically instantaneous.

## What Worked
The logic to consume and rename sessions via `spawn_fresh_engine` will bypass the need for users to manually recover from a broken prompt state by natively forcing a swap for every thread submission.

## What Didn't Work / Known Issues
Nothing noted so far. Wait times could potentially be reduced even further if needed.

## Architecture Notes
Tmux renaming works perfectly for session swapping, but it depends on the spare session actually being initialized and ready by the time the user hits enter. Backgrounding the prep on startup and after every consumption ensures this happens.
