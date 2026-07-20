## Goal
Implement the Zero-Fork Hermes Triage Interceptor to automatically route coding tasks to `agy` without breaking Hermes memory state. Also clarify and fix tool name documentation discrepancies.

## User Feedback & Decisions
The user explicitly asked to verify tool names and remove the ugly hypothetical `mcp__agy_mcp__agy_start_tool` and to implement the interceptor.

## Changes Made
- Fixed `AG_CONTEXT.md` and `FEATURES.md` to reference the correct tools `agy`, `agy_continue`, and `agy_start`.
- Created `/Users/matt/projects/ai-os/scripts/aios_hermes_wrapper.py` which monkey-patches `chat_completion_helpers`.
- Updated `/Users/matt/Library/LaunchAgents/com.matt.agent.hermes-gateway.plist` to run the wrapper.
- Reloaded the LaunchAgent.

## What Worked
- Python monkey patching wrapper script works by injecting the synthetic `agy_start` function call in response to triaged prompts.
- LaunchAgent loaded correctly.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The Zero-Fork Interceptor sits in `aios_hermes_wrapper.py` and proxies the main function of `hermes_cli.main`. 

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/3c54bf55-19ba-4ba4-9b57-5988a618eb5e/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/3c54bf55-19ba-4ba4-9b57-5988a618eb5e/.system_generated/logs/transcript.jsonl)
