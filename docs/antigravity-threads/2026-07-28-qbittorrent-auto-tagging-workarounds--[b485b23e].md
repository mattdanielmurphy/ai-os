---
title: "qBittorrent Auto-Tagging Workarounds"
date: "2026-07-28"
conversation_id: "b485b23e75eca5e3"
source: "antigravity"
---

# qBittorrent Auto-Tagging Workarounds

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-07-28 17:07 MDT-6] [context to this point is 0] how do you set up auto tagging for qbittorrent items? Like I just want a simple: "if it's this tracker, then assign this tag"

---

## Assistant

Here is the reality: **qBittorrent does not have a native rule engine built into the client for automatic tagging based on trackers**.

However, depending on your setup, you have a few ways to accomplish this ranging from native workarounds to lightweight external scripts.

Option 1: Use external management scripts (The intended approach)

Because native tracker-to-tag rules don't exist in qBittorrent, the community relies on small background utilities that connect via qBittorrent's WebUI API:  
autobrr

**qbit_manage (Recommended for full automation):** A widely-used Python script/Docker container designed explicitly for qBittorrent. You define a `tracker_tag` section in a single YAML file, and it dynamically scans your torrents and assigns tags based on domain matches (e.g., `*IPTorrents*` -> `IPT`).  
autobrr
+ 1

**qbittools:** A simple CLI tool that can tag torrents by tracker, status, or errors.  
autobrr

Option 2: Let your *arr apps handle it (If using Sonarr/Radarr)

If you download through automated managers (Sonarr, Radarr, Prowlarr):

In your **Radarr/Sonarr Settings > Download Clients > qBittorrent**, you can specify a default **Tag** or **Category** for everything grabbed by that application.

In **Prowlarr**, under indexer settings, you can pass specific tags down to download clients based on which indexer was used.

Option 3: RSS Feed Auto-Tagging

If you pull torrents via **RSS feeds** directly inside qBittorrent:

Go to **View > RSS Downloader**.

Create or select a rule.

Under **Rule Settings**, assign the **Assign Tags** field to whatever you want for that feed (since each RSS feed usually corresponds to one specific tracker).

Option 4: Execute a script on torrent completion

qBittorrent allows running an external program when a torrent is added or finished (**Settings > Downloads > Run external program on torrent added**).

You can point it to a simple Python/Bash script using the API. qBittorrent provides parameters like `%I` (Info Hash) and `%T` (Tracker URL):

Bash

```
python3 /path/to/tag_script.py "%I" "%T"

```


The script can then evaluate the tracker URL string and send a POST request back to qBittorrent’s API (`/api/v2/torrents/addTags`) to attach your target tag automatically.

---

## User

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







