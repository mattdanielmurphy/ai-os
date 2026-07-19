## Goal
Fix the agy MCP server so that instead of running agy --print (synchronous mode), it starts agy inside a tmux session that Hermes can attach to later.

## User Feedback & Decisions
The user approved the implementation plan to modify `agy_tool` and `agy_continue_tool` in `agy_mcp/server.py` to bypass `_bridge_run` and directly spawn `tmux new-session`.

## Changes Made
- Modified `agy_tool` in `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py` to execute `tmux new-session`.
- Modified `agy_continue_tool` in the same file.

## What Worked
Successfully rewrote the synchronous block to use tmux natively, injecting `--dangerously-skip-permissions` and `--add-dir` where needed.

## What Didn't Work / Known Issues
Nothing noted; changes were implemented seamlessly.

## Architecture Notes
The `AgyPrintBackend` adapter is very helpful because `_agy_adapter.build_command` handles all environment argument construction safely, letting us just wrap its output in `tmux`.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/edfd150e-b9a5-42f6-bac1-4505e746a5a3/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/edfd150e-b9a5-42f6-bac1-4505e746a5a3/.system_generated/logs/transcript.jsonl)
