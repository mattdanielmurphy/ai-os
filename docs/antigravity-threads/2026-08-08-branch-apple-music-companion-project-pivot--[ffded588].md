---
title: "Branch • Apple Music Companion Project Pivot"
date: "2026-08-08"
conversation_id: "ffded58813ca512e"
source: "antigravity"
---

# Branch • Apple Music Companion Project Pivot

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

[2026-08-08 01:27 MDT-6] [context to this point is 1627] I think you're right, an MCP server is the way to go.

But we've got a bigger problem which is, unfortunately, possibly until I reinstall macOS, we can't rely on Music.app actually being able to open.

---

## Assistant

If `Music.app` is completely failing to launch, we need a "headless" approach. You don't actually need the UI application running to access your library data or play music on macOS.

Here is how you pivot the MCP server to work entirely around the broken `Music.app` process:

1. Read Access: The Headless Daemon (`ITLibrary`)

macOS has a built-in framework called `iTunesLibrary` (which was updated to support Apple Music). It doesn't communicate with the `Music.app` UI process; instead, it talks to a background service called `AMPLibraryAgent`. This means you can read your entire library even if the app crashes on launch.  
Super User

Since it's an Objective-C/Swift framework, you can't hit it natively with Bun, but you can write a tiny Swift CLI script, compile it with the Command Line Tools you already have installed, and execute it from Bun.

Create a file at `./tmp/read_library.swift`:

Swift

```
import iTunesLibrary
import Foundation

do {
    let library = try ITLibrary(apiVersion: "1.1")
    var tracks = [[String: String]]()
    
    for item in library.allMediaItems {
        // Only grab actual local/downloaded songs
        guard let url = item.location, item.mediaKind == .kindSong else { continue }
        
        tracks.append([
            "title": item.title,
            "artist": item.artist?.name ?? "Unknown",
            "album": item.album.title ?? "Unknown",
            "path": url.path
        ])
    }
    
    let jsonData = try JSONSerialization.data(withJSONObject: tracks)
    if let jsonString = String(data: jsonData, encoding: .utf8) {
        print(jsonString)
    }
} catch {
    fputs("Error reading library\n", stderr)
    exit(1)
}

```


Compile it once using the terminal:

Bash

```
swiftc ./tmp/read_library.swift -o ./tmp/read_library -framework iTunesLibrary

```


Now, your Bun MCP server can just run `./tmp/read_library`. It will instantly spit out a clean JSON array of your entire library, including the exact file paths on disk, completely bypassing the broken app.

2. Write Access: `.m3u8` Playlists

Since JXA/AppleScript can't automate a broken UI to create native playlists, have your agent generate standard `.m3u8` files.

An `.m3u8` playlist is just a UTF-8 text file containing the absolute file paths to the audio files. Your agent searches the JSON output from Step 1, grabs the file paths for the requested songs, and your Bun server writes them to a file:

JavaScript

```
// Example Bun MCP Tool Logic
const playlistName = "Agent_Focus_Mix.m3u8";
const paths = [
  "/Users/matt/Music/Music/Media.localized/Music/Artist/Album/Song1.m4a",
  "/Users/matt/Music/Music/Media.localized/Music/Artist/Album/Song2.m4a"
];

// Standard m3u8 format
const content = "#EXTM3U\n" + paths.join("\n");
await Bun.write(`/Users/matt/Desktop/${playlistName}`, content);

```


When you eventually reinstall macOS or fix `Music.app`, you simply drag and drop these `.m3u8` files into the application, and it will instantly recreate all the playlists natively. In the meantime, any third-party player (VLC, IINA, Swinsian) can open them.

3. Playback: Native Terminal Audio (`afplay`)

To actually listen to the music right now, use `afplay`, the native macOS command-line audio player. It handles `.m4a`, `.mp3`, and ALAC natively with practically zero overhead.

Your MCP server can expose a `play_track` tool that simply spawns a background process in Bun:

JavaScript

```
import { spawn } from "bun";

// Kills existing playback, starts new track
export function playTrack(absolutePath) {
  Bun.spawn(["pkill", "afplay"]); 
  Bun.spawn(["afplay", absolutePath]); 
}

```


This isolates your entire stack. The agent reads the library via the headless Swift bridge, plays audio via `afplay`, and writes state to disk via `.m3u8` files. No paid developer accounts, no UI dependencies, and it works perfectly well inside an MCP harness.

---
