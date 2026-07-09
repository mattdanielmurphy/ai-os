## Goal
Add an "open project in Finder" button for each project in the AI-OS UI.

## Changes Made
- Modified `src/main.ts` to add a new folder icon button (📁) alongside the existing delete button in the project list UI.
- Wrapped the buttons in a new `action-btns` container for cleaner hover-state handling.
- Added a click handler that calls Tauri's `open(project.path)` (imported from `@tauri-apps/api/shell`) to open the directory in Finder.
- Ensure the delete button is hidden for the root project while the folder button remains visible.

## What Worked
The buttons correctly display on hover, and Tauri's `open` function is invoked correctly with `e.stopPropagation()` so we don't accidentally switch to the project when clicking the button.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Tauri provides `@tauri-apps/api/shell` with an `open` method that opens URLs or file paths using the system's default handler (Finder on macOS).
- Projects list in `main.ts` is rendered manually via `item.innerHTML`. Event delegation is applied to the individual tab items.
