## Goal
Remove the flawed terminal auto-expand logic that was triggering incorrectly when typing `/` into the webview textarea, and failing/causing tmux to frenzy when typing `/` into the TUI prompt box.

## Changes Made
- Modified `src/main.ts` to remove the auto-expand logic from the textarea's input event handler.
- Modified `src/main.ts` to remove the `term.onData` handler's auto-expand logic, which was reading `term.buffer.active.getLine` and checking for `startsWith('/')`. This approach was fundamentally flawed because shell prompts prevent `startsWith('/')` from matching, and frequent resizing causes tmux to recalculate viewports and redraw erratically ("frenzy").

## What Worked
- Removing the auto-expand logic entirely stabilizes the terminal and stops it from expanding at the wrong times.

## What Didn't Work / Known Issues
- Currently, typing `/` in the TUI no longer auto-expands the terminal for tall lists of commands. The user must manually expand the terminal. Dynamically resizing the viewport based on keystrokes in tmux is problematic due to terminal emulator repaints and tmux window redrawing constraints. A better approach might be explicitly sending a command from the TUI to the frontend, or keeping the terminal size manually controlled by the user.

## Architecture Notes
- The terminal auto-adjustment was tied to `term.onData`, checking `startsWith('/')` which failed to account for bash/zsh shell prompts.
- Rapid resizing of the terminal viewport (`debouncedResizePty`) during active user typing triggers disruptive redraws in tmux.
