## Goal
Refactor the UI layout in `index.html` to relocate the engine toggle to a new top header bar, clean up the bottom input area, and resolve the terminal visual clipping issue at the bottom of the screen.

## Changes Made
- **index.html**:
  - Moved the radio button engine toggle container (Claude/Agy toggle) to a new slim top header bar above the `#terminal-container`.
  - Used Tailwind to format the top bar to be compact (`p-1 px-4 text-xs font-semibold bg-gray-800 border-b border-gray-700`).
  - Updated classes on `#terminal-container` to include `min-h-0` and explicit bottom padding `pb-6` to avoid xterm.js drawing text rows underneath the bottom input textarea.
  - Cleaned up the bottom input area container by removing the internal toggle border/layout styles.
- **FEATURES.md**:
  - Documented the changes under a new entry `[2026-06-27] UI Refactoring & Visual Clipping Fix`.

## What Worked
- Relocating the toggle structure was successful and `src/main.ts` DOM query selectors target `input[name="engine"]` which matches the relocated elements automatically.
- Adjusting `#terminal-container` classes correctly prevents visual text drawing rows underneath the input text area.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The terminal fit addon dynamically sizes xterm.js columns and rows to fill `#terminal-container`. Adding bottom padding (`pb-6`) limits the visible dimension calculation of the terminal container, keeping the rows constrained and clear of the bottom prompt input textarea.
