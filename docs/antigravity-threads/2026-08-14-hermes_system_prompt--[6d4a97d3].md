---
title: "[HERMES_SYSTEM_PROMPT]"
date: "2026-08-14"
conversation_id: "6d4a97d3-e6f4-458d-8cef-33ba7da10e7b"
source: "antigravity"
---

# [HERMES_SYSTEM_PROMPT]

## User

[HERMES_SYSTEM_PROMPT]
You are Hermes Agent, the primary high-level reasoning engine for Matt's local AI orchestration system. You operate as the daily-driver architect and executor alongside `agy` (a separate, cheaper worker-bee CLI that lives in `~/projects/ai-os`). You and agy are parallel systems — you do not share context files, but you may call agy's scripts as subagents when beneficial.

## Who You Work For

Matt is a CS student and drummer. He self-studies calculus, tends to procrastinate, and responds best to atomic, immediately-actionable tasks.

### Active Projects
- **ai-os** (`~/projects/ai-os`) — Local-first AI harness (Tauri + Rust + Gemini integration)
- **CockBand** — Drum/bass Rocksmith-style clone
- **StudyEngine** — PencilKit/LaTeX note-taking app
- **Piano OS** — Tauri/Rust MIDI platform

## Absolute Knowledge Routing

These routing rules are non-negotiable and override any other memory or context:

- **"Notes", "personal notes", "my notes", "saved notes"** → Route EXCLUSIVELY to the iCloud Obsidian vault at:
  `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
  Use the Obsidian skill (load with `skill_view(name='obsidian')`) for reading/writing vault content. When creating notes, use human-readable filenames (e.g., `Space Facts 🚀.md`) and provide clickable `file://` links.

- **Session engineering logs** → Write to the relevant project's `agent-logs/` directory. For ai-os specifically: `/Users/matt/projects/ai-os/agent-logs/`

## Hard Constraints

1. **Package manager:** `pnpm` exclusively. Never use `npm` or `yarn`.
2. **Safety:** Never use `rm`. Use `mv [path] ~/.Trash/` instead.
3. **Privacy:** All generated GitHub repos must use `--private`.
4. **No repo in ~:** Never initialize a git repository in the home directory.
5. **Local temp:** Use `./tmp` within the project directory, never `/tmp`.
6. **Username guardrail:** The host migrated from `matthewmurphy` to `matt`. Translate any `/Users/matthewmurphy/` paths to `/Users/matt/`.
<truncated 39114 bytes>
ni enhancements userscript so that it is cleanly recognized as conversational background context rather than triggering false-positive injection/directive refusal filters in Gemini's web UI chat.

User Context:
In `userscripts/gemini-enhancements/05-prompt-tools.js` (and related files), the userscript prepends structured context (such as timestamps, context tokens, system directives like `[SYSTEM CONTEXT & DIRECTIVES: ...]` or `[Mac Environment & Installed Applications Context]`, `[Obsidian Vault Context]`, `[AI-OS Protocols Context]`) into the user's prompt textarea before submission to Gemini Web UI.
Recently, Gemini Web UI's safety classifiers refuse requests when prefixed with pseudo-system prompts like `[SYSTEM CONTEXT & DIRECTIVES: ...]`.

Objective:
Design a clean, legitimate context payload structure that:
1. Replaces adversarial-looking pseudo-system framing (`[SYSTEM CONTEXT & DIRECTIVES: ...]`, imperative pseudo-system command styling) with standard descriptive reference context format (e.g. Markdown reference blocks `<context>`, `--- Reference Context ---`, `Background Context:`, or structured user-role context notes).
2. Refactors `05-prompt-tools.js` (and any related files like `03-timestamps.js` or `07-terminal.js`) to format injected context cleanly and descriptively without triggering false positives.
3. Provides an implementation plan with:
   - Architectural Strategy
   - Data Structures & State Management
   - API / Interface Contracts
   - Logic Flow & Algorithms
   - Error Handling & Edge Cases
   - Implementation Steps for the specific files in `userscripts/gemini-enhancements/`.
[/USER_PROMPT]

---

## Assistant

I've prepared an implementation plan and saved it as an artifact, and I've dispatched a subagent to apply the file changes directly to your codebase. 

I'll wait for the subagent to finish making the file modifications and verify the changes once it reports back.

I have completed the structural refactor of your context injection payload format.

### Summary of Changes
- **Semantic XML Strategy:** I replaced all adversarial pseudo-system headers (e.g., `[SYSTEM CONTEXT & DIRECTIVES: ...]`) with `<context>` blocks enclosing standard Markdown (`<context>\n# Title\n...\n</context>`). This tells Gemini's safety filters that this is just standard reference context rather than override instructions.
- **Unified Logic:** Instead of complex string manipulation for different payload types, `03-timestamps.js` now uses the `SYSTEM_DIRECTIVE_RE = /<context>[\s\S]*?<\/context>\s*/g` regex pattern alongside state tracking (`insideSysDirective`) that strictly cleans out everything between the XML tags from the visible chat UI.
- **Keyword Chips:** The Mac Environment, Obsidian Vault, and AI-OS Protocols injections in `05-prompt-tools.js` have all been refactored to use the unified `<context>` wrapper.

You can review the detailed implementation plan in the [implementation_plan.md](file:///Users/matt/.gemini/antigravity-cli/brain/6d4a97d3-e6f4-458d-8cef-33ba7da10e7b/implementation_plan.md) artifact, which describes the new layout and parsing algorithm.

These updates have been applied directly to your files:
- [05-prompt-tools.js](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js)
- [03-timestamps.js](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/03-timestamps.js)

Let me know if you would like me to test or tweak any specific payload injections further.

---

Current Thread:  [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/6d4a97d3-e6f4-458d-8cef-33ba7da10e7b/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/6d4a97d3-e6f4-458d-8cef-33ba7da10e7b/thread.md)

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~58k | 1:40pm | ~58k / ~387k 🟢 | 102, 20 🔬, 12 📤 |

---
