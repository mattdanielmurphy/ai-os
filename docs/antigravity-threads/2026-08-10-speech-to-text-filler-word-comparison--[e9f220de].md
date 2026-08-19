---
title: "Speech-to-Text Filler Word Comparison"
date: "2026-08-10"
conversation_id: "e9f220de08c858b2"
source: "antigravity"
---

# Speech-to-Text Filler Word Comparison

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-09 23:30 MDT-6] [context to this point is 0] I kind of can't believe this is what spokenly gives me:

`uh, you don't have to look at the diff straight away, um, but I would say you could probably take in a very detailed summary of what Gemini does, and then you can learn from it, um, and Gemini shares your memory, et cetera, and rules, so you're basically like a, a watcher, a high level watcher of what Gemini does with, uh, AGY. ` why the fuck would I want uhs and ums?

should I just use superwhisper instead? is that better?

---

## Assistant

The frustration is completely valid. Having to manually scrub vocal stutters and filler words out of transcription defeats the entire point of using speech-to-text.

**Yes, switching to Superwhisper (or adjusting your current workflow) will give you a vastly better experience.**

Superwhisper vs. Spokenly

Superwhisper is generally considered superior for power users on macOS for a few reasons:

Feature	Spokenly	Superwhisper
**Filler Word Stripping**	Often leaves raw acoustic transcripts (`uh`, `um`) depending on model selection.	**Built-in text cleanup.** Strips `uh`, `um`, repeated words, and false starts automatically.
**Engine / Models**	Uses Whisper variants or basic API endpoints.	Leverages local Whisper, **Claude**, and custom LLM passes to post-process text.
**Custom Rules**	Limited post-processing.	Supports **Custom Prompts** (e.g., "Format as Markdown," "Remove filler words," "Fix jargon").
**Local Processing**	Can be slow or resource-heavy depending on configuration.	High-performance CoreML/GPU optimization on Mac.
Why Superwhisper Solves This

Superwhisper gives you granular control over **LLM post-processing modes**:

**Standard / Precise Mode:** Runs local Whisper models (like `Whisper Large v3` or `Distil-Whisper`) which natively handle acoustic precision, but can include filler if selected strictly.

**Auto-Format / Smart Mode:** Superwhisper routes the raw Whisper text through a fast LLM pass (local or cloud) using a prompt like:

*"Clean up filler words, fix grammar, retain exact intent and vocabulary, and do not paraphrase unnecessarily."*

This gives you perfectly clean prose while keeping every technical term intact.

What You Should Do
Option A: Try Superwhisper (Recommended)

**Download Superwhisper.**

Set your default mode to **Pro / Smart** or create a custom preset with the instruction: `Remove all filler words (uh, um, like, you know) and clean up false starts.`

Result: You get immediate, production-ready text pasted right into your editor or prompt bar.

Option B: Fix It in Spokenly First (If you want to test before switching)

If you're using Spokenly with local Whisper models:

Check if you are running the **Tiny** or **Base** model. Smaller Whisper models tend to transcribe every literal sound.

Upgrade to **Whisper Large v3** or **Distil-Whisper Turbo**, which are significantly better at naturally omitting disfluencies during decoding.

---
