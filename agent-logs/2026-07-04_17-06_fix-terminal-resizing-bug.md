## Goal
Fix a bug where the terminal (tmux PTY) resizing gets desynced, causing lines to repeat incorrectly (e.g. "top line repeated 10 times") and rendering poorly when the sidebar changes size or the pane expands/collapses.

## Changes Made
- Modified `src/main.ts` `resizePty` logic.
- Prevented `fitAddon.fit()` from running if the terminal container isn't visible (`clientWidth > 0 && clientHeight > 0`).
- Replaced manual `invoke('resize_pty')` calls inside `resizePty` with `term.onResize` and `miniTerm.onResize` event listeners. 
- **Why:** `fitAddon.fit()` on a hidden or width=0 container results in extremely small dimensions (e.g., 2 cols, 1 row). The previous logic manually sent these broken dimensions to the PTY backend on every resize debounce, corrupting the tmux session. By using the `onResize` event hook and preventing `fitAddon.fit` on hidden elements, we guarantee that the PTY is only notified of valid, visible resizing calculations directly from xterm.js.
- Fixed a minor TypeScript issue around `displayValue` in the tool calls UI logic.

## What Worked
- Added robust visibility checks prior to fitting terminals.
- Bound directly to `onResize` to keep `xterm.js` and Tauri's PTY cleanly in sync.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Using `term.onResize` is the xterm.js best practice for syncing PTY bounds rather than explicitly calling IPC updates right after `fitAddon.fit()`, as `fitAddon` correctly triggers the `onResize` internally.
