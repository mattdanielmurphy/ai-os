## Goal
Add an action bar/search bar triggered by cmd-k to quickly search active AI-OS threads. The search needs to prioritize titles, factor in the user prompts (specifically what the user actually wrote, omitting system instructions) and the agent responses, and then show the results for the current project.

## Changes Made
- Added `search_project_threads` to `src-tauri/src/main.rs`. This Tauri command gets all the project threads, then reads their corresponding `transcript.jsonl` files from the agy `.gemini` brain directory to extract `<USER_REQUEST>` blocks and model responses.
- Implemented a custom scoring system in Rust to prioritize title matches, then user requests, and then model/planner responses, generating a preview for the UI.
- Implemented an `ActionBar` UI component in `src/ActionBar/ActionBar.ts` and `src/ActionBar/ActionBar.module.css` following project requirements (dedicated directory, vanilla CSS modules).
- Wired up the `ActionBar` initialization in `src/main.ts`, which responds to `Cmd-K` and renders the search modal. Clicking a thread successfully routes the user to that thread and resumes it via `/resume`.
- Addressed `ThreadLog` missing `Clone` trait to support returning it nested in `ThreadSearchResult`.

## What Worked
- Directly parsing the `transcript.jsonl` and searching the JSON payload content allows extremely fast offline searches of agent logs without heavy indexing.
- Extracting the contents of the `<USER_REQUEST>` tag cleanly bypasses system instructions and hidden context matching.

## What Didn't Work / Known Issues
- Currently loads all transcripts for a project synchronously upon search in Rust. This is very fast given local SSD speeds and small project scoped sizes, but if a single project accumulates tens of thousands of threads it might stutter.
- No fuzzy searching, relying on basic case-insensitive exact substring matches.

## Architecture Notes
- ai-os "threads" are actually standard `agy` threads stored in `.gemini/antigravity-cli/brain/`. The connection to an ai-os project is purely maintained by analyzing the `project_path` string embedded dynamically into the transcript logs during runtime.
- `latest_leaf_id` is the actual file we resume or search to get the most recent conversation transcript state, while `id` (the root id) identifies the logical thread timeline grouping.
