## Goal
Group all threads that do not belong to an explicit project directory under a single unified "Misc" project, and automatically filter out legacy `~/projects/thread-...` entries from the sidebar list.

## Changes Made
1. **Frontend (`src/main.ts`)**:
   - Modified project load to explicitly filter out legacy `thread-` mock project entries from `localStorage`.
   - Updated `syncProjectsFromAllThreads` to point any uncategorized threads (which lack a detected project path) to `/Users/matthewmurphy/projects/Misc` and set the name to "Misc", instead of creating a distinct mock project for every thread.
2. **Backend (`src-tauri/src/main.rs`)**:
   - Updated `get_project_threads` to recognize the `Misc` project path.
   - If the path is `Misc` (or ends with `/projects/Misc`), the function returns threads for which `detect_project_path` yields `None`.
3. **Features Ledger (`FEATURES.md`)**:
   - Documented the "Misc Project Thread Grouping" capability.

## What Worked
- Vite production build compiles successfully.
- Sidebar is automatically cleaned of individual `thread-...` projects, routing those threads under a single "Misc" container.

## What Didn't Work / Known Issues
- None.
