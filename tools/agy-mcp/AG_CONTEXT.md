# Repository Context

- `agy-mcp` bridges the local `agy`/Gemini CLIs to MCP and a JSON CLI wrapper.
- Preserve the bridge's structured event and redaction behavior when changing invocation defaults.
- Validate both direct bridge envelopes and MCP-facing behavior for execution-path changes.
- The bridge uses MCP 2's `MCPServer` API and pins `mcp[cli]` to `>=2.0,<3`; do not reintroduce the removed v1 `FastMCP` import path.
- Codex launches the globally configured `agymcp` process when a task begins; a task whose bridge crashed at startup cannot gain its tool list dynamically, but later tasks load the repaired bridge automatically.
- Agy runs unsandboxed with write access and permission auto-approval for every invocation. Restrictive caller flags are ignored so execution mode cannot fail solely for missing write authorization.
- This source lives in AI-OS at `tools/agy-mcp`; reinstall the global `uv` tool from this path and never push bridge changes to the imported upstream repository.
