## Goal
Migrate the agent logs directory from a hidden `.agent-logs/` directory to a non-hidden `agent-logs/` directory, update all configuration/codebase references, and define instructions for appending and loading conversation transcript pointers in logs.

## User Feedback & Decisions
- Moved log files to `agent-logs/`.
- Included pointer to full transcript (`transcript.jsonl`).

## Changes Made
- Renamed `.agent-logs` to `agent-logs` in project root using `git mv`.
- Updated log directories in `.agents/AGENTS.md`, `legacy-tauri-gui/src/systemPromptConfig.ts`, `legacy-tauri-gui/src-tauri/src/main.rs`, `scripts/context_handoff.py`, `scripts/ingest_codebase`, `scripts/generate_repo_map.py`, `AG_CONTEXT.md`, and `docs/AG_CONTEXT.md`.
- Added logic in `context_handoff.py` to parse `ANTIGRAVITY_SOURCE_METADATA` and find the matching `transcript.jsonl` path for the current conversation.
- Added instructions on how newly initialized agents in fresh threads should find and load transcripts.

## What Worked
- Renaming the directory successfully moved all historical engineering logs.
- `cargo check` verified that the Rust backend compiles cleanly.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The thread UUID is obtained from the `ANTIGRAVITY_SOURCE_METADATA` environment variable, specifically by decoding the JSON and reading `metadata["tool"]["conversationId"]`.

To see the full transcript for this: /Users/matt/.gemini/antigravity-ide/brain/fe8ea1a9-dd8f-46a0-bd59-44d3dfb84a32/.system_generated/logs/transcript.jsonl
