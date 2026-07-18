## Goal
Modify the local MCP server (`agy-mcp`) to extract Hermes Agent's live system prompt from `~/.hermes/state.db` and prepend it to prompts sent to `agy` to align instructions and preserve behavioral consistency during handoffs.

## User Feedback & Decisions
- Decided to retrieve the system prompt directly from the active Hermes session SQLite database `~/.hermes/state.db` rather than importing python files, which is faster and has zero runtime dependencies.
- Confirmed that prepending the system instructions to the prompt using clear `[HERMES_SYSTEM_PROMPT]` and `[USER_PROMPT]` tags works perfectly.

## Changes Made
- Modified [server.py](file:///Users/matt/.local/share/uv/tools/agy-mcp/lib/python3.14/site-packages/agy_mcp/server.py) in the `agy-mcp` package:
  - Added `_get_hermes_system_prompt` helper function to extract system prompts.
  - Added `include_hermes_prompt` parameter to `agy_tool`, `agy_continue_tool`, and `agy_start_tool`.
  - Prepended prompt when enabled.
- Updated [FEATURES.md](file:///Users/matt/projects/ai-os/FEATURES.md) to record the new capability.
- Updated [AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md) to document the system prompt handoff.
- Transitioned [hermes-agy-system-prompt-handoff.md](file:///Users/matt/projects/ai-os/.devtool/features/hermes-agy-system-prompt-handoff.md) to `status: review`.

## What Worked
- Successfully extracted and prepended the dynamic system prompt (identity + memory states) from `state.db`.
- Verified command-preview generation via dry run with `debug=True`.
- Restarted launch agent/tmux and verified tool calls run properly.

## What Didn't Work / Known Issues
- `mcp-cli` encountered a known internal `httpx.InvalidURL` error during manual CLI testing, but verifying via direct Python package invocation and dry run proved everything works perfectly.

## Architecture Notes
- The SQLite table `sessions` in `~/.hermes/state.db` contains a `system_prompt` column containing the fully rendered system prompt for each active native session. We match by CWD or fallback to the absolute latest session to fetch it.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/7b48034f-e26a-4719-902c-a126b962156f/.system_generated/logs/transcript.jsonl)