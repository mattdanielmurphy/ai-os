---
title: "Brainstorming Media Context AI Names"
date: "2026-07-29"
conversation_id: "0a6c419a308389d9"
source: "antigravity"
---

# Brainstorming Media Context AI Names

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-07-28 21:38 MDT-6] [context to this point is 0] Act as a technical sounding board. I have an idea for a new feature/project, and we need to brainstorm.




Do not try to build it, write code, or structure a final plan yet. Your goal is to help me explore the edges of this idea. Ask me clarifying questions about the core problem, the ideal user experience, and potential pitfalls. Let's keep the conversation fluid and conceptual until I tell you we are ready to lock in a plan.




Here is my initial thought:













I want to make a simple app that monitors my IINA playback and, if it's a TV episode, loads up the context of the season arc up to that point to answer questions about the show. They'll have to extract the subtitles and know the exact playback position, and make sure not to mention anything about what happens after that playback position and not spoil anything. Anything that's happened already in the show though is free game.




And of course this will have to be sent to an agent.




And it'd work for movies as well of course.




And it would provide the current frame of the show and maybe even in an ideal universe it could describe exactly what happened in the show in the past few minutes, I guess? I don't know how you would do that.




Anyway, all I really need from you is a good short name for this project.




Like, `media-context-ai` is a terrible name. Can you give some other options?

---

## Assistant

Here are a few naming angles, depending on the vibe you want:

Narrative & Film Terms

**`diegesis`** (or **`diegetic`**) — Refers to everything that exists within the world of the story up to that specific moment.

**`subtext`** — Clean, short, single-word.

**`continuity`** — Fits the exact goal of maintaining narrative awareness without leapfrogging the timeline.

Technical & Playback Concepts

**`playhead`** — Direct reference to tracking the precise timecode position.

**`mark-in`** — Video editing terminology for the exact starting/current boundary point.

**`backchannel`** — Sounds like an internal commentary or query pipeline running alongside the main feed.

Short & Conceptual

**`lorebound`** — Bound strictly to the lore established up to the current frame.

**`scenewise`** — Practical and conversational.

**`frameguard`** — Highlights both the visual feed element and the strict anti-spoiler boundary.

Do any of those directions (film terminology, playback metaphors, or descriptive hybrids) hit closer to what you're imagining?

---

## User

[2026-07-28 21:39 MDT-6] [context to this point is 315] Sorry, these are like product names. I just need a utility name for the project folder, one that's actually descriptive.

---

## Assistant

Here are some straightforward, descriptive utility-style options for the project directory:

**`iina-context-agent`** — Direct and explicitly states the host app, core data layer, and execution model.

**`episode-context-agent`** — Focuses specifically on the TV/narrative scoping.

**`iina-spoiler-guard`** — Highlights the strict timeline boundary aspect.

**`playhead-context-agent`** — Accurate to the underlying mechanics (tracking timecode to bound the prompt context).

**`video-context-agent`** — Clean, general, and covers both movies and show episodes.

**`iina-media-agent`** — Compact while keeping the tool target obvious.

`iina-context-agent` or `playhead-context-agent` are probably the most accurate to what the process actually does day-to-day.

---

## User

[2026-07-28 21:41 MDT-6] [context to this point is 541] yeah I thought of using iina in the name and that makes sense, but for some reason I wanted to make my project not be tied to iina necessarily, even though for now it's all we'll support

---

## Assistant

That makes sense—decoupling the utility name from the specific player frontend keeps it clean if you ever swap playback sources later.

Here are descriptive options focused on the generic playback or media layer:

**`playhead-context-agent`** — Focuses on the core mechanic: pulling context relative to the active playback timestamp.

**`video-context-agent`** — Broad, clear, and leaves room for any media player.

**`episode-context-agent`** — Emphasizes the narrative scoping side of the tool.

**`media-spoiler-guard`** — Highlights the safety-boundary aspect of the context engine.

**`player-context-agent`** — Generic enough to wrap around IINA, MPV, or VLC without changing directory names later.

