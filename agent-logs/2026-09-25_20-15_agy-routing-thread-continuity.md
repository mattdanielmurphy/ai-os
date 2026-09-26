# Agy Flash High Routing and Thread Continuity

## Changes

- Made `gemini-3.8-flash-high` the required model for non-trivial `agy` work while quota is available.
- Required `SESSION_ID` retention per ChatGPT/Codex thread and `agy_continue` for later non-trivial turns.
- Updated planner fallback wording and regenerated shared agent instruction files.

## Verification

- `agy models` listed `gemini-3.8-flash-high`.
- `uv run pytest tests/test_mcp_server.py -k 'agy_continue'` passed: 2 tests.
- Reinstalled `agy-mcp` from its tracked source as an editable `uv` tool.

## Runtime Note

- The MCP process already attached to this Codex task retains an older bridge and still rejects `agy_continue`; new tasks launch the reinstalled bridge.
