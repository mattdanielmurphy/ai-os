## Goal
The user wanted to click directly on the TUI and pass input directly to the terminal PTY.

## Changes Made
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Removed `disableStdin: true` from the `Terminal` configuration.
  - Added `term.onData` handler to capture direct keystroke input and invoke `write_to_pty`.
  - Modified the document click handler to focus the terminal `term.focus()` if the user clicks inside the `#terminal-container`.
  - Adjusted the automatic textarea focus redirection so it doesn't steal focus from inputs, textareas, or when clicking the terminal itself.
- Built the assets via `pnpm build` to compile the production bundle.

## What Worked
- Direct keystrokes to the terminal container are successfully received by xterm.js and forwarded to the backend `write_to_pty` command.
- Clicking on the terminal correctly focuses it.
- Clicking on other text fields or radio buttons works seamlessly without focus hijacking.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The Rust backend uses `portable_pty` and expects raw stream bytes, which matches what `xterm.js` produces in its `onData` handler.