`playhead-context-agent` or `video-context-agent` both keep it fully agnostic while describing the utility's exact job.

---

## User

[2026-07-28 21:42 MDT-6] [context to this point is 787] yeah ok.

Can you give me back exactly what I wrote but just formatted better? Don't remove anything

---

## Assistant

Markdown

```
I want to make a simple app that monitors my IINA playback and, if it's a TV episode, loads up the context of the season arc up to that point to answer questions about the show. 

### Core Mechanics & Requirements
* **Subtitle & Position Extraction:** They'll have to extract the subtitles and know the exact playback position.
* **Strict Anti-Spoiler Guardrail:** Make sure not to mention anything about what happens after that playback position and not spoil anything. Anything that's happened already in the show though is free game.
* **Agent Integration:** And of course this will have to be sent to an agent.
* **Format Support:** And it'd work for movies as well of course.
* **Visual & Scene Context:** And it would provide the current frame of the show and maybe even in an ideal universe it could describe exactly what happened in the show in the past few minutes, I guess? I don't know how you would do that.

Anyway, all I really need from you is a good short name for this project.

Like, `media-context-ai` is a terrible name. Can you give some other options?

```

---

## User

[2026-07-28 21:43 MDT-6] [context to this point is 1159] ok so I just want a description of the app now; we've got the name.

So based on this, give me an app description

---

## Assistant

Here is a clear, functional description based on your requirements:

**Project Overview**

An intelligent, context-aware media assistant that hooks into local video playback (starting with IINA) to act as a real-time sounding board for movies and TV shows. By tracking your exact playhead position and parsing available subtitles up to that frame, it builds a strictly bounded historical context window for an AI agent.

**Key Features & Architecture**

**Time-Gated Context Engine:** Automatically extracts subtitles and syncs with the current timestamp to ingest character arcs, plot points, and dialogue leading up to the exact moment you're watching.

**Strict Anti-Spoiler Guardrail:** Enforces a hard boundary at the active playhead. The agent can freely reference, analyze, and explain anything that has already occurred, while completely blocking future narrative developments, twists, or season-arc outcomes.

**Visual Frame Capture:** Pulls the active video frame alongside the text query, allowing the agent to analyze what’s visually on screen.

**Short-Term Scene Awareness:** Explores rolling short-term scene summaries (tracking the last few minutes of screen activity) to answer targeted questions about recent dialogue or fast-paced actions.

**Player-Agnostic Design:** Built around generic playback monitoring, allowing the underlying hooks to expand beyond IINA to other local media players.

---

## User

[2026-07-28 21:45 MDT-6] [context to this point is 1600] ok great. Now if I were to bootstrap this project, what do you suggest I would make my prompt?

There's lots of system rules that should be loaded when I ask my agent to do this, but do you have any ideas as to a better prompt than literally just saying:

```Build this project:

<your Project Overview>```

---

## Assistant

When bootstrapping a new project with an AI coding agent, giving it just a generic feature description usually leads to over-engineered boilerplate, unwanted npm packages, or unneeded UI frameworks.

To get clean, actionable code on the first pass, a good bootstrap prompt should define **boundaries, initial file structure, tech stack, and step zero**.

Here is a structured, production-ready bootstrap prompt you can use:

Markdown

