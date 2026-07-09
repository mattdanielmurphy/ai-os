## Goal
Fix the issue where on startup the project is loaded but the threads list says "Loading threads..." forever until switching projects, and make the app recall the most recent thread automatically. Also, collapse agentic (tool call) steps in the output timeline, leaving only the latest 2 visible by default.

## Changes Made
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Extracted tool call formatting into a new shared `buildTimelineHtml` helper function.
  - Implemented logic in `buildTimelineHtml` to group consecutive tool call steps and collapse older ones using a `<details>` element if there are more than 2 steps, displaying only the latest 2.
  - Refactored `renderCustomTuiLog` and `renderHistoricalThreadLog` to use the new `buildTimelineHtml` formatter.
  - Updated `switchToProject` to support an optional `autoSelectFirstThread` parameter, propagating it to `renderProjectThreads`.
  - Updated `renderProjectThreads` to automatically click/select the first thread (which is the most recent thread, sorted descending by modification time) when `autoSelectFirstThread` is true.
  - Corrected the startup IIFE to automatically resolve `activeProject` to the most recent active project in sorted `projects` list on startup (if `get_initial_project` returns null), and call `switchToProject(activeProject, true)` to auto-load the most recent thread.
  - Removed the redundant/late `renderProjects()` call from the startup IIFE that was overwriting and clearing the threads list back to "Loading..." after the initial load completed.

## What Worked
- TypeScript compiled successfully using `pnpm build`.
- Automatic recall of the most active project and thread on startup, with a clean collapsed timeline steps presentation.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The threads list DOM container (`#project-threads-list`) is generated inside `renderProjects` for the active project item. Any subsequent calls to `renderProjects` will recreate and overwrite this container with a "Loading..." placeholder. So, calling `renderProjects` synchronously after triggering an asynchronous thread fetch like `renderProjectThreads` will wipe out the fetched thread list.
