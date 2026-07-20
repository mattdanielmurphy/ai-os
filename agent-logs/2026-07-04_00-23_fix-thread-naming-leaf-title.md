## Goal
Fix Thread Naming UUID Display by ensuring thread titles extracted from PLANNER_RESPONSE or USER_INPUT fallback in the latest thread (leaf) are propagated to the frontend, rather than relying on the root thread's title which may be out-of-date or a UUID.

## Changes Made
- Modified `src-tauri/src/main.rs` to use `info.title` and `info.snippet` (from the latest thread leaf) instead of `root_info.title` and `root_info.snippet` (from the root thread) when constructing `ThreadLog` entries in `get_threads` and `get_all_agy_threads`. 

## What Worked
- Thread titles updated dynamically when the user issues new tasks or resumes threads, accurately reflecting the latest generated `<THREAD_NAME>` or fallback user prompt.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- The application groups AI threads by `root_id` to maintain conversation lineages. However, the title of the conversation group should reflect the most recent state/intent of the conversation, which is stored in the `latest_leaf_id` (represented by `info` in `get_threads`). Using `root_info` causes the UI to freeze the thread title to whatever it was at initialization.