```
# Role & Task
You are building `video-context-agent`, a local macOS utility that monitors active video playback, extracts current timecode and subtitle context up to that point, and exposes an anti-spoiler context payload for an AI agent.

# Context & Requirements
- **Core Purpose:** Track video playhead (starting with IINA via WebSocket/IPC or AppleScript), extract embedded or sidecar subtitles up to the current timestamp, capture the active video frame, and assemble a time-bounded context window.
- **Strict Boundary Rule:** The extracted context must NEVER contain narrative data, subtitles, or timestamps past the current playhead.

# Tech Stack & Guidelines
- **Runtime & Manager:** Bun / TypeScript (macOS local utility)
- **Local Tooling:** Use native CLI binaries (`mpv` IPC / `ffmpeg` / `mpv-cmd` / AppleScript) where appropriate. Keep dependencies minimal.
- **Architecture Goal:** Modular design separating Player Hook (`iina.ts`), Subtitle Parser (`subtitles.ts`), Frame Extractor (`frame.ts`), and Prompt Assembler (`context.ts`).

# Initial Objective (Phase 1)
Do not build a full UI or end-to-end agent workflow yet. Focus purely on the core execution harness:

1. Draft the initial project structure in Bun.
2. Implement a minimal proof-of-concept script that:
   - Queries IINA for the current file path and playhead position (`time-pos`).
   - Parses the associated subtitle file up to `time-pos`.
   - Logs the compiled context payload to `stdout`.

Provide the step-by-step file structure and code to get Phase 1 running.

```

Why this structure works well:

**Constrains the scope immediately:** It forces the agent to build *just* the data extraction pipe first (Phase 1) rather than hallucinating a whole full-stack app.

**Sets local constraints:** Specifies Bun and native macOS CLI utilities right away so it doesn't default to heavy node modules.

**Defines clear modular boundaries:** Keeps the player connection separated from the subtitle parser so swapping IINA for MPV later requires changing only one file.

---

## User

[2026-07-28 21:49 MDT-6] [context to this point is 2419] please rewrite this prompt to be more detailed, and make sure it's not recommending anything bad.

---

## Assistant

Here is a more detailed bootstrap prompt that avoids the common pitfalls (like using slow AppleScript or inefficiently extracting subtitles on every single query).

By forcing the agent to use IINA’s underlying `mpv` IPC socket and caching the subtitles to `./tmp`, you avoid terrible performance and get exact millisecond accuracy.

Markdown

```
# Role & Task
You are an expert macOS systems developer building `video-context-agent`. This local utility monitors active video playback, extracts exact timecode and subtitle context up to the current frame, and formats a strict, anti-spoiler context payload for an AI agent. 

# Technical Stack & Constraints
- **Environment:** macOS exclusively.
- **Package Manager:** Bun (strict). Do not use npm or pnpm.
- **Language:** TypeScript.
- **File Management:** Use `./tmp/` for any temporary file extraction, caching, or frame storage. Do not use `rm` for file removal; execute safe deletion by moving files to `~/.Trash/`.
- **Output Style:** Keep your code modular and concise. Do not write a massive monolithic script, and avoid dumping unrequested boilerplate.

# Core Mechanisms & Best Practices (Strictly Enforced)
- **Player Hook (No AppleScript):** Do not use AppleScript; it is too slow and brittle for exact millisecond timecodes. Instead, interface with IINA via its underlying `mpv` IPC socket (which can be enabled via IINA's advanced settings, e.g., `--input-ipc-server=/tmp/iina-socket`).
- **Subtitle Extraction (Cache, Don't Re-parse):** Do not run `ffmpeg` to parse embedded subtitles from massive video files on every single query. The system should detect when a new file plays, extract the subtitle track *once* to `./tmp/`, and parse that cached file for subsequent queries. 
- **Frame Capture:** Utilize `mpv`'s native IPC `screenshot-to-file` command to instantly grab the current frame directly from the player's buffer, avoiding slow `ffmpeg` seeking operations.
- **Strict Anti-Spoiler Boundary:** The subtitle parsing module must strictly filter all dialogue against the current `time-pos`. It must NEVER expose text, metadata, or timestamps past the active playhead to the final payload.

# Initial Objective (Phase 1)
Do not build the LLM integration, agent logic, or attempt to write the entire app at once. Focus purely on the local data extraction harness:

1. Scaffold the initial Bun/TypeScript file structure.
2. Write a minimal IPC connection script that connects to the `/tmp/iina-socket` and successfully polls the current playing file path and exact `time-pos`.
3. Write the subtitle caching logic that detects the active subtitle track, dumps it to `./tmp/`, and filters the text up to the polled `time-pos`.

Output the Phase 1 project structure and the exact code required to get these data hooks working.

```

---
