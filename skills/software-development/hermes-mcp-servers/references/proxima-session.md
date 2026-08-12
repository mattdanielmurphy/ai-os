# Proxima MCP server — wiring notes

Session-recap of making Proxima's MCP server available to Hermes (2026-08).

## What Proxima is

- An Electron agent hub at `~/projects/external/Proxima`.
- Its MCP server is a **stdio** server: `node ~/projects/external/Proxima/src/mcp/index.js`
  (uses `StdioServerTransport` from `@modelcontextprotocol/sdk`). It does not self-host
  a port; an MCP client must spawn it over stdin/stdout.

## Facts verified

- `hermes mcp list` → `proxima ... 36 selected  ✓ enabled`
- `hermes mcp test proxima` → `✓ Connected (512ms)`, `✓ Tools discovered: 40`
  (ask_gemini, ask_chatgpt, ask_claude, smart_query, review_code, analyze_file, ...)
- `agent.log` shows `MCP server 'proxima' (stdio): registered 38 tool(s): mcp__proxima__ask_gemini, ...`
- The WebUI server (`server.py`) spawns it as a child via `mcp_stdio_watchdog.py` — so a
  healthy webui process already holds the Proxima connection.

## The config fix

Original config used a bare `command: node`, which under Hermes' filtered launchd env
produced `FileNotFoundError: no such file or directory: '.../node_modules/.bin/node'`.
Fixed with:

```bash
hermes config set mcp_servers.proxima.command "/Users/matt/.local/bin/node"
```

(that `node` is a symlink to Hermes' managed node, resolves to v22).

## Launch agent for a stdio MCP server

Since Hermes already spawns Proxima as a stdio child, a standalone launch agent is
optional/redundant for loading tools — but is useful to keep the server alive, visible
via `la`, and loggable. Matt asked for one, so it was added:

- Wrapper: `/Users/matt/projects/external/Proxima/run_proxima_mcp.sh`
  (resolves node from PATH, `exec`s `node index.js` in the foreground).
- Plist: `~/Library/LaunchAgents/com.matt.agent.proxima-mcp.plist`
  - `com.matt.agent.proxima-mcp` label, `keepalive --no-watch` via
    `~/Library/Scripts/tmux-agent-wrapper.sh`
  - tmux session `agent-proxima-mcp`
  - logs: `~/Library/Logs/launch-agents/proxima-mcp.log`
- Verified: `la status proxima-mcp` → running, tmux alive, `LastExitStatus 0`.

## The one thing that actually fixed the "tools not loading" complaint

Not the launch agent — it was that the **WebUI backend process** needed restarting to
pick up the freshly-enabled MCP config. See `references/webui-reload.md` for the reload
rule. The takeaway for future me: do the `hermes mcp test` / `agent.log` / restart
diagnosis first, before adding any launch-agent scaffolding.