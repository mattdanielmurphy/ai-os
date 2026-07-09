## Goal
Sanitize legacy and newly synced projects in the frontend, stripping trailing formatting characters/markdown symbols and merging duplicate paths to completely clean up sidebar project fragmentation.

## Changes Made
1. **Frontend (`src/main.ts`)**:
   - Updated the `projects` loader initializer to sanitize paths and names parsed from `localStorage`.
   - Implemented duplicate merging in the initializer by mapping project paths to a unique map and keeping the version with the latest `lastActive` timestamp.
   - Added immediate persistence (`localStorage.setItem`) on startup if cleanup/deduplication altered the project count.
   - Updated `syncProjectsFromAllThreads` to strip formatting/markdown suffix symbols from synced paths and names to prevent future duplicate registration.
2. **Features Log (`FEATURES.md`)**:
   - Documented the changes under `[2026-06-30]`.

## What Worked
- Project paths loading from local storage are properly sanitized, resolving duplicate entries in the sidebar dynamically.
- Compiles cleanly and builds successfully via Vite.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Dynamic sync of projects from thread logs can produce malformed paths if the underlying threads contain raw transcripts referencing styled paths. By applying sanitization at both the storage loading boundary and the synchronization boundary, we ensure the UI remains fully synchronized and correct.
