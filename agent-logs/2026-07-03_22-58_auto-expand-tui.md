## Goal
Implement auto-expansion of the TUI terminal when it enters an interactive state or asks for user input, using the active terminal buffer instead of relying on slow polling.

## Changes Made
- Modified `src/main.ts` inside the `pty-output` event listener.
- Implemented a parser that checks the last 5 lines of `term.buffer.active` whenever new data is written.
- Added a RegEx that checks for common CLI interactive prompts (`? `, `> `, `(y/n)`, `[y/N]`, `Select `, `Choose `, `Approve?`, or ending with `❯`).
- If an interactive prompt is detected and the TUI is currently collapsed (`!isTuiExpanded`), it simulates a click on `toggle-tui-btn` to automatically maximize the TUI so the user can see and respond immediately.

## What Worked
- Accessing `term.buffer.active` synchronously after `term.write(data)` successfully captures the fully parsed ANSI-free text of the current TUI state.

## What Didn't Work / Known Issues
- Full live stream extraction into the custom Markdown log layout is still pending; for now, this ensures the TUI pops open when action is required.
