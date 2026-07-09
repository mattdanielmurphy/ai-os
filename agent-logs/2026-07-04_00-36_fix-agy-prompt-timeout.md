## Goal
Fix an issue where starting a new thread opens `agy` in the terminal but fails to automatically paste the prompt and historical context into the PTY.

## Changes Made
- Modified `src/main.ts`: Increased the timeout after `spawn_fresh_engine` from 500ms to 3000ms.

## What Worked
- By extending the delay before sending the `write_to_pty` payload, we ensure that the raw PTY and Python `prompt_toolkit` have enough time to initialize and stabilize in raw mode. Previously, sending the prompt after only 500ms caused the input buffer to be flushed or dropped during the `tcsetattr` raw mode initialization sequence of the interactive CLI.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- This issue was exacerbated by the removal of the tmux middleman (which previously helped shield or buffer keystrokes during the split-second startup process of the underlying shell). 
