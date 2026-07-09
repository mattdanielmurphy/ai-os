## Goal
Fix the TUI live stream spinner bug where `\r` and `\b` escape characters were not properly processed, causing the loading string to duplicate in the display. Also fix the appearance of `(B` character set escape sequences.

## Changes Made
- Modified `src/main.ts` line 1194 to fix the `\r` and `\b` escape characters. In the previous fix, they were mistakenly written as `\\r` and `\\b`, which attempted to match 2-character literal strings against single characters. They are now correctly matching the `\r` and `\b` single characters.
- Modified `lastIndexOf` to search for `\n` instead of `\\n`.
- Enhanced the regex for stripping ANSI codes (`data.replace(/\x1B(?:\[[0-?]*[ -/]*[@-~]|[\(\)][a-zA-Z0-9])/g, '').replace(/\x1B/g, '')`) so it correctly strips out the `\x1B(B` character set selections, which were previously leaving orphaned `(B` text in the TUI stream.

## What Worked
Properly interpreting single control characters and correctly stripping non-CSI ANSI escapes successfully restores proper spinner formatting in the plaintext pane without artifacts or duplication.

## What Didn't Work / Known Issues
The previous attempt (2026-07-04_16-25) failed because it checked single characters against double-escaped literal strings (`'\\r'` length 2).

## Architecture Notes
The terminal PTY output is extremely raw and contains multiple types of ANSI control codes, not just `\x1B[`. It also relies heavily on `\r` without `\n` to draw frame animations.
