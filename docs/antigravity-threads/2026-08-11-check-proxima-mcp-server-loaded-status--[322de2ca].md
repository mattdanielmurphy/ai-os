---
title: "Check Proxima MCP server loaded status"
date: "2026-08-11"
conversation_id: "322de2cae790"
source: "antigravity"
---

# Check Proxima MCP server loaded status

## User

do you see Proxima mcp server loaded for you?

---

## Assistant

I'll check whether a Proxima MCP server is loaded for me. Let me look at my available tools and MCP configuration.

Let me check what MCP servers are actually loaded/configured for me. Let me look at my configured tools and MCP config directly.

Proxima MCP server **is** configured and enabled. Here's what I see:

**From `hermes mcp list`:**
```
proxima   /Users/matt/.local/bin/no...   36 selected   ✓ enabled
```

So the **proxima** MCP server is loaded, running the local binary (`/Users/matt/.local/bin/no...` — cut off, likely `node` based on the path pattern), with **36 tools selected** and status **enabled**.

However — there's a key distinction I need to flag. Let me check whether its tools are actually exposed to *this* session. The config shows it's enabled globally, but I don't see any `proxima_*` tools in my available tool list right now. Let me verify the actual selection.

I have the full picture now.

## Yes — Proxima MCP is loaded and enabled for me

**Server config:**
- **Name:** `proxima`
- **Binary:** `/Users/matt/.local/bin/node` running `/Users/matt/projects/external/Proxima/src/mcp/index.js`
- **Status:** `enabled: true`
- **Tools:** a curated allowlist (`tools.include`) — the output was cut off, but it selects 36 tools starting with `ask_gemini`, `ask_perplexity`, `smart_query`, `new_conversation`, `verify_code`, `explain_code`, `generate_code`, `optimize_code`, and ending with `proxima_cost_report`, `proxima_agentic_status`.

So the server is **configured and enabled globally** in `/Users/matt/.hermes/config.yaml`, and Hermes reports it with **36 selected tools, status ✓ enabled**.

## One caveat to flag honestly

Even though the server is enabled in config, I don't currently see any `mcp__proxima__*` tools in **my active tool list** for this session. In Hermes, MCP tools are typically exposed as `tool_call(name="mcp__<server>__<tool>")` and loaded on-demand. Right now my immediate toolset doesn't include them — which means either:

1. They're loaded lazily (available via `tool_search`/`tool_describe` but not listed up-front), or
2. This particular session/WebUI connection wasn't refreshed after the server was last (re)started.

Let me check whether the tools are actually reachable right now.

That confirms it. The search only surfaces **agymcp** tools (and other deferred tools), not any `mcp__proxima__*` tools. Let me check the full tool listing to be certain Proxima's 36 tools aren't registered under this session.

Confirmed. Here's the honest, complete answer:

## Proxima MCP: configured + enabled on disk, but **NOT loaded into this session**

**The server exists and is healthy in config:**
- `proxima` is defined in `~/.hermes/config.yaml` → runs `node /Users/matt/projects/external/Proxima/src/mcp/index.js`, `enabled: true`, with a 36-tool allowlist.

**But it is NOT currently exposed to me.** My on-demand tool registry (`tool_search`/`tool_describe`) only shows one connected MCP source — **`agymcp`** (15 tools) — plus my native toolset. Zero `mcp__proxima__*` tools (e.g. `ask_gemini`, `smart_query`) are importable into this session right now.

## Why the gap

`hermes mcp list` reads the **config** and shows "selected/enabled", but this **WebUI session** appears to have connected before Proxima was (re)started, or the session's MCP tool registry didn't pick it up. The config being correct doesn't mean the live session has the 36 tools wired in — and right now, it doesn't.

## How to fix it

The typical fix in Hermes is to **restart the MCP server** so the current session picks it up, or start a fresh session. Let me check if there's a way to reload it live before suggesting that.

There's a `hermes mcp test` command to verify the server actually responds. Let me run it against proxima to confirm the binary works and the 36 tools are reachable — the issue may just be the live session tool registry, not the server itself.

The server is fully healthy and reachable. Here's the complete, verified picture:

## ✅ Proxima MCP is loaded and functional — here's the full status

**`hermes mcp test proxima`** confirms the server handshake and tool discovery succeed live:
```
Transport: stdio → /Users/matt/.local/bin/node
Auth: none
✓ Connected (552ms)
✓ Tools discovered: 40
```
(`40` the server exposes; your config allowlist is trimming it to the `36 selected` you saw in `mcp list`.)

The 40 tools include exactly what you'd expect from Proxima's Agent Hub:
- **Direct providers:** `ask_gemini`, `ask_claude`, `ask_chatgpt`, `ask_perplexity`, `ask_model`, `ask_all_ais`
- **Smart entry:** `smart_query`, `new_conversation`
- **Code tools:** `generate_code`, `verify_code`, `explain_code`, `optimize_code`, `review_code`, `solve`, `fix_error`, `build_architecture`, `write_tests`, `convert_code`, `security_audit`, `analyze_file`, `review_code_file`
- **Research/web:** `deep_search`, `web_scrape`, `ddg_search`
- **Pipelines:** `run_workflow`, `run_loop`, `crew`
- **Content/compare:** `content`, `compare`, `debate`, `verify`
- **Window/status:** `show_window`, `hide_window`, `toggle_window`, `set_headless_mode`, `proxima_cost_report`, `proxima_agentic_status`

## One honest caveat for *this* session

The server is connected **and** test-able — but its tools aren't in **my live importable registry** for this WebUI session. Right now `tool_search` only lists `agymcp` (15 tools) plus my native set; no `mcp__proxima__*` entries are importable mid-session. The config + server are correct; what's stale is this session's connected-tool registry (it likely attached before Proxima was last (re)started).

**Fixes, in order of least friction:**
1. **Start a new session** (or `/new`) — the fastest, most reliable path; fresh sessions pull the full enabled toolset including Proxima's 36.
2. **Restart the Hermes gateway/runtime** if you want to keep this browser tab — that reloads the MCP tool registry into connected sessions.

Want me to walk you through restarting so Proxima's tools become importable in this tab, or will you spin up a fresh session? Just say the word and I'll run it.

---
