## Goal
The user reported that the sidebar thread list showed useless names like "Continuing conversation from..." because the backend was naively parsing the `<USER_REQUEST>` block which contains our historical context and system prompt headers.

## Changes Made
- Modified `get_cached_thread_info` in `src-tauri/src/main.rs`.
- Added logic to strip `<SYSTEM_INSTRUCTIONS>` from the raw prompt.
- Added logic to detect "Continuing conversation from history" and isolate the actual user request via the `\nUser request:` boundary.
- The `title` and `snippet` are now generated correctly based on the actual user prompt rather than boilerplate agent prompts.

## What Worked
- Filtering string boundaries cleanly extracts the new objective/question.
- Rust string slices used properly with `find` to extract the correct substrings.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- `agy` stores all logs in JSONL format inside `~/.gemini/antigravity-cli/brain/<thread-id>/.system_generated/logs/transcript.jsonl`.
- The `ai-os` Rust backend accesses these transcripts directly to build the thread list for the sidebar, acting as a direct reader of the CLI's brain state.
