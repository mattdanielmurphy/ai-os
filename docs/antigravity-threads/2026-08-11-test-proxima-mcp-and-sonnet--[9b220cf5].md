---
title: "Test Proxima mcp and sonnet"
date: "2026-08-11"
conversation_id: "9b220cf5bb87"
source: "antigravity"
---

# Test Proxima mcp and sonnet

## User

We need to use our Proxima mcp server and ask_perplexity in Hermes.
I set it up with Antigravity; I don't know if it's set up here in Hermes.
See if it works, and do a test call to sonnet. Don't attach a file please!

---

## Assistant

Let me check if the Proxima MCP server is set up in this Hermes profile.

No direct Proxima config found in the file tree. Let me check the Hermes config files and MCP server config to see if it's registered.

Let me check the config.yaml for MCP server entries and the providers.json for Proxima:

No Proxima or ask_perplexity found. Let me check the MCP section of config.yaml and see the rest:

Found it — Proxima MCP server is set up under Antigravity (`~/.gemini/antigravity/mcp/proxima`), but not registered in Hermes' `config.yaml`. Let me check what Proxima exposes:

Found it. Proxima MCP server is installed at `~/.gemini/antigravity/mcp/proxima/` (configured in Antigravity's tool spec — 39 tools including `ask_perplexity`, `ask_claude`, etc.) but **not registered in Hermes' `config.yaml`** under `mcp_servers`.

Let me see how Proxima exposes itself — what command runs it:

These are just tool-spec JSON files (tool definitions for the MCP server). I need to find the actual MCP server executable. Let me check how Antigravity registers it:

Now I see it — Proxima's MCP server is started via `node src/mcp/index.js`. Let me check the MCP entry point and see if it's running:

Proxima's MCP server is already running on stdio transport. Now I need to register it in Hermes' `config.yaml` as an MCP server. Let me check its available tools (from the JSON specs) and then add it to the config:

Good — BYOK mode is disabled (`enabled: false`) which means Proxima is using its built-in session providers. Now let me register it as an MCP server in Hermes and test it

Now I'll add the Proxima MCP server to the config. It runs via `node src/mcp/index.js` inside the Proxima project directory:

Right — can't edit the Hermes config directly. Let me use the `hermes config` CLI instead:

Now I need to load the `hermes-agent` skill to see if there's a proper MCP server reload command:

I see the `hermes mcp add` command mentioned in the skill. Let me use it:

Now let me check — Proxima's MCP server uses stdio transport. The existing config I set via `hermes config set` should work. Let me verify it was written correctly and try to add it via the proper `hermes mcp add` command

It already exists (from my `hermes config set` earlier). Let me test the connection:

Connection failed. The issue is Proxima's MCP server is already running (several instances from the `ps` output earlier), and the stdio transport creates a new subprocess that tries to bind to the same IPC port (19222). Let me check what's happening:

That path doesn't exist. Let me find the correct node binary:

Node is at `~/.local/bin/node`. Let me also check if there's a `bun` binary in the Proxima project:

Operation interrupted.

---
