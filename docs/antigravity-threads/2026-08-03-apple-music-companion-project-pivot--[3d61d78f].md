---
title: "Apple Music Companion Project Pivot"
date: "2026-08-03"
conversation_id: "3d61d78f33b945d9"
source: "antigravity"
---

# Apple Music Companion Project Pivot

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-03 17:45 MDT-6] [context to this point is 0]




[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```







[Attached Context: AI-OS Protocols Context]

```text

[AI-OS Protocols Context]

Project Root: /Users/matt/projects/ai-os

Preflight Routine: python3 /Users/matt/projects/ai-os/scripts/preflight.py

Auto-Commit Routine: python3 /Users/matt/projects/ai-os/scripts/auto_commit.py

Rules Summary: Bun is required for JS projects; ./tmp for temporary scripts; mv ~/.Trash/ for deletions; no heredocs; concise token-efficient outputs.

```







[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

I am reconsidering the direction of a project called "Apple Music Companion" and need your help figuring out the best path forward.




### My Goal & Vision

I want a dead-simple, rock-solid AI companion app for my Apple Music library. 

Key desired functionality:

1. Conversational Chat Interface: To talk naturally with an AI agent about my music library (artists, albums, genres, listening history, preferences).

2. Automated Playlist Generation: Have the agent directly build, modify, and save Apple Music playlists based on natural language queries or conversation.

3. Reliable Music Control: Simple, robust control over local Apple Music / Music.app playback.




Currently, the project is not useful to me because it lacks the core conversational agent and playlist creation capabilities. Instead, we ended up with a basic album art grid and a simple playback controller.




### Current Codebase & Architecture Context

- Repository Location: `/Users/matt/projects/apple-music-companion`

- Existing Features:

  - Web UI displaying an album art grid (built with Bun/HTML/CSS).

  - AppleScript / JSA bridge integration controlling local macOS `Music.app` (play/pause/track info).

  - Local server handling IPC between web frontend and macOS native services.

- Current Gaps:

  - No LLM/agent harness integrated for library intelligence.

  - No deep library indexing or querying engine for agent tool-use (reading library XML/SQLite/ScriptingBridge).

  - No automated playlist creation interface via AppleScript/JSA/MusicKit.




### What I Need Help With

I want to evaluate whether to pivot this current codebase or start fresh with a simple, customizable agent harness / chat WebUI (or leverage an existing rock-solid open-source UI). 




Could you help me:

1. Architectural Options: Compare building onto our current simple Bun server vs. adopting an established open-source chat harness/UI (e.g., Open WebUI, a custom agent web stack, or lightweight sidecar setup) for Apple Music interaction.

2. Library & Playlist Access: What are the cleanest, most reliable ways on macOS to give an LLM agent full access to read/search the Apple Music library and write/generate playlists (e.g., AppleScript/JSA, MusicKit API, local `Music Library.musiclibrary` SQLite parsing)?

3. Recommended Next Steps: Outline a dead-simple, step-by-step roadmap to get a functional MVP focused ONLY on library chat + automated playlist creation as quickly as possible.




4. Recommend me something that's ideally a streamlined, non-bloated, Tauri-based agentic chat framework so I can just figure out how to get the Music library and create playlists in a robust way that doesn't require a paid developer account—that's why I'm not simply making something with AppleMusicKit or whatever; you need a paid dev account which I don't yet have.




In fact, I want this mainly to be just a deep dive on frameworks. I'm tired of reinventing the wheel to get a half-working result at the cost of quota when I COULD have found a suitable framework to work off of that would make everything faster, cheaper, more reliable; better in every way really.

---

## Assistant

1. Architectural Options & Framework Deep Dive

Stop building custom chat UIs from scratch. The web is littered with abandoned, half-baked LLM frontends because handling streaming chunks, markdown rendering, and tool-call states is tedious.

Since you want a non-bloated, Tauri-based agentic chat framework, here are the two most practical paths forward:

**Path A: Fork an Existing Tauri Chat Client (Recommended for Standalone App)**

**Chatbox (Tauri + React):** This is one of the cleanest, most robust open-source Tauri chat clients available. It supports local LLMs, custom API endpoints, and handles all the UI/UX heavy lifting (streaming, markdown, chat history). You can fork it, inject a custom local API provider that points to your Bun server, and strictly focus on the music tools.

**LobeChat:** Heavier than Chatbox, but has a native Tauri desktop build. It has a built-in plugin architecture, meaning you could build your Apple Music controls as a LobeChat plugin rather than modifying the core UI.

**Path B: The Model Context Protocol (MCP) Approach (Recommended for Extensibility)**
Instead of building a dedicated app, build an **MCP Server** in Bun. MCP is an open standard that allows local tools to be exposed to any MCP-compatible chat UI (like Claude Desktop, or your own `ai-os` project).

**Why this wins:** You write zero UI code. You write a Bun script that exposes three tools (`search_library`, `create_playlist`, `play_track`). You plug that script into Claude Desktop (or an open-source MCP client), and the LLM instantly knows how to use them. If you eventually want this in your `ai-os` Tauri harness, you just drop the MCP server in.

2. Library & Playlist Access Strategies

Since you don't have a paid Apple Developer account, MusicKit is off the table. Parsing the raw `Library.musicdb` SQLite file is a massive headache because Apple obfuscates the schema and changes it without documentation.

The cleanest, most reliable method for local macOS control is **JSA (JavaScript for Automation)** executed via Bun.

**For Writing/Controlling (Playlist Creation & Playback):** JSA is flawless here. You can pipe JSA strings directly into `osascript` from Bun. JSA has native permissions to orchestrate the Music app.

**For Reading/Searching (Library Context):**

*Targeted Searches:* Use JSA's `Application("Music").search({for: "query"})`. This is fast enough for dynamic tool calls (e.g., the LLM searching for a specific artist before building a playlist).

*Full Library Indexing:* JSA is too slow to read 10,000+ tracks iteratively. If the LLM needs to know your *entire* library to suggest things, do a one-time export (`File > Library > Export Library` to XML). Parse this XML locally in Bun using a fast XML parser to maintain a lightweight in-memory JSON index or a local SQLite vector database for the LLM to query.

3. The Dead-Simple MVP Roadmap

Here is how to get a functional MVP running without reinventing the wheel.

**Step 1: Set up the Chat Interface (Zero UI Coding)**

Download an MCP-compatible client (like Claude Desktop) or fork **Chatbox**.

If using MCP, initialize a standard Bun project in `./tmp` or your project root specifically for the MCP server.

**Step 2: Build the JSA/Bun Bridge**
Write a simple utility in Bun that executes JSA strings.

JavaScript

```
// /Users/matt/projects/apple-music-companion/lib/jxa-runner.ts
import { spawn } from "bun";

export async function runJXA(script: string) {
  const proc = Bun.spawn(["osascript", "-l", "JavaScript", "-e", script]);
  const text = await new Response(proc.stdout).text();
  return text.trim();
}

```


**Step 3: Expose the "Create Playlist" Tool**
Write the specific JSA logic to create a playlist and add tracks, wrapped in a function your agent can call.

JavaScript

```
// /Users/matt/projects/apple-music-companion/tools/playlist.ts
import { runJXA } from "../lib/jxa-runner";

export async function createPlaylist(playlistName: string, trackNames: string[]) {
  const trackSearches = trackNames.map(name => `
    var result = music.search({for: "${name}"});
    if (result.length > 0) result[0].duplicate({to: pl});
  `).join("\n");

  const script = `
    var music = Application("Music");
    var pl = music.UserPlaylist({name: "${playlistName}"}).make();
    ${trackSearches}
    return "Playlist created successfully.";
  `;
  
  return await runJXA(script);
}

```


**Step 4: Wire the Tools to the Agent**

Define your tool schemas (e.g., `create_playlist(name: string, tracks: string[])`).

Pass these schemas into your chosen framework (via MCP definition or Chatbox custom tool config).

When the LLM decides to build a playlist, it outputs the JSON arguments. Your Bun server parses them, passes them to `createPlaylist()`, and the `osascript` bridge handles the native macOS execution.

By using JSA for execution and an established Tauri client (or MCP) for the interface, you bypass the UI quota drain entirely and focus strictly on the system architecture.

---

## User

[2026-08-03 17:54 MDT-6] [context to this point is 1627]




[Attached Context: AI-OS Protocols Context]

```text

[AI-OS Protocols Context]

Project Root: /Users/matt/projects/ai-os

Preflight Routine: python3 /Users/matt/projects/ai-os/scripts/preflight.py

Auto-Commit Routine: python3 /Users/matt/projects/ai-os/scripts/auto_commit.py

Rules Summary: Bun is required for JS projects; ./tmp for temporary scripts; mv ~/.Trash/ for deletions; no heredocs; concise token-efficient outputs.

```







[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

so the thing is, ai-os is ITSELF half-broken. It's practically unusable.

I've found Antigravity.app is the best option for me (when I have Google API quota available!), but even IT leaves a lot to be desired; particularly that it's closed source and can't be customized really, and it's electron.

I experimented with a few frontends, like ones for Hermes and claude code...

I liked some of them, but I found a few had some bugs that made it unusable really.

Plus, I decided I needed to use Hermes, but then I realized I have to use Antigravity (or agy cli via my custom MCP server) to use up the quota I paid for rather than pay out of pocket... and Antigravity has the best interface I think I've used so far despite its shortcomings, so I just use that.




But I'm just thinking... there's gotta be something out there that I could use for my whole ai-os project... to have a proper triage, and a nice, robust chat interface that can dynamically switch providers, and be how I like it... and not be something I have to built from scratch over the course of 3 months.

There's gotta be some kind of tool for making complex agentic harnesses... right?

I'm curious about something else too...

I sometimes want gemini to research a bunch of sites, but I feel like, it's either: gemini looks up some unknown amount of websites based on what it feels like doing, or I use the deep research mode and it writes me a long ass essay that I don't even bother reading anyway...

I need to figure out something in between. It'd be great if I could say for this chat, for example... `/research 20 websites` or something, you know?

And not have it produce me a giant essay but it just takes all that data into account.

Because too often AI only finds one or two results and recommends me something when there's a far better option; it just didn't bother trying to find it

---

## Assistant

I can help with this. Let's break down the landscape of open-source agent frameworks that could replace your `ai-os` codebase, and how you can handle your research goal.

Since you've experienced the pain of building a custom UI and agent harness from scratch, leveraging an existing, robust open-source solution is definitely the right move. The landscape has matured significantly recently.

Open-Source Agent Harnesses: The Top Contenders

Here is a breakdown of the most relevant open-source frameworks for your `ai-os` replacement, focusing on those that support multi-model routing, persistent memory, and local execution via Tauri or the terminal.

1. Goose (by Block/Agentic AI Foundation)

This is currently one of the most mature and actively developed open-source AI agents.

**Architecture:** Built in Rust. It offers a native desktop app (Tauri-like), a CLI, and an API.

**The Big Draw:** It is built entirely around the **Model Context Protocol (MCP)**. It has over 70+ extensions out of the box (connecting to databases, GitHub, browsers, Google Drive, etc.).

**Multi-Provider:** It supports over 15 providers, including Anthropic, OpenAI, Google (Gemini), and local models via Ollama. You can use your existing API keys or subscriptions.  
Developers Digest

**Why it fits:** It's designed to be a general-purpose agent running on your machine. You can use its desktop app for a visual interface, and because it's MCP-first, you can easily plug in custom tools (like your Apple Music scripts).  
Miraheze

2. OpenHuman

If your vision for `ai-os` heavily involves the agent knowing your context before you even ask, OpenHuman is the standout.

**Architecture:** Rust/Tauri desktop-first application.

**The Big Draw:** It features an automated "Memory Tree." It connects to over 118 services via OAuth (Gmail, Notion, Calendar, Slack) and automatically pulls and compresses that data into an Obsidian-compatible Markdown vault every 20 minutes.  
mager.co - mager.co

**Token Optimization:** It includes "TokenJuice," a layer that aggressively compresses HTML, emails, and tool outputs into dense Markdown before sending them to the LLM, reducing token usage (and cost) by up to 80%.  
mager.co - mager.co

**Why it fits:** If you want an assistant that automatically organizes your life into a local SQLite/Markdown structure without you building the connectors, this is the fastest path.  
mager.co - mager.co

3. EvoAgentX

If you are more interested in defining complex, multi-agent workflows that run autonomously, EvoAgentX is a powerful framework.

**Architecture:** Python-based framework focused on building self-evolving agent ecosystems.  
GitHub

**The Big Draw:** It features "Agent Workflow Autoconstruction," where a single prompt can generate a structured, multi-agent workflow. It also includes self-evolving algorithms and built-in evaluators to optimize agent behavior.  
GitHub

**Why it fits:** It's heavily focused on the *orchestration* side of multi-agent systems and includes memory modules and human-in-the-loop capabilities. It is more of a backend framework than a ready-to-use desktop UI.  
GitHub

The "Antigravity" Situation

You mentioned using Antigravity. Just to clarify the landscape, Google recently launched **Antigravity 2.0**. It's not just the IDE fork anymore; they released a standalone desktop app explicitly for agent orchestration, alongside a CLI version. While it remains closed-source, its architecture (parallel subagents, scheduled workflows, persistent artifacts) is exactly what tools like Goose and OpenHuman are building in the open.  
Reddit
+ 1

Solving the "Research" Problem (The Middle Ground)

You want to avoid the two extremes: the agent randomly checking one or two links, or a massive Deep Research essay that you won't read.

The solution is to use a framework that supports **Headless Subagents** with structured data output.

Instead of typing `/research 20 websites`, you want to use a tool that can spawn a parallel subagent. Both **Goose** and the concepts behind **Antigravity 2.0** support this.

Here is how you structure that workflow to get the middle ground:

**Spawn the Subagent:** Tell your main chat interface to spawn a research agent.

**Define the Output Format:** This is the crucial step. Do not ask for a "summary" or an "essay." Ask for a **Data Table** or a **Markdown List with specific keys**.

*Example Prompt:* "Spawn a research agent to search 15 websites regarding the best local vector databases for Rust. Do not write an essay. Return only a markdown table comparing: Name, License, RAM Usage, Disk Footprint, and Primary Use Case. Save this table silently to my Obsidian vault at `/Personal/AI/vector-dbs.md`."

**Review the Artifact:** The subagent runs in the background. When it finishes, it doesn't dump text into your chat; it simply drops the structured data into your vault. You review the table, and then ask your main chat agent specific follow-up questions based on that data.

This approach separates the *data gathering* from the *conversation*, keeping your chat interface clean while forcing the AI to process a high volume of sources into a scannable format.

---
