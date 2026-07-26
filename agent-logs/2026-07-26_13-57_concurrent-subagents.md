## Goal
Update subagent.py to support multiple concurrent subagents via tmux split-window and pane management.

## User Feedback & Decisions
- User requested support for running multiple subagents concurrently rather than sequentially.

## Changes Made
- Modified `_kill_pane` and `_respawn` to take `pane_id`.
- Added `_allocate_pane()` to find or create a free pane in the subagents session.
- Added `_cleanup_pane(pane_id)` to mark panes free and kill them if they aren't the last pane.
- Wrapped `run_in_tmux` loop in `try/finally` to ensure cleanup.

## What Worked
- Successfully implemented pane pooling and cleanup. Verified with git diff.

## What Didn't Work
- NA.

## Architecture Notes
- Tmux `@busy` options are used to track pane state.