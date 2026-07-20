## Goal
Investigate and fix why the hermes agent (via agy-mcp) stops prematurely before completing its job when dispatched to triage.

## User Feedback & Decisions
User explicitly stated: "It's not that it would complete the job and then stop; it would stop BEFORE completing the job!"

## Changes Made
- `agy_mcp/models.py`: Added `dangerously_skip_permissions: bool = False` to `BridgeRequest`.
- `agy_mcp/adapters/agy.py`: Threaded `request.dangerously_skip_permissions` down to the `agy` CLI via the `--dangerously-skip-permissions` flag when building the headless command.
- `agy_mcp/server.py`: Updated `agy_start_tool`, `agy_continue_tool`, and `agy_tool` to inject `dangerously_skip_permissions=True` into their `_build_request` calls.

## What Worked
The missing `dangerously_skip_permissions` flag was successfully threaded. A local script confirmed that `agy_start_tool` now successfully runs bash commands without aborting prematurely on interactive confirmation blocks in headless mode. 

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `agy --print` mode (headless) aggressively aborts if a tool request is made without the skip-permissions flag or an explicit `settings.json` allowlist. Since `agy_mcp` delegates triage jobs via `agy_start_tool`, which is completely headless, it MUST supply this flag so the subagent can execute commands autonomously.
[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/b54ef527-d9ff-4b75-8b80-aa5e37672d5a/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/b54ef527-d9ff-4b75-8b80-aa5e37672d5a/.system_generated/logs/transcript.jsonl)
