# Development Journal

## 2026-09-27

- Migrated the MCP bridge from the removed v1 `FastMCP` import to MCP 2's `MCPServer` API and bounded the dependency at `<3` to prevent the next breaking-major upgrade.
- Added regression coverage for the dependency contract and MCP 2 schema/result naming, then verified a fresh Codex client called `agy_doctor` successfully.

## 2026-09-24

- Made noninteractive `agy-bridge` requests enable agy's permission approval by default, with an explicit opt-out.
- Added a failure envelope for zero-exit runs that produce no assistant response, preventing silent false successes.
