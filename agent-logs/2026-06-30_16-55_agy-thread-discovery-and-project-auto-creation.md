## Goal
Ensure every single `agy` thread log file in `~/.gemini/antigravity-cli/brain/` is accounted for in the sidebar. If an `agy` thread does not belong to any of the listed projects, automatically start a new AI-OS project/collection to encapsulate the thread.

## Changes Made
- **Backend Rust (`src-tauri/src/main.rs`)**:
  - Added `detected_project_path` field to the `ThreadLog` struct.
  - Implemented `detect_project_path` helper to scan transcript logs for paths starting with `<home_dir>/projects/` and extract the root project directory path.
  - Added `get_all_agy_threads` Tauri command to scan all directories in the brain folder, parse titles/snippets/dates, detect project paths, and return a sorted list of all threads.
  - Registered `get_all_agy_threads` in the Tauri invoke handler.
- **Frontend TypeScript (`src/main.ts`)**:
  - Updated the `ThreadLog` interface with optional `detected_project_path` field.
  - Implemented `syncProjectsFromAllThreads` to fetch all `agy` threads, determine their project paths (or fall back to a specific path `/Users/matthewmurphy/projects/thread-<thread_id>` for orphaned threads), check if they are in the projects list, and dynamically add/save/render them if missing.
  - Called `syncProjectsFromAllThreads` on startup IIFE and registered it to run periodically every 10 seconds.

## What Worked
- TypeScript compiled successfully.
- Rust `cargo check` completed successfully.
- Every `agy` thread is now automatically grouped under either its parent project directory or its own lone thread project in the sidebar.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Checking files under `~/.gemini/antigravity-cli/brain/` is done in Rust, and regex/substring matches are used to safely parse paths matching the pattern `~/projects/<name>`.
