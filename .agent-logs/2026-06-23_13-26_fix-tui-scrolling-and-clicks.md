## Goal
Fix two main TUI issues:
1. Users were unable to scroll back through logs/chat in the TUI window.
2. Clicking "Okay" (or "Cancel") on the Self-Reflection question box did not trigger any action, even though hover effects functioned correctly.

## Changes Made
- `src/index.js`:
  - Added `mouse: true` and `keys: true` to the `blessed.question` configuration in `askAcceptIgnoreTui` to allow mouse clicks and keys.
  - Added `mouse: true` and `keys: true` to the `blessed.box` and `blessed.textbox` configurations in `askQuestion` (TUI branch) to ensure proper interaction.
  - Enabled mouse-wheel scrolling on the TUI Log widget by setting `mouse: true`, `keys: true`, and `alwaysScroll: true`.
  - Added global key listeners on `tuiScreen` for `pageup` and `pagedown` to scroll `tuiLogWidget` by `10` lines up or down.
  - Added `pageup` and `pagedown` key handlers in the input textarea (`tuiInputWidget.on('keypress')`) to scroll `tuiLogWidget` directly while typing.
- `FEATURES.md`:
  - Documented the new mouse click support for TUI dialogs and PageUp/PageDown keyboard and mouse-wheel scrolling for the logs view.

## What Worked
- Enabling `mouse: true` and `keys: true` on the Blessed question box and textboxes correctly maps and routes clicks to the underlying elements (e.g. "Okay" and "Cancel" buttons), allowing interactive questions to be answered.
- Setting `mouse: true`, `keys: true`, and `alwaysScroll: true` on the log widget enables smooth mouse scroll wheel tracking.
- Adding the `pageup`/`pagedown` key handlers enables fast keyboard-driven log scrolling.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- In `neo-blessed`, parent container elements must have `mouse: true` and `keys: true` explicitly configured for click events to successfully bubble and execute listeners on interactive child elements like buttons.
