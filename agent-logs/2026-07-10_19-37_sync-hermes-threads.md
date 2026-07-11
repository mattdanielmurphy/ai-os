## Goal
Support automatically synchronizing Hermes threads into the antigravity-cli thread history so the user can continue conversations started with the Hermes agent.

## Changes Made
- Created [sync_threads.py](file:///Users/matt/projects/ai-os/scripts/sync_threads.py) which reads `~/.hermes/state.db` and maps messages to `~/.gemini/antigravity-cli/brain/` conversation transcripts in NDJSON format.
- Modified [bin/ai-os](file:///Users/matt/projects/ai-os/bin/ai-os) to run the sync script in oneshot mode at startup and watch mode in the background.
- Updated [FEATURES.md](file:///Users/matt/projects/ai-os/FEATURES.md) and [AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md).
- Created task file [.devtool/features/sync-hermes-threads.md](file:///Users/matt/projects/ai-os/.devtool/features/sync-hermes-threads.md) and set to `review`.

## What Worked
- Thread synchronization successfully imports and updates Hermes conversations.
- Oneshot and background watch modes operate efficiently.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Thread IDs under `~/.gemini/antigravity-cli/brain/` do not require standard UUID formats.
- The UI builds the compact history via `USER_INPUT` (source: `USER_EXPLICIT`) and `PLANNER_RESPONSE` (source: `MODEL`) lines in `transcript.jsonl`.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/99fdc596-e56e-4d8f-9a6e-d79b8c26d64a/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/99fdc596-e56e-4d8f-9a6e-d79b8c26d64a/.system_generated/logs/transcript.jsonl)
