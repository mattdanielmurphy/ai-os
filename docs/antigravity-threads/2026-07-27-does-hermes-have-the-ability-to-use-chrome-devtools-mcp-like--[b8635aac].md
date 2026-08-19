---
title: "does Hermes have the ability to use chrome devtools mcp like Antigravi"
date: "2026-07-27"
conversation_id: "b8635aac33f1"
source: "antigravity"
---

# does Hermes have the ability to use chrome devtools mcp like Antigravi

## User

does Hermes have the ability to use chrome devtools mcp like Antigravity?

---

## Assistant

Let me check the current MCP setup and Hermes docs.

Let me check if Chrome DevTools MCP is already configured in your Hermes setup, and read the relevant docs.

Let me check if it's already configured in your Hermes config

**Yes**, Hermes supports Chrome DevTools MCP — but it's not currently configured on your machine.

Here's the breakdown:

### Current state
Your Hermes config (`~/.hermes/config.yaml`) only has these MCP servers active:
- `agymcp` (agy integration)
- `hermes-studio-mcp` (Hermes Studio)

No Chrome DevTools MCP server is present yet.

### What Hermes is capable of
The official Hermes docs cover `chrome-devtools-mcp` setup in the [MCP guide](file:///Users/matt/.hermes/hermes-agent/website/docs/guides/use-mcp-with-hermes.md). The system prompt even already has safety rules referencing `mcp_chrome-devtools_*` tools — meaning the tooling is designed to work once the MCP server is added. And since Chrome is already running on port `9223` on this machine (as noted in `MAC_ENVIRONMENT.md`), it's ready to connect.

### To add it
Run this from the terminal:

```bash
hermes mcp add chrome-devtools --command npx --args -y chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

Then `/reload-mcp` to pick up the new tools. After that, you'll have tools like `mcp_chrome-devtools_list_pages`, `mcp_chrome-devtools_new_page`, etc. — same as what Antigravity offers through its CDP integration, but surfaced as MCP tools.

Want me to go ahead and set it up?

---
