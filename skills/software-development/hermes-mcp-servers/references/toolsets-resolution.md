# Why a healthy MCP server can still have zero callable tools (the `platform_toolsets.cli` allowlist bug)

Root cause of the most confusing MCP failure mode: the server connects, tests clean,
registers `N tools` in the agent log, the process is freshly restarted, and yet the tools
**still never appear** in a new session. In that situation the problem is never the server
and never the restart — it's the **toolset-resolution** step silently dropping the server.

## The trigger

`platform_toolsets.cli` in `~/.hermes/config.yaml` explicitly lists an MCP server name
(here `agymcp`). Per `_get_platform_tools(cfg, "cli")` in `hermes_cli/tools_config.py`:

```python
# If the platform explicitly lists one or more MCP server names, treat that
# as an allowlist. Otherwise include every globally enabled MCP server.
if "no_mcp" in toolset_names:
    explicit_mcp_servers = set()
    ...
else:
    explicit_mcp_servers = explicit_passthrough & enabled_mcp_servers
    enabled_toolsets.update(explicit_passthrough - enabled_mcp_servers)
if include_default_mcp_servers:
    if explicit_mcp_servers or "no_mcp" in toolset_names:
        enabled_toolsets.update(explicit_mcp_servers)   # ONLY explicitly-listed servers
    else:
        enabled_toolsets.update(enabled_mcp_servers)    # all globally-enabled servers
```

Because `agymcp` was an explicit member, `explicit_mcp_servers` was non-empty → the resolver
took the **first branch** and injected ONLY `{agymcp}`, silently dropping every other
globally-enabled server (`proxima`). `agymcp` worked; `proxima` was invisible despite being
enabled + healthy + registered.

## Detect it fast

Probe the webui's cached toolset constant (computed at process import):

```bash
cd ~/projects/external/hermes-webui && \
/Users/matt/projects/hermes-agent/venv/bin/python -c "
import os, yaml
os.environ.setdefault('HERMES_HOME', '/Users/matt/.hermes')
from api.config import CLI_TOOLSETS
print('CLI_TOOLSETS:', CLI_TOOLSETS)
print('has proxima:', 'proxima' in CLI_TOOLSETS)
print('has agymcp:', 'agymcp' in CLI_TOOLSETS)"
```

Here `agymcp` present and `proxima` absent = allowlist bug confirmed.

## The fix

Add the missing server name to `platform_toolsets.cli`. Because the plain
`hermes config set platform_toolsets.cli '<json list>'` writes a **JSON string** (not a YAML
list — it becomes `'"["agymcp",...]"'`), the reliable edit is a yaml round-trip that appends
the name while keeping the value a real list:

```python
import os, yaml, json
p = os.path.expanduser('~/.hermes/config.yaml')
cfg = yaml.safe_load(open(p))
cli = cfg['platform_toolsets']['cli']
if isinstance(cli, str):
    cli = json.loads(cli)                 # undo the mangled string form
if 'proxima' not in cli:
    cli = cli + ['proxima']
cfg['platform_toolsets']['cli'] = cli
with open(p, 'w') as f:
    yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
```

## Verify before restarting

```bash
# 1. On-disk shape is a LIST (not a quoted string):
sed -n '/^platform_toolsets:/,/^[a-z]/p' ~/.hermes/config.yaml

# 2. Resolution now includes the server:
cd ~/projects/external/hermes-webui && /Users/matt/projects/hermes-agent/venv/bin/python -c "
import os, yaml
from hermes_cli.tools_config import _get_platform_tools
os.environ.setdefault('HERMES_HOME','/Users/matt/.hermes')
cfg = yaml.safe_load(open(os.path.expanduser('~/.hermes/config.yaml')))
ts = _get_platform_tools(cfg, 'cli')
print('resolved has proxima:', 'proxima' in ts)
print('resolved has agymcp:', 'agymcp' in ts)"

# 3. Whole config still parses + all servers still listed:
hermes mcp list
```

## Then the restart

`CLI_TOOLSETS` is a module-level constant computed once at webui process import, so the fix
only lands after restarting the webui backend + starting a **new** chat:

```bash
la restart hermes-webui   # see references/webui-reload.md
```

## The meta-lesson

Distinguish "restart will fix it" from "no restart can fix it". Logging `registered N tools`
proves the SERVER is connected, not that the resolver chose to inject it. If you've already
restarted + tried a new session and the tools are STILL gone, stop restarting and check
toolset resolution (`CLI_TOOLSETS` / `_get_platform_tools`) — the allowlist bug lives there.
