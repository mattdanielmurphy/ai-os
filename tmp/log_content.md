## Goal
Fix PTY resize errors that complain "No PTY session found for project: ..." when active threads are selected.

## User Feedback & Decisions
- Pass `threadId: activeThreadId || ""` in the resize RPC arguments from both terminal wrappers so the backend can correctly locate the active PTY thread session key.

## Changes Made
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Updated `term.onResize` to pass `threadId: activeThreadId || ""` in `resize_pty`.
  - Updated `miniTerm.onResize` to pass `threadId: activeThreadId || ""` in `resize_pty`.

## What Worked
- Rebuild via `bun run build` completed successfully.
- Terminals resize cleanly without triggering PTY lookup failures.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The backend matches PTY sessions using `session_key` format (`{project_path}_{thread_id}`). Omitting `threadId` in the frontend `resize_pty` call causes the key search to default to the empty thread ID placeholder (`{project_path}_`), causing lookups to fail for any running thread sessions.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/066be666-bc5b-4bce-a3bd-5bb7b36e4cb5/.system_generated/logs/transcript.jsonl)
