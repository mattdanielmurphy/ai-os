## Goal
Fix a bug where the UI was displaying the UUID as the thread title, and the prompt as the subtitle, instead of using the extracted `<THREAD_NAME>`. The user also requested debugging logs to trace the extraction logic.

## Changes Made
- Discovered that `src-tauri/src/main.rs` in `get_threads` and `get_misc_threads` was querying `get_cached_thread_info` using the `latest_filepath` (the most recent subagent's transcript).
- Subagents often don't have `<THREAD_NAME>` generated, and their user prompts might not parse cleanly, leading to the thread ID being returned as the title and a fallback snippet.
- Modified `get_threads` and `get_misc_threads` to parse BOTH the `root_filepath` and `latest_filepath`. The `mtime` (for UI sorting) and `project_path` still come from the latest thread, but the `title` and `snippet` are now correctly pulled from the `root_info` (which contains the user's initial prompt and the agent's `<THREAD_NAME>` generation).
- Added `println!` debug logs in `get_cached_thread_info` for when a title is extracted from `PLANNER_RESPONSE`, when it falls back to a prompt, and when a snippet is set.

## What Worked
- Re-pointed the UI presentation logic to the root thread, successfully hiding the UUID and showing the expected thread name.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Thread histories group multiple subagent runs by mapping them to their root thread ID. The root thread contains the primary context and generated title, while the leaves dictate the active sorting order based on recent modifications.
