## Goal
Enhance the sidebar display to make project pathnames visible and format all paths globally in the UI so that relative project paths are shown for files inside the project, and `~` is used instead of `/Users/matthewmurphy` for external files.

## Changes Made
1. **Frontend helper (`src/main.ts`):**
   - Added `formatPathForUser` to check if a path is within the active project, rendering it relative to the project root, or returning the path with `/Users/matthewmurphy` replaced with `~` otherwise.
2. **Sidebar Projects rendering (`src/main.ts`):**
   - Updated `renderProjects` to show both the project name and the formatted project path (`~/projects/...`) in a vertical flex block.
3. **Paths throughout the UI (`src/main.ts`):**
   - Updated tool call links in the timeline to format display paths via `formatPathForUser`.
   - Updated edited files title tooltip using `formatPathForUser`.
   - Formatted all connecting/loading terminal messages with `formatPathForUser`.
   - Set the current directory header text content with `formatPathForUser`.
4. **Documentation (`FEATURES.md`):**
   - Documented the changes under the `[2026-06-30]` section.

## What Worked
- TypeScript compiled cleanly without errors.
- Rust backend compiled cleanly without errors.
- Sidebar projects render both name and path beautifully, preventing confusion between identically named auto-created projects.
- UI elements display clean relative paths for files inside projects, and tilde representations for home directory files.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `formatPathForUser` helper provides a single, uniform place for sanitizing and formatting path strings before they reach the user interface.
