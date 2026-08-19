---
title: "Use proxima mcp server"
date: "2026-08-11"
conversation_id: "55b8ff579d5e"
source: "antigravity"
---

# Use proxima mcp server

## User

hermes mcp list

  MCP Servers:

  Name             Transport                      Tools        Status    
  ──────────────── ────────────────────────────── ──────────── ──────────
  agymcp           /Users/matt/.local/bin/ag...   all          ✓ enabled
  hermes-studio-api /Users/matt/.hermes-web-u...   all          ✓ enabled
  hermes-studio-devices /Users/matt/.hermes-web-u...   all          ✓ enabled
  hermes-studio-use /Users/matt/.hermes-web-u...   all          ✓ enabled
  chrome-devtools  bunx -y chrome-devtools-mc...   all          ✓ enabled
  proxima          node /Users/matt/projects...   36 selected  ✓ enabled

Use proxima mcp server as a test for me. It says you have it.
use ask_perplexity with a simple prompt.

---

## Assistant

Let me look up the Proxima MCP tool details so I can call it properly.

The Proxima MCP server is connected but its tools aren't showing up in `tool_search`. Let me check what tools it exposes directly.

Operation interrupted.

---

## User

continue

---

## Assistant

The `ask_perplexity` tool from the proxima MCP server isn't showing up in `tool_search`. The search only surfaced tools from `agymcp`. Let me check if the proxima server tools are actually loaded by searching with the service name.

The proxima MCP server's tools aren't surfacing through `tool_search` — only agymcp's tools are indexed. Let me check whether the proxima tools are loaded at all and whether there's a config issue, using the hermes-agent skill to diagnose.

I can only see agymcp's 15 tools indexed. The proxima server's 36 tools are not loaded into my available toolset — they don't appear via `tool_search` at all. This means the proxima MCP server is "enabled" in config but its tools aren't being surfaced to this session.

Let me diagnose this. First let me check the hermes-agent skill for how MCP servers and their tools get loaded, and check the actual config.

The proxima server is configured with 36 selected tools, but those tools aren't appearing in my `tool_search` index — only agymcp's tools are. Let me look at the actual config to understand how proxima tools are selected and whether they use a naming convention I should search for.

The config looks correct — `ask_perplexity` is in the include list and proxima is enabled. The tools should be named like `mcp__proxima__ask_perplexity` if the search index worked. My `tool_search` only indexes 15 tools (the agymcp batch), and it seems the index shows only `available_sources: [agymcp]`.

This looks like the deferred `tool_search`/`tool_describe`/`tool_call` mechanism only loaded the agymcp server's 15 tools and not proxima's. Let me try searching specifically for the exact tool name and also verify it directly by probing the proxima MCP server manually via the protocol (stdio), since I know the command.

Let me try the deferred tool system with the exact tool name, and in parallel verify the server responds.

I have a clear picture now. The Proxima MCP server is correctly configured and its server file exists, but its tools are **not loaded into this session's toolset** — `tool_search` only indexes agymcp's 15 tools, and does not see Proxima's 36 selected tools at all (including `ask_perplexity`). So the tools aren't available to me to call.

Let me verify directly by talking to the Proxima MCP server over stdio to confirm the server itself is healthy and the tool exists, so I can tell you definitively whether it's a server problem or a Hermes loading problem.

The server works — it listed its tools correctly at the protocol level. So the Proxima MCP server is healthy. The problem is purely on the Hermes side: the Proxima tools aren't being loaded into my session's toolset.

Let me confirm the tools list actually contains `ask_perplexity` and check the full list, to nail down the exact issue.

I have a definitive diagnosis now. Let me give you the bottom line.

## Diagnosis: Proxima server is fine, but its tools aren't loaded in *this* session

Here's what I confirmed:

1. **The Proxima MCP server is healthy.** When I probed it directly over stdio (`node src/mcp/index.js`), it listed all 41 tools correctly — including `ask_perplexity` and `ask_gemini`. So the server itself works fine.

2. **Hermes recognizes Proxima as enabled.** `hermes mcp list` shows `proxima ... 36 selected ✓ enabled`, and your `config.yaml` has the correct `tools.include` list with `ask_perplexity` in it.

