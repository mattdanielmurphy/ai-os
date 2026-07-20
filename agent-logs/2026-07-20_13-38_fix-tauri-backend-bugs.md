## Goal
Fix remaining reliability issues in Tauri backend:
1. WebSocket relay host reconnect race condition in `server.rs`.
2. Thread naming, chain resolution, and project path association in `threads.rs`.
3. Terminal output tab switching/interleaving race conditions.

## User Feedback & Decisions
- The user requested to continue the pending task.
- Moved task to `review` status on completion.

## Changes Made
- **`server.rs`**: Modified `WsState` to track active host connections using unique connection IDs (`conn_id`). During socket registration, the active connection ID is stored. In socket cleanup, the host channel is only cleared if the dying socket matches the stored connection ID, resolving the host reconnect race condition.
- **`threads.rs`**:
  - Increased buffer size in `get_child_to_parent_map` to `65536` to avoid truncating long step entries when searching for the parent UUID.
  - Added `is_uuid` and `resolve_thread_metadata` helpers to walk up the parent-child thread chain to find the most accurate user-friendly title and project path.
  - Updated `get_project_threads` and `get_all_agy_threads` to resolve metadata dynamically, ensuring continuation threads do not display default UUID titles or fall into "Misc" due to lack of local project paths.
- **`types.rs`**: Added `thread_id` field to the PTY output `Payload` struct.
- **`pty.rs`**: Propagated the active `thread_id` inside the PTY reader loop output events.
- **`main.ts`**:
  - Isolated cached terminal buffers by keying on `${project_path}_${thread_id}` instead of just the project path.
  - Conditioned terminal writes so output is only printed to xterm if the event's `thread_id` matches the global `activeThreadId`.
  - Updated project/engine switching routines to restore terminal history correctly using the new keys.

## What Worked
- Clean backend compile (`cargo check`) and frontend build (`bun run build`).
- Corrected race condition in tab switching: terminal outputs no longer interleave when multiple project threads are running.
- Corrected thread grouping: child threads now correctly inherit parent project paths and titles.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Thread properties like titles and projects are now resolved along the entire tree path from child to root, making metadata extraction highly resilient.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/a978bc24-593d-4cc8-827f-763828bc4450/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/a978bc24-593d-4cc8-827f-763828bc4450/.system_generated/logs/transcript.jsonl)
