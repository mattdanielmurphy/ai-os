## Goal
Install and isolate-test the `agy-mcp` server, and create a documentation file explaining the available commands for the MCP server.

## Changes Made
- Installed `agy-mcp` and `mcp-cli` using `uv`.
- Ran `agy-doctor` successfully.
- Verified interactive MCP tool execution using `mcp-cli`.
- Created `docs/agy-mcp-commands.md` in `ai-os` outlining the tools provided by the `agy-mcp` server.

## What Worked
- Installation via `uv tool install` worked perfectly.
- Background and interactive execution of the MCP server tools returned valid JSON and correctly parsed commands.
- `mcp-cli` `/execute` command successfully passed inputs.

## What Didn't Work / Known Issues
- Initial confusion with `mcp-cli`'s command-line flags. Discovered that tools need to be executed via `/execute` inside the interactive shell or properly formatted in non-interactive `cmd` mode.

## Architecture Notes
- The `agy-mcp` server exposes 11 tools providing deep integration with the Antigravity CLI, allowing both synchronous and asynchronous session management, log polling, and skill installation directly through the MCP protocol.
