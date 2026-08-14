---
title: "Hermes Agent ACP Support and Setup"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "5576f77e-181c-5f35-983c-4e8c78ae5aa1"
url: ""
---

# Hermes Agent ACP Support and Setup

> [!NOTE]
> Archived Gemini Thread: [Hermes Agent ACP Support and Setup]() | Date: 2026-08-13

## User
[2026-07-14 14:09 MDT-6] [context to this point is 0] wait does hermes agent have ACP?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-14 14:09" -->

---

## Gemini
**Yes, Hermes Agent does support ACP** (Agent Client Protocol).  
Hermes Agent - nous research

It can run as an ACP server, allowing compatible editors (like VS Code and Zed) to communicate with Hermes over `stdio`.

What Hermes Exposes in ACP Mode

When running in ACP mode, it uses a curated toolset (`hermes-acp`) designed for seamless, editor-native workflows:

**File Tools:** `read_file`, `write_file`, `patch`, and `search_files`.

**Terminal Tools:** `terminal` and `process`.

**Browser/Web Tools** for web searches.  
Hermes Agent - nous research

**Approval Controls:** Simpler session-scoped prompt approvals (`allow_once`, `allow_session`, `allow_always`, `deny`) directly inside the editor UI.

How to Connect
1. Via VS Code (Manual Setup)  
Hermes Agent - nous research

You can define the agent manually in your VS Code settings under `acp.agents`:

JSON

```
{
  "acp.agents": {
    "Hermes Agent": {
      "command": "hermes",
      "args": ["acp"]
    }
  }
}

```

2. Via Zed  
Hermes Agent - nous research

You can install it directly from the official ACP Registry:  
Hermes Agent - nous research

Open the Agent Panel in Zed.  
Hermes Agent - nous research

Click **Add Agent** (or run `zed: acp registry`).

Search for **Hermes Agent** and install it.

**Note:** To run Hermes in ACP mode, make sure you have installed the ACP extra dependencies locally using `pip install -e '.[acp]'` (or via `uv`).  
Hermes Agent - nous research

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-14 14:09" -->

---

## User
[2026-07-14 14:09 MDT-6] [context to this point is 468] what's the best ACP plugin for vscode?

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-14 14:09" -->

---

## Gemini
The landscape for **Agent Client Protocol (ACP)** extensions in VS Code has shifted toward polished, multi-agent management UIs. The standard protocol allows these extensions to let you swap out agents (like Claude Code, GitHub Copilot CLI, Gemini CLI, or your custom Hermes build) using a single, unified interface.  
GitHub

The top three ACP clients available on the VS Code Marketplace right now vary depending on how you like to work:

1. Multicoder (Best Overall / Feature-Rich)

**Multicoder** has become the go-to choice if you want deep IDE integration and visibility into exactly what an autonomous agent is doing to your files.  
Visual Studio Marketplace

**The Standout Feature:** It provides dedicated workspace sidebars for **Changes** (a tree view of file modifications) and an **Edit Timeline**. If an agent makes a sweeping multi-file change, you can click it to pull up a native VS Code diff side-by-side.  
Visual Studio Marketplace

**UI/UX:** Very polished sidebar chat panel with collapsible "thinking/reasoning" blocks, markdown, and token/usage tracking.

**Config:** It maps perfectly to Zed's standard `agentServers` format, making it incredibly easy to copy-paste configurations.

2. ACP Pro (Best for Tabs & Multi-Session Workflows)

**ACP Pro** is optimized for running multiple agent tasks at the exact same time without them stepping on each other's toes.

**The Standout Feature:** It handles a tabbed chat interface. You can have an active debugging session with your Hermes agent in one tab, and a parallel architectural conversation with Claude Code in the next.  
Open VSX Registry

**Sharing:** It includes a built-in "Bridge" server. You can easily stream or share a live agent session's progress with a teammate over a local WebSocket link.  
Open VSX Registry

**Simplicity:** Relies heavily on cached `npx` execution for mainstream agents so you don't have to pre-install them globally.  
Open VSX Registry

3. ACP Client (formulahendry) (Best for Lightweight/Pure Spec Setup)

Built by the creator of the ubiquitous Code Runner extension, **ACP Client** (`formulahendry.acp-client`) is a highly pragmatic, rock-solid client that strictly follows the protocol spec.  
GitHub

**The Standout Feature:** Protocol traffic logging. If you are debugging a custom agent configuration (like tweaking standard input/output streams or custom capability flags), it lets you inspect raw JSON-RPC messages directly inside the editor.  
GitHub

**UI/UX:** A clean, uncluttered, single-agent focused view that feels native to the base VS Code design.  
GitHub

Connecting Your Custom Hermes Build

Since you're working with Hermes, **Multicoder** or **ACP Client** are your cleanest options because they parse session-scoped permission approvals beautifully.

Whichever you choose, you'll just drop your command configuration into your global `settings.json`:

JSON

```
"acp.agents": {
  "Hermes": {
    "command": "hermes",
    "args": ["acp"]
  }
}

```


*(Note: If using Multicoder, the settings key defaults to `"multicoder.agentServers"`, but the structure remains the same).*

Are you planning to run Hermes primarily for local workspace edits, or are you hooking it up to external MCP tools?

<!-- /gemini-message -->

---

