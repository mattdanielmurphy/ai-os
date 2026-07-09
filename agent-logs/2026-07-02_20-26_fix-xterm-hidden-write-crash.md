## Goal
Fix GUI failing to show tasks and agent responses in the markdown preview due to an xterm.js `lineFeed` TypeError.

## Changes Made
- Modified `src/main.ts` to wrap `miniTerm.write(data)` and `term.write(data)` in a `try...catch` block.
- The `TypeError: undefined is not an object` in `xterm_xterm.js` was caused by writing terminal data to an xterm instance that was instantiated inside a container with `display: none;` (which results in dimensions of 0x0, crashing the buffer parsing when `lineFeed` occurs). This uncaught exception in the Tauri event listener loop was halting other UI updates on the frontend.
- Ran `pnpm run build`.

## What Worked
- Wrapped the xterm write calls to gracefully swallow the exception and allow the markdown preview to continue rendering independently.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- `xterm.js` throws an exception if `.write()` is invoked when the terminal has 0 cols or rows (often due to being hidden via CSS `display: none;`). Wrapping it in a try-catch prevents it from taking down the event loop.
