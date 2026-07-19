## Goal
Fix reliability bug in `agy` MCP server where crashed worker threads lose logs and tool events.

## User Feedback & Decisions
The user specified four key priorities for the reliability fixes:
1. Don't use a temp spool dir for outputs; write directly to the session store.
2. Add a signal handler and atexit hook in `supervisor._run_job` to write diagnostic events with thread stack traces before the thread dies.
3. In `status()` reconcile path, try to capture any remaining spool files if the spool dir exists.
4. Add a `last_heartbeat` timestamp to `JobRecord` updated by the worker every 10 seconds to allow `status()` to distinguish "thread alive but stuck" from "thread is dead".
Additionally, enable tool event capture in `agy.py` (`supports_tool_events = True`).

## Changes Made
- `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/models.py`: Added `last_heartbeat` to `JobRecord`.
- `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/adapters/agy.py`: Set `cap.supports_tool_events = True`.
- `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/supervisor.py`:
  - `_run_job`: Modified spool log assignments to point directly to `paths.stdout`, `paths.stderr`, and `paths.agy_log`. Added `heartbeat_loop` running in a daemon thread. Added `dump_stacks` signal and atexit handler for crash diagnostics. Removed legacy `_migrate_if_present` calls from finally block.
  - `status`: Refactored to leverage `fresh.last_heartbeat`. It now accurately identifies stuck threads (alive but heartbeat >30s stale) vs dead threads, and captures leftover spool files (`stdout.spool`, `stderr.spool`, `agy.log`) if a worker crashed without finalizing.

## What Worked
All four user requirements implemented successfully. The server will now persist logs even on a hard crash, dump stacks on SIGTERM/SIGINT, distinguish dead from stuck threads, and capture tool events.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `last_heartbeat` addition provides robust detection for worker threads that hang during `adapter.run` without changing the `BaseAdapter` interface. Signal handlers in worker threads normally raise `ValueError`, which was explicitly suppressed as they will still attach if the worker is the main thread, or fallback safely to `atexit`.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/ce810782-e67b-43e0-b90c-304131b67e43/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/ce810782-e67b-43e0-b90c-304131b67e43/.system_generated/logs/transcript.jsonl)