3. **But Proxima's tools are not actually loaded into my session's toolset.** My `tool_search` mechanism only indexes **15 tools from `agymcp`** — it sees `agymcp` as the *only* connected source. The 36 Proxima tools (including `ask_perplexity`) never appear, no matter how I search (`ask_perplexity`, `proxima …`, etc.). So even though MCP lists it as enabled, the tool integration wasn't surface in this running session.

**Net result:** I cannot actually call `ask_perplexity` from here — the tool isn't reachable, so I can't fabricate a "test call." I won't pretend it worked when it didn't.

## Why this happens
The `tool_search` index was built when this session started, and only the `agymcp` server's tools made it into the deferred-tool catalog. Proxima's tools were filtered/missing from that catalog even though the server connects. This is typically a **session-loaded-tools issue, not a server issue** — the config is correct.

## To get Proxima's tools live
The most reliable fix is a fresh session so Hermes re-reads the MCP config and loads the 36 Proxima tools into the tool catalog:
- Start a `/new` session (or restart the Hermes process) and ask me to call `ask_perplexity` again.
- Alternatively, update the Proxima config exclude/tools and re-enable it with `hermes mcp` to force a reload in-place (this may still need a fresh session to take effect in this WebUI).

Want me to check the Hermes MCP config format for a way to force-reload Proxima without a full restart, or shall we just have you open a fresh session and re-run this as a quick smoke test? I'd suggest the fresh session — it's the cleanest confirmation that the tool lands.

---

## User

how do I restart Hermes?

---

## Assistant

The answer depends on how Hermes is running. Let me check the running Hermes processes so I give you the exact restart command for your setup rather than a generic one.

I have a full picture of your Hermes setup now. You're running the **WebUI** (labeled LaunchAgent `com.parantoux.hermes-webui`, PID 9351 = `server.py`) plus the **gateway** (`com.matt.agent.hermes-gateway`, PID 9381 via the `aios_hermes_wrapper`) and a **dashboard** on port 9120 (PID 65099). The session I'm in is the WebUI.

Let me check the exact LaunchAgent details so I give you commands that match your actual setup (not generic ones) — including whether the gateway wrapper auto-restarts.

I have the full picture. Here's how to restart Hermes for your exact setup.

## The component running this chat = the **WebUI**

You're talking to me through the **Hermes WebUI** (`server.py`, LaunchAgent label **`com.parantoux.hermes-webui`**, port 8787). That's the thing that needs restarting to reload the Proxima MCP tools. The gateway (`com.matt.agent.hermes-gateway`) and dashboard (port 9120) are separate and don't need touching for the MCP tool load.

## Restart the WebUI

```bash
launchctl kickstart -k gui/501/com.parantoux.hermes-webui
```

`-k` kills and restarts it. Because `KeepAlive` is `true` and `RunAtLoad` is `true`, the LaunchAgent brings the WebUI straight back up on port 8787 automatically. This reloads the MCP config, so the Proxima `ask_perplexity` tool should land in the new session.

**Then: open `/new` in this WebUI** (or reload the page) so the fresh session actually indexes Proxima's tools. A restart alone won't help the session you're in right now — the tool catalog is fixed when a session starts.

## The full-kill variant (if you want everything: gateway + dashboard + webui)

```bash
# Stop all three tracked services
launchctl bootout gui/501/com.parantoux.hermes-webui
launchctl bootout gui/501/com.matt.agent.hermes-gateway

# Dashboard isn't a LaunchAgent — it's a bare process (PID 65099).
# Kill it; restart manually when ready:
kill 65099
```

Then to bring them back:
```bash
launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.parantoux.hermes-webui.plist
launchctl bootstrap gui/501 ~/Library/LaunchAgents/com.matt.agent.hermes-gateway.plist
# and for the dashboard:
hermes dashboard --no-open --host 127.0.0.1 --port 9120
```

## My recommendation
For your goal — getting `ask_perplexity` loaded — **just restart the WebUI** with the single `kickstart` command, then start a fresh session. You don't need to bounce the gateway or dashboard.

⚠️ One heads-up: restarting the WebUI will kill *this* running session mid-flight. I won't survive the restart, so once you run it this conversation closes out. After the restart, in the fresh session just say **"call ask_perplexity with a simple prompt"** and we'll confirm the tool loaded.

Want me to run the WebUI restart for you now?

---
