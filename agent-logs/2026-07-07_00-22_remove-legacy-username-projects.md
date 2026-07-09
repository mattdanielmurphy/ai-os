## Goal
Filter out and remove legacy projects referencing the old user path `/Users/matthewmurphy` from the sidebar and project lists.

## Changes Made
1. **`src/main.ts` (Project Loader):** Added a condition to skip/ignore any project path containing `/Users/matthewmurphy` when loading projects from `localStorage` (`ai-os-projects`).
2. **`src/main.ts` (`syncProjectsFromAllThreads`):** Added a condition to skip project synchronization for thread logs referencing the legacy `/Users/matthewmurphy` path.
3. **Rebuild:** Successfully rebuilt frontend bundles to `dist/` with `pnpm run build`.

## What Worked
- Filtering out legacy paths from both loading and runtime syncing ensures they no longer populate or display in the Projects sidebar.
- Rebuilding compiles all TypeScript and Vite output successfully.

## What Didn't Work / Known Issues
None.

## Architecture Notes
Projects list stored in client-side `localStorage` (`ai-os-projects`) is automatically sanitized on load and when threads are scanned/synced.
