---
name: hermes-mcp-servers
description: "When adding, testing, or fixing MCP servers in Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, mcp, mcp-servers, toolset, reload, launch-agent, webui]
    related_skills: [hermes-agent, hermes-provider-setup, la-launch-agent-manager, macos-service-migration]
    category: software-development
---

# Hermes MCP Servers

Connecting and troubleshooting external MCP servers whose tools Hermes exposes to the agent as `mcp_<server>_<tool>` (e.g. `mcp__proxima__ask_gemini`).

## When to use

Use when the user asks to:
- Wire up an MCP server (n8n, Proxima, filesystem, github, custom project).
- Figure out why MCP tools are missing from a session/WebUI chat.
- Make an MCP server a managed launch agent.
- Test whether a configured server actually connects.

## Config location

MCP servers live in `~/.hermes/config.yaml` under `mcp_servers` (NOT `mcp` or `servers`):

```yaml
mcp_servers:
  my_server:
    command: node                 # or /absolute/path/to/node
    args: ["/abs/path/to/server.js"]
    tools:                        # optional allowlist
      include: [tool_a, tool_b]
    enabled: true
```

Use `hermes config set mcp_servers.<name>.command "<abs path>"` for edits — do NOT hand-edit config.yaml (memory rule). Verify the result after any `hermes config set`; list-valued writes can mangle into a quoted string.

## Diagnose "MCP tools not showing up" — do this in order

1. **Is it configured + enabled?** `hermes mcp list` — shows each server, transport, tool count, and ✓/✗ enabled state.
2. **Does it actually connect?** `hermes mcp test <name>` — prints `✓ Connected (Nms)` and `✓ Tools discovered: N`. This is the fastest proof the server is healthy.
3. **Did the agent register the tools?** Grep the logs:
   ```bash
   grep -i "MCP server '<name>'" ~/.hermes/logs/agent.log | tail
   ```
   A line like `registered 38 tool(s): mcp__proxima__ask_gemini, ...` means the agent process HAS the tools — the problem is purely session/snapshot, not the server.
4. **THE key crate of confusion: MCP toolset is FROZEN at agent-process boot.** Page refresh is NOT a reload. If the server is healthy but tools still aren't callable, the running agent process imported its toolset before the config was active. Fix = restart the process that owns the session, then start a **NEW** session:
   - WebUI (in-process agent): restart the supervising launch agent, not the browser.
   - Config/provider changes: `/reset` (new session) or quit & relaunch Hermes.
5. **If a restart + new session STILL doesn't load the tools — check toolset RESOLUTION, not the server.** The server can be perfectly healthy and enabled, and the process freshly booted, yet the tools are silently dropped at toolset-resolution time. This is the deepest cause and the one most often missed. Diagnose it with:
   ```bash
   cd ~/projects/external/hermes-webui && \
   /Users/matt/projects/hermes-agent/venv/bin/python -c "
   import os, yaml
   os.environ.setdefault('HERMES_HOME', '/Users/matt/.hermes')
   from api.config import CLI_TOOLSETS
   print('CLI_TOOLSETS:', CLI_TOOLSETS)
   print('has <server>:', '<server>' in CLI_TOOLSETS)"
   ```
   If `<server>` is absent from `CLI_TOOLSETS` while another MCP server is present, you've hit the **allowlist bug** (below) — a restart alone will never fix it. See `references/toolsets-resolution.md`.

Behavior differs by surface — see `references/webui-reload.md` for the exact launch-agent restart commands.

## Two MCP server shapes — pick the right one

- **Stdio-only server** (e.g. Proxima, most local MCPs: uses `StdioServerTransport`): designed to be SPAWNED as a child by an MCP client (Hermes). Hermes launches it via its own `mcp_stdio_watchdog.py`. A standalone `launchctl` agent wrapped around it just sits idle on stdin with no client — often redundant. Only add a launch agent if you specifically want it alive/visible/loggable as a service.
- **HTTP/StreamableHTTP server**: configured with `url:` + `headers:` instead of `command`. Good candidate for a launch agent that self-hosts a port.

## Pitfalls

- **`command` must resolve in the launchd/MCP environment.** A bare `node` worked interactively but produced `FileNotFoundError: no such file or directory: '.../node_modules/.bin/node'` under Hermes' filtered env. Fix: point `command` at an absolute node binary (e.g. `/Users/matt/.local/bin/node` — the Hermes-managed node), and `args[0]` at the absolute server path.
- **MCP stdio children inherit a FILTERED env** (PATH/HOME/USER/LANG/TERM/etc. plus anything in `env:`). API keys are excluded unless added under `env:`. A server that needs a key must get it there.
- **`tools.include` is an allowlist** — if a tool you expect is missing, first check it's on the allowlist in config, then that the server advertises that exact name.
- **The `platform_toolsets.cli` ALLOWLIST BUG (silent tool disappearance).** MCP servers are injected via `_get_platform_tools(cfg, "cli")` in `hermes_cli/tools_config.py`. If `platform_toolsets.cli` explicitly lists ANY MCP server name (e.g. `agymcp`), the resolver flips into **allowlist mode** — it detects `explicit_mcp_servers` is non-empty and ONLY injects the explicitly-listed servers, silently dropping every other *globally-enabled* server. So a healthy, enabled, freshly-restarted server with `registered N tool(s)` in the log can still be absent from sessions because its name isn't in that list. **Fix:** add the server's name to `platform_toolsets.cli` (it resolves once at process import → must restart + new session after). This looked like a "restart didn't work" case but was actually never a restart problem.
- **`hermes config set platform_toolsets.cli '[...json...]'` writes the list as a JSON STRING, not a YAML list** — `cli` becomes `'"["agymcp",...]"'`, which breaks toolset iteration (a single str instead of a list). Fix with a `yaml.safe_load` → append → `yaml.safe_dump` round-trip (sort_keys=False) so it stays a real list. Verify: `hermes mcp list` still shows all servers, and `_get_platform_tools(cfg,'cli')` returns the names.
- **Logs are your friend**: `~/.hermes/logs/agent.log` (registration), `~/.hermes/logs/mcp-stderr.log` (server stderr). A `parked until a reconnect is requested ... McpError: Connection closed` line means the first connect failed and it's waiting — restart the server/session to re-trigger.
- When run inside the WebUI, restarting the webui backend kills the in-progress conversation. Hand the user the restart command rather than running it yourself mid-turn.

## References

- `references/webui-reload.md` — how the WebUI hosts the agent in-process, and the exact command to reload its toolset (the thing page-refresh can't do).
- `references/toolsets-resolution.md` — the `platform_toolsets.cli` allowlist bug: the exact resolver code, the CLI_TOOLSETS probe, and the fix + verification (root cause of "healthy server, tools still missing after restart").
- `references/proxima-session.md` — the Proxima MCP work: config, wrapper, launch agent for a stdio server.
