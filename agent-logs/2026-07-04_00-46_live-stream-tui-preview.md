## Goal
The user wanted to stream the TUI terminal text output (agent thoughts, tool calls, and plaintext final response) immediately into the UI instead of waiting for the `transcript.jsonl` log file to update. When the log file updates, the plaintext stream should disappear and be replaced by the properly formatted markdown block.

## Changes Made
- Modified `src/main.ts` to add a global `liveAgyStream` string state.
- Hooked into the backend `pty-output` event listener for `terminal_type === 'agy'`.
- Intercepted the text stream, stripped its ANSI escape codes using regex, and accumulated it into `liveAgyStream` (capped at 20,000 characters).
- Updated the HTML generation inside `renderCustomTuiLog()` to inject a `<div id="live-stream-pane">` inside the existing "Agent is thinking..." indicator container.
- Added live DOM updating in the PTY event listener to `textContent` the `live-stream-pane` dynamically on every chunk and auto-scroll the pane.
- Added logic inside the log polling mechanism to automatically clear the `liveAgyStream` string back to empty whenever the `transcript.jsonl` log updates or the thread ID switches.

## What Worked
The real-time streaming works perfectly by scraping and stripping the TUI data chunk stream and appending it locally in the UI, then seamlessly replacing it with the `transcript.jsonl` parsed payload when the engine commits a step.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `formatMarkdown(data)` wrapper intercepts data for TUI view styling just before the cache buffer. Striping the ANSI codes from this chunk allows us to render perfectly clean plaintext agent thinking and steps without any lag.
