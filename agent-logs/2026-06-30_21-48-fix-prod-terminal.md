## Goal
Enable opening dev tools via `cmd-opt-I` in the built version of the app and fix the issue where the terminal doesn't connect in production.

## Changes Made
- Added the `devtools` feature to `tauri` dependencies in `src-tauri/Cargo.toml`.
- Added an `open_devtools` Tauri command in `src-tauri/src/main.rs`.
- Added a global keyboard event listener in `src/main.ts` to capture `Cmd+Opt+I` and trigger the `open_devtools` command.
- Updated the `PATH` environment variable configuration in `main.rs` to include common user bin directories (e.g., `~/.local/bin`, `~/.cargo/bin`, `/opt/homebrew/bin`, `~/.gemini/antigravity-cli/bin`). 

## What Worked
- The Tauri build succeeded. The updated PATH allows `portable_pty::CommandBuilder` to successfully spawn the user's local installations of tools like `tmux`, `agy`, and `claude` even when the app is launched as a macOS App Bundle with a highly restricted default PATH.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- The app uses `portable_pty` rather than Tauri's shell APIs to spawn the terminal. `portable_pty` relies on the process `PATH` to resolve commands, which we manually expand in `main()` to bridge the gap between development shells and the built GUI bundle's environment.
