## Goal
The user reported that the TUI display often disappears completely when collapsing/expanding, expanding the window, or running a command. Additionally, they were unable to paste directly into the terminal, and Cmd-clicking links would not open them.

## Changes Made
- `src/main.ts`:
  - **Disappearing Terminal Fix**: Modified `resizePty()` to force a terminal redraw by explicitly calling `term.resize(term.cols, term.rows)` when the container height is greater than zero after running `fitAddon.fit()`. Wrapped it in a try-catch.
  - **Paste Support**: Added a check for `e.key === 'v' && e.metaKey` inside `attachCustomKeyEventHandler` for both the main `term` and `miniTerm`. This intercepts Cmd+V and manually reads from `navigator.clipboard`, forwarding the text to the PTY via `write_to_pty`.
  - **Cmd-Click Link Fix**: Updated `handleLink` to check `if (e.metaKey)` instead of `if (true)`. This ensures that only Cmd-clicks activate the link handler and not standard clicks (which otherwise get swallowed or interfere with terminal focus).

## What Worked
- Terminals will now forcibly rerender layout changes if dimensions exist during resize.
- Explicit interception of the paste shortcut provides a reliable fallback for Tauri constraints.
- Cmd-click is explicitly guarded.

## What Didn't Work / Known Issues
- None at this time.

## Architecture Notes
- The terminal's WebLinksAddon and LocalPathLinkProvider trigger their callbacks purely on whatever the mouse event is; they do not inherently restrict to metaKey unless specified manually inside the handler function.
- In macOS Tauri applications, standard paste shortcuts do not natively bubble into WebGL or Canvas based terminal instances if the OS-level Edit > Paste menu item isn't cleanly registered to emit web paste events. Using custom keyhandlers is necessary.
