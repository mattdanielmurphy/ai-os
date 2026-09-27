# MCP 2 Bridge Migration

## Cause

`agymcp` could no longer start because a fresh tool installation resolved MCP 2.x while the bridge imported the removed v1 `mcp.server.fastmcp.FastMCP` API. Codex therefore received no Agy tools when the task started.

## Change

- Replaced `FastMCP` with MCP 2's `MCPServer` import and constructor.
- Set the package requirement to `mcp[cli]>=2.0,<3` and refreshed `uv.lock`.
- Updated MCP 2's snake_case model-field assertions in the server test suite.
- Added a dependency-contract regression test and refreshed documentation terminology.

## Verification

- `uv run pytest` — 564 passed.
- `uv run ruff check .` — passed.
- `uv build` and `uv run scripts/check_release_artifacts.py` — passed.
- Reinstalled the editable `agy-mcp` tool, then used a fresh Codex client to call `agymcp/agy_doctor`; it succeeded and detected `agy` 1.2.12.
