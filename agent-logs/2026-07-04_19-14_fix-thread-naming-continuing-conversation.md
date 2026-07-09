## Goal
Prevent `agy` from picking "Continuing conversation from history" as a thread name.

## Changes Made
- Modified `src/systemPromptConfig.ts` to add explicit instructions in the `<THREAD_NAMING>` blocks for both Worker Bee and Triage Mode rules. The prompt now strictly forbids using generic phrases like "Continuing conversation from history" and asks the agent to focus on the ACTUAL user request.

## What Worked
- Updated the system prompt configuration.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `<THREAD_NAME>` extraction logic in `src-tauri/src/main.rs` relies on the agent emitting `<THREAD_NAME>...` properly, which is driven by `src/systemPromptConfig.ts`.
