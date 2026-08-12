# Reloading the Hermes WebUI backend (to pick up MCP tools)

## Why page-refresh is never enough

The WebUI (`~/projects/external/hermes-webui`) runs the agent **in-process**:
`server.py` imports `run_agent.AIAgent` into its long-lived Python process. MCP tool
discovery + toolset injection happen at agent/session initialization, so a browser
refresh only reloads the frontend — the backend process keeps its already-imported
toolset. Adding/editing an MCP server therefore requires **restarting the backend
process**, then starting a **NEW** chat (old sessions keep their stale snapshot).

Surfaces: the WebUI can run as (a) the `com.parantoux.hermes-webui` launch agent, or
(b) a `./ctl.sh` daemon. Restart the one that's actually supervising, or you'll spawn
a second, competing instance.

## The reload commands

```bash
# If launched via the com.parantoux.hermes-webui launch agent (Matt's setup uses this):
la restart hermes-webui        # or: launchctl kickstart -k gui/$(id -u)/com.parantoux.hermes-webui

# If launched as a ctl.sh daemon:
cd ~/projects/external/hermes-webui && ./ctl.sh restart
```

Then open a fresh chat in the browser.

## Confirm the current supervisor before restarting

```bash
./ctl.sh status            # in ~/projects/external/hermes-webui
la status hermes-webui
```
`ctl.sh status` prints `running (NOT managed by ctl.sh)` when the launch agent owns it,
or shows the ctl pid when it's a ctl daemon. Match the restart command to that.

## CRITICAL: restarting the webui kills the in-progress conversation

`server.py` runs the very session doing the work. If an agent restarts the webui
mid-turn, its own reply is cut off. When you're being asked inside the WebUI to "restart
webui", hand the user the one-liner to run themselves rather than executing it — the
browser reconnects to a fresh server and new sessions pick up the new toolset.

## Verification after reload

- `grep -i "MCP server '<name>'" ~/.hermes/logs/agent.log | tail` → expect a
  `registered N tool(s): mcp__<name>__...` line timestamped after the restart.
- In a NEW chat, the tools appear as `mcp__<name>__<tool>`.
- `hermes mcp test <name>` re-proves the server itself still connects.
