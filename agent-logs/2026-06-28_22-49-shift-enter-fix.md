## Goal
Fix an issue where Shift-Enter fires as a normal Enter in the tmux TUIs (xterm.js terminals) instead of inserting a newline.

## Changes Made
- Modified `src/main.ts` to attach a custom key event handler to `term` (Engine Terminal) and `miniTerm` (Terminal Mode).
- Intercepted `Shift-Enter` and mapped it to send `\x1b\x0d` (Escape+Enter) to the PTY instead of the default `\r`. This allows prompt toolkits and shells inside the tmux session to interpret it as an "insert newline" command instead of a hard Enter.

## What Worked
- Verified that `xterm.js` instances intercept `e.shiftKey` and `e.key === 'Enter'` and prevent default.
- Sent the appropriate Escape-Enter payload (`\x1b\x0d`) to `invoke('write_to_pty', ...)`.
- Re-built successfully with `vite build`.

## What Didn't Work / Known Issues
- None so far. The standard textarea prompt handling already supported Shift-Enter correctly. This fix strictly addresses the behavior inside the nested TMUX terminal view.

## Architecture Notes
- The terminal instances are running standard xterm.js which defaults to emitting `\r` (carriage return) for Shift-Enter exactly as it does for plain Enter. By intercepting it, we leverage the common CLI/TUI paradigm where Alt/Meta-Enter acts as an in-prompt newline break.
