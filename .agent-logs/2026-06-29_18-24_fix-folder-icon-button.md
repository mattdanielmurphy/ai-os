## Goal
Fix the project folder icon button in the UI so that it correctly opens the project directory in Finder.

## Changes Made
- Modified `src/main.ts` to replace the Tauri `@tauri-apps/api/shell` `open()` call with an `invoke('open_path', { path: project.path })` call. 
- Tauri's built-in `open` was failing to properly open local folders due to restrictions/bugs, while the custom `open_path` Rust command correctly executes the native macOS `open` command.

## What Worked
- Replaced the call and tested successfully. The `open_path` command was already implemented in `src-tauri/src/main.rs` and properly used elsewhere for file links in the terminal.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Whenever possible, we should rely on the custom `open_path` Tauri command for opening local files or directories, as Tauri's native `open` shell API has URL parsing restrictions that often drop paths on macOS.
