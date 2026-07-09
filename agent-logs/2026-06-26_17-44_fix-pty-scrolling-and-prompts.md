## Goal
Fix extra blank prompts and terminal scrolling issue by updating the command submit sequence and syncing PTY geometry size between frontend and Rust backend.

## Changes Made
- Modified `src/main.ts`:
  - Replaced command execution suffix from `\r\n` to `\r` to fix duplicate prompts.
  - Linked `FitAddon`'s fit callback to invoke `resize_pty` command in the Rust backend.
  - Added resize listener to window to trigger `resizePty()` and sync window dimensions.
- Modified `src-tauri/src/main.rs`:
  - Updated `AppState` to hold `pty_master` in addition to `pty_writer`.
  - Added `resize_pty` command that calls `master.resize` with the provided row and column dimensions.
  - Updated `main()` initialization to store `pair.master` inside `pty_master` Mutex.
  - Registered `resize_pty` command inside the Tauri invoke handler.
- Updated `FEATURES.md`:
  - Documented the fix and geometry sync features.

## What Worked
- Both Tauri and Rust compilations completed without errors.
- Visual and backend sync integration confirmed.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The Rust PTY master system needs to resize dynamically so the shell output correctly flows into scrollback buffers rather than overwriting existing screen rows in xterm.js.
