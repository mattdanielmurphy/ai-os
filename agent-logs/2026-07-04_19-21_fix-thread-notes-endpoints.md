## Goal
Fix the missing "thread notes" endpoints that caused the file reads/writes to fail for the thread notes sidebar.

## Changes Made
- `src-tauri/src/main.rs`: Implemented `read_thread_notes_file` and `write_thread_notes_file` endpoints and registered them in the `invoke_handler`. These endpoints specifically read/write from `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/thread-notes.md` to conform to the strict note file path requirement. Added `std::fs::create_dir_all` to ensure the directory exists before writing if it hasn't been created yet.

## What Worked
- Endpoints were added. Cargo check succeeds.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The Tauri commands strictly write to the user's Obsidian directory instead of the project root as mandated by the system directive, resolving the conflicting instruction from the user vs the directive.
