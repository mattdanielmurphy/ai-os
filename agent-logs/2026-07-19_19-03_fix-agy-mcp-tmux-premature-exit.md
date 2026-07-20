## Goal
Investigate and fix an issue where `agy` stops prematurely when invoked via the `agy-mcp` tool. Also, add debugging information to help diagnose any future crashes.

## User Feedback & Decisions
The user noted that `agy` stops prematurely during Hermes triage routing when used via MCP. They requested lots of debugging information to be added.

## Changes Made
- Modified `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py`.
- Changed the `agy` command inside the `tmux` session to use `--prompt-interactive` instead of `--print`. `--print` causes `agy` to exit immediately after generating its response, tearing down the tmux session prematurely before Hermes can interact with it. `--prompt-interactive` ensures the session remains open, awaiting further input.
- Stripped `--print-timeout` arguments which are invalid for interactive mode.
- Wrapped the tmux bash command with a failure handler (`|| { echo 'Agy crashed or stopped prematurely! Exit code: $?'; sleep 86400; }`). This ensures that if `agy` fails, the tmux pane stays alive for a day so the stack trace/error logs can be inspected rather than instantly disappearing.
- Restarted the `agy-mcp` daemon to apply the changes.

## What Worked
- The `agy` tool in `agy-mcp` now correctly spawns an interactive `agy` session inside `tmux`.
- Tmux panes are now resilient to crashes and will remain open on failure for debugging.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The `agy_start_tool` runs daemon threads via the Supervisor, which already has excellent logging (`stdout.spool`, `stderr.spool`, and crash handlers). The premature exit issue was specific to the newly introduced `tmux` handling in `agy_tool` and `agy_continue_tool` which were accidentally wrapping a one-shot `--print` command.
- The Hermes Triage Interceptor delegates coding tasks using `agy_start`, but `agy_tool` and `agy_continue_tool` are what rely on tmux for persistence.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/b54ef527-d9ff-4b75-8b80-aa5e37672d5a/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/b54ef527-d9ff-4b75-8b80-aa5e37672d5a/.system_generated/logs/transcript.jsonl)
