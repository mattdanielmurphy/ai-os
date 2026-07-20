## Goal
Implement a left sidebar listing the user's active projects (sorted by recency, styled like tabs with distinct random colors). Enable project switching where console screens are restored and the active shell is swapped per project. Add a terminal command mode triggered by typing `!` or typing `exit`/pressing `Escape` to revert back to prompt input mode.

## Changes Made
* **`index.html`**:
  - Inserted left `#projects-sidebar` structure and styling.
  - Added project adding button (`#add-project-btn`) and list wrapper (`#projects-list`).
  - Included a `#mode-badge` indicator and a breadcrumb panel `#current-dir-path` to identify the active path.
* **`src-tauri/src/main.rs`**:
  - Refactored `AppState` to support a `HashMap` of active `ProjectSession` instances, each holding its own PTY masters, writers, and child shell PIDs.
  - Created backend commands `initialize_project_session`, `switch_active_project`, `write_to_pty`, `resize_pty`, and `is_engine_running` configured to process path-based project targeting.
* **`src/main.ts`**:
  - Implemented client state tracking for loaded `projects` and active project selection.
  - Created `switchToProject` to reset xterm consoles, populate text outputs from an in-memory buffer cache, switch sessions in Tauri, and query project contexts.
  - Implemented `setMode` for toggling terminal command inputs when typing `!` at prompt start or exit commands.
* **`FEATURES.md`**:
  - Documented the project sidebar layout, PTY caching layer, and terminal toggle features.

## What Worked
* Dynamic session initialization and swapping compiles and runs perfectly under Tauri.
* Project sidebar automatically updates recency sorts on localStorage and styles tabs with distinct, randomly-assigned pastel colors.
* Command mode intercepts and forwards direct raw PTY writes correctly when typing '!'.

## What Didn't Work / Known Issues
* None detected.

## Architecture Notes
* In-memory console buffer `terminalBuffers` avoids re-reading logs recursively while maintaining high UI performance.
* Setting `$PWD` dynamically via Tauri's `portable_pty` CWD spawning allows shells to open immediately in their respective project directories.
