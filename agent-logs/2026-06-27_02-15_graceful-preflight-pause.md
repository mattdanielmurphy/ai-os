## Goal
- Implement a graceful pause feature checking both Network and I/O (files & child processes) guards before suspending the process.
- Avoid interrupting file writes or network requests by implementing a "Pending Pause" state.

## Changes Made
- **`src-tauri/src/main.rs`**:
  - Implemented safe graceful-pause checkers `find_agent_pid`, `has_open_write_files`, `has_active_network_traffic`, and `has_child_processes` using shell commands `lsof` and `ps`.
  - Re-wrote `toggle_process_pause` to enter a `Pending` state and execute a polling thread (every 50ms) to check safe pre-flight metrics before executing `SIGTSTP`.
- **`src/main.ts`**:
  - Implemented three-state Pause button UI management (`Running`, `Pending`, and `Paused`).
  - Subscribed to the `pause-status` event from the Tauri backend to dynamically update the UI status.

## What Worked
- Polling thread safety verification loop in Rust evaluates constraints cleanly.
- Tauri event subscription works, updating UI elements to show "Pending..." with an active pulse animation.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Checking regular files (`REG`) in `lsof` filters out standard system descriptors or TTY channels, focusing strictly on write/append active outputs.