[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

is there a more "scriptable" modern version of a torrent client for macos that can match qbittorrent's speeds?

---

## Assistant

Here's my take: **You don't actually need to replace qBittorrent to get hyper-scriptable automation and max speeds.**

qBittorrent *is* the gold standard on macOS for raw speed and libtorrent performance. Instead of swapping clients, power users achieve modern scriptability by decoupling the background engine from the control layer using a few specific tools:

Option 1: Use `autobrr` (Best for rule-based auto-tagging & speed)

If your goal is automated tracker-based rules, **autobrr** is the modern CLI/Go-based automation daemon. It runs as a lightweight service on your Mac, Hooks into tracker feeds (IRC/RSS), and sends torrents directly to qBittorrent.  
GitHub

**Why it wins:** It has built-in rule engines for auto-assigning **tags, categories, save paths, and download limits based on tracker domain, regex, or size**.

**Setup:** Easily runnable as a single binary via `brew install autobrr` or Docker.

Option 2: Put **Flood** in front of qBittorrent

If you hate qBittorrent’s default UI and want a slick, modern Web UI alongside a developer-friendly REST/OpenAPI endpoint, check out **Flood**.

**How it works:** Flood runs as a Node.js background process that connects directly to qBittorrent's API.  
QuickBox.IO

**Scriptability:** Flood exposes a modern OpenAPI spec / Swagger UI. You keep qBittorrent’s underlying download speed while controlling it through Flood’s GraphQL/REST interfaces or clean web dashboard.  
GitHub

Option 3: Swap to **Deluge** (If you want a native Daemon/CLI architecture)

If you genuinely want a client that is built from the ground up to be headless, scriptable, and modular:

**Architecture:** Deluge operates as a dual-part application: `deluged` (the daemon running in the background) and whatever interface you choose (Mac GUI, Web UI, CLI via `deluge-console`, or Python RPC).

**Speed:** Like qBittorrent, Deluge is built on **libtorrent (C++)**, meaning network throughput and peer handling are identical.

**Scripting:** Deluge has a rich Python plugin engine and a native Python RPC interface, making scripting custom rules (like auto-tagging by tracker) far simpler than writing custom API wrappers for traditional GUIs.

The Verdict
Solution	Speed	UI	Scriptability	Use Case
**qBittorrent + autobrr**	Max	Native / Web	High	Auto-tagging, regex filtering, private tracker automation
**qBittorrent + Flood**	Max	Sleek Web UI	High (OpenAPI)	Modern dashboard + scripting layer
**Deluge (Daemon)**	Max	Minimal / CLI	Very High (Python RPC)	Custom CLI control and deep plugin scripting

If tracker-based tagging was the main headache, pairing **qBittorrent + autobrr** gives you total scripting control over your torrent pipeline without sacrificing a single megabit of transfer speed.

---

## User

I'd love something that can be controlled by agents easily as well

---

## Assistant

If you want LLMs or autonomous agents to control torrents on macOS (reading state, adding magnet links, auto-tagging, pausing, moving files), **Transmission** and **qBittorrent** are by far the two easiest to integrate into agentic workflows.

The most developer- and agent-friendly setups break down into two core options:

1. Transmission (`transmission-daemon`)

*The undisputed king of minimalist, agentic control.*

**Why Agents Love It:** Transmission runs as a headless, ultra-lightweight background daemon with a standardized, stateless **JSON-RPC API**. Agents don't have to deal with complex cookie sessions or fragile WebUI parsing.  
Wikipedia

**Tooling / SDKs:**

**Python:** `transmission-rpc` (Type-hinted, sync/async support, near-zero overhead).  
PyPI

**TypeScript/Bun:** `@ctrl/transmission` or direct JSON-RPC HTTP payloads using `fetch`.

**Execution on Mac:**

Bash

```
brew install transmission-cli
transmission-daemon --foreground --port 9091

```


**Agent Integration Example (Python):**

Python

```
import transmission_rpc

client = transmission_rpc.Client(host="localhost", port=9091)
# Agent adds a torrent and tags/labels it cleanly in 2 lines:
torrent = client.add_torrent("magnet:?xt=urn:btih:...")
client.change_torrent(torrent.id, labels=["tracker-name", "ai-processed"])

```

2. qBittorrent via WebAPI + Typed SDKs

*Best if you need maximum swarm speeds and advanced libtorrent settings.*

qBittorrent’s native WebUI API exposes almost everything the client can do (categories, tags, piece priority, tracker edits). To make it agent-friendly, pair it with well-typed SDK wrappers.

**Tooling / SDKs:**

**Python:** `qbittorrent-api` (The definitive SDK; fully type-hinted, handles auth tokens/cookies automatically under the hood).

**TypeScript/Bun:** `@ctrl/qbittorrent` or `@robertklep/qbittorrent`.

**Agent Integration Example (Bun / TS):**

TypeScript

```
import { QBittorrent } from '@ctrl/qbittorrent';

const client = new QBittorrent({
  baseUrl: 'http://localhost:8080',
  username: 'admin',
  password: 'yourpassword',
});

// Agent inspects torrents and applies tags based on tracker URL
const torrents = await client.listTorrents();
for (const t of torrents) {
  if (t.tracker?.includes('specific-tracker.com')) {
    await client.addTorrentTags(t.hash, ['my-tag']);
  }
}

```

3. Exposing Torrents as Agent "Tools"

If you're using function-calling or local agent frameworks (e.g., LangChain, LlamaIndex, or custom Zod tool definitions in TS), exposing your torrent client via simple wrappers is straightforward:

TypeScript

```
// Example Tool Definition for an Agent
import { z } from 'zod';

export const addTorrentTool = {
  name: 'add_torrent_with_tag',
  description: 'Downloads a torrent magnet link and assigns a specific organizational tag.',
  parameters: z.object({
    magnetUrl: z.string().url(),
    tag: z.string().describe('The target tag based on content or tracker'),
  }),
  execute: async ({ magnetUrl, tag }) => {
    // Client API logic here
    return { status: 'success', message: `Added torrent with tag: ${tag}` };
  },
};

```

Summary Recommendation

**If you want the cleanest API with zero boilerplate:** Switch to `transmission-daemon`. Its JSON-RPC spec is tiny, predictable, and requires almost no prompt tokens for an LLM to write code against.

**If you want max download speeds and fine-grained settings:** Stick with **qBittorrent**, enable the WebUI, and use `qbittorrent-api` (Python) or `@ctrl/qbittorrent` (Bun/TS) as the agent's translation layer.  
GitHub

---

## User

hmm.

Please stop giving me code snippets and stuff.

You type so goddamn much every time I say something that it's overwhelming. It makes me constantly skim over what you've written and it makes these threads get out of hand really qucikly.

You also jump to providing me code way too quickly.




---




I mean, I like sticking with what I know. I know qbittorrent can *usually* stream torrents and is fast and reliable, and I'm used to the GUI. It's not the best GUI ever but it's fine for what it is, and I'm used to it.

Now, what do I really want to automate?

Basically it's just this very simple auto-tagging thing... I guess I wouldn't mind moving media things to my CloudMounter drive in their respective locations would be nice.

And I always want to be able to configure everything with text files so an agent can do it for me.

---

## Assistant

Fair point. I'll cut the code blocks and keep this direct.

If you want to keep qBittorrent, keep the GUI, and have text-file configuration that an agent can easily manage, your best bet is **qbit_manage**.

Here is why it fits:

**Pure YAML config:** Everything is set up in a single, plain text file (`config.yml`). An agent can read, edit, or write rules without needing to interact with qBittorrent's GUI or API directly.

**Tracker-to-tag matching:** You write simple text rules in that YAML file to say "if tracker contains X, apply tag Y."

**Category and path management:** It can automatically assign categories or move completed files to specific paths (like your CloudMounter drive) based on tags, categories, or tracker state.

**qBittorrent stays untouched:** You don't have to switch clients or abandon the GUI you like. It just runs periodically in the background (via terminal or Docker) and cleans up your library.

---

## User

ok give me a prompt to get this set up and configured the ways I mentioned.

First give an outline of what you think I want done (high level, concisely, but define everything that's being done), and then a code block containing a simple prompt that just explains what we want done. You don't know all the context, so don't be overly prescriptive in your prompt; just tell it in basic terms what we want done.

---

## Assistant

Here is a high-level breakdown of what we're setting up:

**Install qbit_manage:** A Python-based automation tool that runs alongside qBittorrent.

**Enable qBittorrent WebUI:** Provides the API local tools need to read and update your torrents.

**Configure Tracker-Based Auto-Tagging:** Sets up rules in `config.yml` to automatically assign tags based on the tracker domain.

**Configure Automated File Management:** Sets up rules in `config.yml` to route media to your CloudMounter drive based on those tags or categories.

**Agent-Friendly Config Setup:** Ensures all behavior lives in a single, plain-text YAML file so an agent can easily adjust or extend rules in the future.

Here is a prompt you can feed directly to an agent or coding tool:

Plaintext

```
Help me set up qbit_manage for qBittorrent on macOS to automate tagging and file organization.

Requirements:
1. Ensure qBittorrent WebUI is enabled so qbit_manage can communicate with it locally.
2. Install qbit_manage (via Python/pip, Homebrew, or Docker, whichever is cleanest for macOS).
3. Create a clean, well-commented YAML configuration file (`config.yml`) that establishes:
   - Tracker-to-tag rules (assign specific tags automatically based on tracker domains).
   - Category and directory path rules (move completed downloads to specific destination directories, including CloudMounter mount points, based on their tags/categories).
4. Keep the configuration structured and straightforward so future rules can easily be edited or appended in plain text.
5. Set up a simple method (like a local cron job or background script) to run qbit_manage periodically.

```

---
