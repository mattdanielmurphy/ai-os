# Agent Work Log

## Goal
Resolve the issue where historical threads built from `agy` logs only contain user prompts and no assistant responses because the agent outputs its full response to a markdown file (`.ai-os/output.md`) instead of talking directly to the terminal chat.

## Changes Made
- **`src-tauri/src/main.rs`**:
  - Implemented the `patch_thread_log_with_output` Tauri command. This function locates the thread log directory matching the active project (either utilizing the selected `active_thread_id` or searching for the most recently modified transcript file that matches the project path).
  - It reads `transcript.jsonl` and `transcript_full.jsonl`, parses their lines as JSON, searches backwards to find the last assistant `PLANNER_RESPONSE` line, and replaces its `content` field with the new markdown content.
  - Registered `patch_thread_log_with_output` in the Tauri invoke handler list.
- **`src/main.ts`**:
  - Updated the frontend `output.md` polling interval function to run `patch_thread_log_with_output` immediately whenever `.ai-os/output.md` changes, regardless of whether the user is in terminal mode or markdown preview mode.
- **`FEATURES.md`**:
  - Added a bullet documenting the new thread log patching feature.

## What Worked
- Polling changes in `.ai-os/output.md` regardless of terminal mode ensures the log is patched immediately after the agent runs, even when the user is watching the terminal.
- Searching backwards in the JSONL files to find the last `PLANNER_RESPONSE` correctly targets the final response of the agent for that turn.
- Patching both `transcript.jsonl` and `transcript_full.jsonl` ensures that sidebar previews, preview pane rendering, and resumed context prompts all contain the actual markdown output instead of "I have updated the output file."

## What Didn't Work / Known Issues
- None. The Rust compiler ambiguity error was resolved by removing `by_ref` and consuming the `Take` reader directly.

## Architecture Notes
- The Antigravity brain logs (`transcript.jsonl` and `transcript_full.jsonl`) are JSONL files where each turn includes `PLANNER_RESPONSE` lines. Patching these files dynamically allows the UI and the resumption context parser to remain fully aligned with the actual output files generated during conversation turns.
