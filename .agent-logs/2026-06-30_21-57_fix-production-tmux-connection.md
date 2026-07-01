## Goal
Fix the built version of the app where it doesn't connect to tmux instances and throws `[Error] Unhandled Promise Rejection: Input/output error (os error 5)` in production.

## Changes Made
- Modified `src-tauri/src/main.rs` to explicitly set `TERM=xterm-256color` in `portable_pty::CommandBuilder` for spawned terminals.
- Modified `src-tauri/src/main.rs` to apply the `PATH` fallback unconditionally, instead of only modifying `PATH` when `std::env::var("PATH")` is already `Ok`.

## What Worked
- By explicitly setting the `TERM` variable, `tmux` now correctly identifies the PTY environment and starts the sessions. Previously, `tmux` exited immediately with "terminal does not support clear" because `TERM` was unset in the macOS LaunchServices (App Bundle) environment.
- The `PATH` is now correctly modified with fallback logic so `tmux` and `agy` binaries are found properly.
- The PTYs spawn correctly and the frontend connects without `os error 5` (which was caused by `portable_pty` failing on `TIOCSWINSZ` resize ioctl after the child exited immediately).

## What Didn't Work / Known Issues
- None so far. The built app bundle now connects successfully.

## Architecture Notes
- macOS App Bundles launched by Finder or LaunchServices execute with an almost entirely empty environment (no `TERM`, minimal `PATH`, etc.). The `portable_pty` crate sets `TERM=xterm-256color` internally on Unix, but it seems to require us to manually push it to the `CommandBuilder` if the environment is completely stripped out, otherwise tools like `tmux` will immediately fail to start.
