## Goal
Document the architectural decisions and create a handoff file for the Zero-Fork Hermes Triage Interceptor. The user wanted to prioritize `agy` execution using the Gemini quota pool for triage tasks without burning tokens on Hermes' native models, while still retaining Hermes' memory capabilities.

## User Feedback & Decisions
- The user clarified that they want to prioritize `agy` for all coding tasks, throttling to Gemini 3.1 Pro Low if the quota dips below 20%.
- We explored directly modifying `triage_proxy.py` to spoof WebUI WebSocket messages, but realized this blinds Hermes to the interaction (no memory, no state).
- The user approved Option 3: a "Zero-Fork Wrapper" that monkey-patches Hermes Agent in memory to intercept the `chat_completion_request`, run the cheap Tier 1 triage, and synthetically return an MCP tool call to `agy`.
- The user decided to implement this in a fresh thread due to the current thread's length.

## Changes Made
- Created `hermes-triage-interceptor.md` in `.devtool/features/` documenting the architecture, launch agent discovery, and implementation steps for the next thread.
- Discovered that Hermes is launched via `~/Library/LaunchAgents/com.matt.agent.hermes-gateway.plist`.

## What Worked
- Successfully mapped out a highly effective architectural solution that avoids merge conflicts with the upstream Hermes repo.
- Created the handoff file per the user's instructions.

## What Didn't Work / Known Issues
- Initial plan to just use `triage_proxy.py` on port 9119 was flawed because it bypassed the Hermes agent state entirely.

## Architecture Notes
- Hermes is launched via a launchd plist that calls a `tmux-agent-wrapper.sh` script, which then executes `-m hermes_cli.main gateway run --replace`.
- We can intercept this by swapping the `-m` module target to our own `aios_hermes_wrapper.py` script.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/34a33f30-4176-4ddb-bc83-0b4aede61d63/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/34a33f30-4176-4ddb-bc83-0b4aede61d63/.system_generated/logs/transcript.jsonl)
