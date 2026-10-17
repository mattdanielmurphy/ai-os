---
title: "Master Project Board"
updated: 2026-10-17
type: project-board
---

# 📌 Master Project Board

> **Board file**: [PROJECT_BOARD.md](/Users/matt/projects/ai-os/PROJECT_BOARD.md)

Central task registry across all projects and active coding threads. Automatically hydrated during session pre-flight.

---

## 🚀 In Progress

- [ ] Make ai-os work well for Claude (plan: docs/handoffs/2026-10-17_claude-onboarding.md) [project:: ai-os] [assignee:: agent]
- [ ] Verify gemini-thread-sync userscript & sync daemon (new Gemini threads were landing in Hermes DB on 2026-10-17, so it may already work) [project:: gemini-thread-sync] [assignee:: agent]

---

## 🤖 ai-os → Claude migration (from 2026-10-17 onboarding handoff)

- [ ] Migrate old threads off Hermes: export every thread to plain markdown (one file per thread), add a rebuildable search index, point `scripts/threads.py` at it, then shelve Hermes [project:: ai-os] [assignee:: agent]
- [ ] Add Codex sessions and a ChatGPT data export to the thread archive (Matt: request ChatGPT export) [project:: ai-os] [assignee:: user]
- [ ] Import ChatGPT/Gemini saved memories into Claude memory [project:: ai-os] [assignee:: user]
- [ ] Decide on scrubbing PII from git history and docs/antigravity-threads (irreversible force push) [project:: ai-os] [assignee:: user]
- [ ] Rules rewrite: shelve agy/query_aios/Perplexity/HTML-formatting rules; rebuild GEMINI/HERMES/Codex outputs [project:: ai-os] [assignee:: agent]
- [ ] preflight v2: per-step timings (JSONL), honest statuses, `report` command, drop dead steps, under 1s [project:: ai-os] [assignee:: agent]
- [ ] Create visible `shelf/` (README per item + INDEX.md); first residents: agy, query_aios, Perplexity, Tauri GUI [project:: ai-os] [assignee:: agent]
- [ ] Cleanup pass (stale branches, `.agy-mcp/worktrees`, tmp/, .bak files); rewrite README.md and todo.md as a current map [project:: ai-os] [assignee:: agent]
- [ ] Empty `ai-os/_to_delete/` (4.6 GB) into Trash [project:: ai-os] [assignee:: user]
- [ ] Thread-size awareness: nudge + `/handoff` skill that writes docs/handoffs/ files [project:: ai-os] [assignee:: agent]
- [ ] Review fell-through-the-cracks ideas (docs/ideas, parking-lot, best-ideas, VISION) → revive / shelve / drop list [project:: ai-os] [assignee:: agent]
- [ ] Set up Claude.app projects list (clarify: Chat sidebar Projects vs Code folders) [project:: ai-os] [assignee:: user]
- [ ] Fix Claude CLI default model (settings point at unavailable deepseek-v4-flash) [project:: ai-os] [assignee:: agent]
- [ ] Decide whether Mem0 memory (Qdrant in ~/.hermes) stays, given the move off Hermes [project:: ai-os-memory] [assignee:: user]

---

## 📋 Active Engineering Backlog

- [ ] 🔥 **HIGH PRIORITY**: Migrate personal Obsidian LLM Wiki knowledge base into Mem0 database for semantic retrieval [project:: ai-os-memory] [assignee:: agent]
- [ ] 🔥 **HIGH PRIORITY**: Harvest durable insights, patterns, and decisions from massive agent thread history transcripts into Mem0 [project:: ai-os-memory] [assignee:: agent]
- [ ] Investigate and eliminate remaining keypress/release CSS transition blur and WebKit redrawing in QWERTY HUD [project:: qwerty-midi-hammerspoon] [assignee:: agent]
- [ ] Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: agent]
- [ ] Explore a Bartender replacement or a custom expandable menu-bar controls window that exposes app menu-bar actions [project:: menu-bar-controls] [assignee:: user]
- [ ] Thread Browser UI over the new markdown thread archive (was: extension of query-aios companion, now shelved) [project:: thread-browser] [assignee:: agent]
- [ ] Implement system prompt injection helper in gemini-thread-sync [project:: gemini-thread-sync] [assignee:: agent]
- [ ] Automate adding Apple Music recommendations to the user’s library from deterministic native Apple Music links [project:: music-cross-linker] [assignee:: agent] [due:: 2026-09-29]
- [ ] Automate creating named Apple Music playlists from curated recommendation sets [project:: music-cross-linker] [assignee:: agent] [due:: 2026-09-29]

---

## 📦 Archived / Deprecated Decisions

- `[SHELVED 2026-10-17]` query_aios investigation (query_aios paused; revive from shelf)
- `[SHELVED 2026-10-17]` agy quota check fix (Antigravity trial ended)
- `[SHELVED 2026-10-17]` Hermes WebUI fork (moving off Hermes)
- `[SHELVED 2026-10-17]` Perplexity thread-sync userscript (Perplexity removed)

- `[DEPRECATED]` GLIC Safari sidecar Tauri app & Rust window tracker (Made irrelevant by Chrome migration)
- `[DEPRECATED]` Wails Go backend for thread-browser (Replaced by ai-os companion app)
- `[DEPRECATED]` Quartz/Docsify ai-os-wiki web server (Decommissioned in favor of direct Obsidian vault)

---

## ✅ Completed

- [x] Automatically continue morning FSRS reviews after the minimum and keep only the latest reminder nudge visible [project:: proactive-assistant] [assignee:: agent] [due:: 2026-10-11]
- [x] Implement Dynamic Codex Hook-Based Policy Engine (classifier, tool_guard, rollout/rollback, 30 tests) [project:: ai-os] [assignee:: agent] [due:: 2026-09-27]
- [x] Add AI-OS Controls menu actions to reveal and hide the Perplexity/Gemini companion windows [project:: query-aios-controls] [assignee:: agent]
- [x] Add forallx chapters 1–15 FSRS quizzes and repeat unanswered morning Telegram check-ins every 15 minutes [project:: proactive-assistant] [assignee:: agent] [due:: 2026-09-24]
- [x] Deploy Hermes WebUI with Gemini Flash orchestration, agy cost delegation, and Mac-to-VPS Caddy failover [project:: hermes-webui] [assignee:: agent] [due:: 2026-09-15]
- [x] Implement Proactive Executive Assistant Service with FSRS, Habit Bridge, and Context Gate [project:: proactive-assistant] [assignee:: agent] [due:: 2026-09-13]
- [x] Decommission redundant ai-os-wiki web server and prune deprecated sub-apps [project:: ai-os] [assignee:: agent]
- [x] Establish Master PROJECT_BOARD.md and active preflight state hydration [project:: ai-os] [assignee:: agent]
- [x] Unload rogue Quartz ai-os-wiki LaunchAgent to stop CPU/memory runaway [project:: ai-os] [assignee:: agent]
- [x] Clean up ai-os docs (active/archive subfolders) [project:: ai-os] [assignee:: agent]
- [x] Set up Obsidian Project Notes vault folder and index [project:: ai-os] [assignee:: agent]
- [x] Strategize and clean up global todo system [project:: ai-os] [assignee:: agent]

---

## 🏷️ Metadata Schema (For Agents & Automation)
Format: `- [ ] Task Description [project:: <project-id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`
- **`project`**: Project ID matching active repo or Obsidian note.
- **`assignee`**: `user` (for Matt) or `agent` (for AI agents).
- **`due`**: (Optional) Due date in `YYYY-MM-DD`.
