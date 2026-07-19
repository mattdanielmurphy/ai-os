## Goal
Resolve `agy` MCP tool confusion where sync calls returning `agent_messages: ""` were misinterpreted by other agents (like Hermes) as failures, leading to polling/redispatch loops. Add `dispatched=True` flag and ensure `job_id` is populated in sync mode.

## User Feedback & Decisions
- The user provided an autopsy of a "Double-Dispatch Fiasco" where the agent misread the synchronous output of the `agy` tool.
- The user instructed to add `dispatched: bool` to the sync return envelope.
- The user instructed to ensure `job_id` is returned from sync calls.
- The user asked to update the MCP tool description for the sync tool to clarify it's a "fire-and-forget" call.

## Changes Made
- Modified `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/models.py`: Added `dispatched: bool = False` to `BridgeResponse`, and added a Pydantic `Field` description to `agent_messages` explaining it streams to the chat UI.
- Modified `/Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py`: Updated `agy_tool` and `agy_continue_tool` return responses to include `dispatched=True` and `job_id=session_id`. Also updated both tools' docstrings to explicitly tell models "do not poll or re-dispatch."

## What Worked
- Directly modifying the global `uv tool` installation `site-packages`.

## What Didn't Work / Known Issues
- `uv` environment access threw some Sandbox `PermissionError` when trying to run `agymcp --help` to syntax check, but the actual file edits were fully permitted and succeeded.

## Architecture Notes
- `agy-mcp` is currently installed globally as a `uv tool`. Edits made here directly affect the running tool, though the daemon may need a restart to pick up the schema changes.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/8d0f2c27-2a03-4ad6-beae-84fac442c582/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/8d0f2c27-2a03-4ad6-beae-84fac442c582/.system_generated/logs/transcript.jsonl)
