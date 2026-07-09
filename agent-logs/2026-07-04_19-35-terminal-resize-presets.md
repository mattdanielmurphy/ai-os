## Goal
User wanted 3 terminal height states they could switch between intuitively, a resize bar to configure the states, and for the app to remember those states. They also requested app state persistence on relaunch for window size/position, sidebar-width, and the terminal height presets.

## Changes Made
- Modified `index.html`: Added a draggable resize handle (`#tui-resize-handle`) to the `tui-toggle-bar` and 3 preset buttons (1, 2, 3) to intuitively cycle between terminal heights.
- Modified `src/styles.css`: Added styles for the new `.tui-resize-handle`, `.terminal-presets`, and `.preset-btn` elements.
- Modified `src/main.ts`:
  - Added `restoreWindowState()` at the top to save and restore `appWindow` dimensions and position on load using `@tauri-apps/api/window`.
  - Updated the sidebar resizing logic to persist `sidebarWidth` to `localStorage` and read it back on launch.
  - Implemented terminal preset logic: Created an array of 3 height values, persisted them in `localStorage`, and applied them when the preset buttons are clicked. Dragging the new resize handle updates the *current* active preset's value in real-time.
  - Updated the interactive auto-expand logic: when the engine prompts for user input, if the terminal is on preset 1 (the smallest), it will automatically jump to preset 2 (medium) to ensure visibility, instead of relying on the removed boolean toggles.

## What Worked
- Replaced the simple toggle logic with the 3 preset buttons.
- Drag-to-resize successfully adjusts the current preset.
- Tauri window state persistence.

## What Didn't Work / Known Issues
- `vite build` throws a rollup darwin module not found error natively which is an unrelated `pnpm` issue, but `tsc` compilation succeeded cleanly.

## Architecture Notes
- Tauri state persistence is easily handled via `@tauri-apps/api/window` events (`onResized` / `onMoved`).
- Replaced `isTuiExpanded` legacy logic.
