## Goal
Fix a bug in the TUI where loading spinners (like in thoughts) cause the same thought text to be reprinted repeatedly in the live preview pane due to ANSI strip processing missing carriage returns (`\r`) and backspaces (`\b`).

## Changes Made
- Modified `src/main.ts` in the `pty-output` event listener where the live stream is parsed (`liveAgyStream`). 
- Added a loop to process `\r` (carriage return) by removing the current line back to the last newline (`\n`), and `\b` (backspace) by removing the last character from `liveAgyStream`. This prevents spinner frames from just appending.

## What Worked
- Properly filtering out and parsing `\r` and `\b` out of the stripped plaintext payload so the live preview doesn't just infinitely append the line being redrawn by the spinner.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `liveAgyStream` plaintext preview pane uses a simple string buffer that it replaces inside a text block. It relies on standard string manipulations to behave like a primitive TUI buffer when encountering `\r`.
