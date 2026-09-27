# Agy MCP monorepo integration and full permissions

- Imported the maintained bridge into `tools/agy-mcp` under its MIT provenance; the AI-OS remote is `https://github.com/mattdanielmurphy/ai-os.git`, and no upstream push was attempted.
- Migrated the bridge to the MCP v2 Python SDK and installed the global bridge as an editable install from the monorepo path.
- Made execution unconditional: restrictive or missing caller permission flags are compatibility inputs only; bridge requests remain write-enabled, unsandboxed, and noninteractive. Destructive-operation and sensitive-read guards remain enforced.
- Verification: `uv run pytest` reported 565 passing tests, Ruff and the release-artifact audit passed, a dry-run execute request omitted `allow_write` successfully, and a fresh Codex MCP request returned `AGY_FULL_PERMISSIONS_OK`.
