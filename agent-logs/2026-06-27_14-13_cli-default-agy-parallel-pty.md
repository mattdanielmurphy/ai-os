## Goal
Default the CLI mode to Agy rather than Claude, handle custom arguments like `--help` locally, and optimize Tauri's project tab loading performance.

## Changes Made
- **`bin/ai-os`**: Rewrote option parsing. The script now defaults to `agy` engine rather than `claude`. Supported `--agy`, `--claude`, and `--gui` options. Added a custom `show_help` function which intercepts `-h` and `--help` to show helper information for `ai-os` itself instead of forwarding to Claude or Agy.
- **`package.json`**: Modified `"cli"` script to invoke `./bin/ai-os` directly so that it defaults to the `agy` orchestrator.
- **`src-tauri/src/main.rs`**:
  - Cached the `is_tmux_available` command check using `std::sync::OnceLock<bool>` to avoid executing `which tmux` repeatedly on every PTY spawn.
  - Refactored `switch_active_project` to spawn the `mini` terminal PTY and the engine PTY concurrently in parallel threads using `std::thread::spawn`, halving the tab switching latency when opening a new project tab.

## What Worked
- Custom option parsing in `bin/ai-os` intercepts `--help` cleanly.
- Parallel thread spawning for PTY sessions compiles and functions without blocking Tauri's main thread.
- Caching `is_tmux_available` with `OnceLock` prevents process fork overhead.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Spawning PTYs in parallel avoids blocking Tauri's renderer loop sequentially on two subprocess spawns when loading project tabs.
