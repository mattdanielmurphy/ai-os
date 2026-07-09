## Goal
Fix a bug where the UI was displaying 50+ line long thread titles.

## Changes Made
- Modified `src-tauri/src/main.rs` in `get_thread_info`. Previously, it was searching for `<THREAD_NAME>` on the entire raw JSON string of `transcript.jsonl`. This caused it to match on the system prompt instructions or tool output responses (which could contain unescaped tags or huge chunks of JSON string data, leading to massive unintended titles being extracted).
- The logic now specifically iterates through the parsed JSON lines, checking the `PLANNER_RESPONSE` messages for the `<THREAD_NAME>` tag.
- It also correctly sets the `snippet` and fallback title using the first `USER_INPUT`, breaking out of the loop once both pieces of information are gathered.

## What Worked
- Thread naming is now robust against raw JSON escaping and tool outputs.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Parsing JSON lines using `serde_json` is fast enough that iterating the file to find the first `PLANNER_RESPONSE` doesn't noticeably impact UI rendering, and ensures we don't accidentally match on the agent's system prompt instructions or intermediate tool calls.
