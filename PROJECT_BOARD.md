---
title: "Master Project Board"
updated: 2026-08-15
type: project-board
---

# 📌 Master Project Board

> **Quick Actions**: [Open in Zed](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) | [Open in Obsidian](obsidian://open?vault=Personal&file=Development%2FProject%20Notes%2FGlobal%20Todos) | [Open in Finder](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

Central task registry across all projects and active coding threads. Automatically hydrated during session pre-flight.

---

## 🚀 In Progress

- [ ] Fix gemini-thread-sync userscript connection & verify sync daemon [project:: gemini-thread-sync] [assignee:: agent]

---

## 📋 Active Engineering Backlog

- [ ] 🔥 **HIGH PRIORITY**: Migrate personal Obsidian LLM Wiki knowledge base into Mem0 database for semantic retrieval [project:: ai-os-memory] [assignee:: agent]
- [ ] 🔥 **HIGH PRIORITY**: Harvest durable insights, patterns, and decisions from massive agent thread history transcripts into Mem0 [project:: ai-os-memory] [assignee:: agent]
- [ ] Build unified Thread Browser (as extension of ai-os companion app) [project:: thread-browser] [assignee:: agent]
- [ ] Fork Hermes WebUI for custom UI controls & unconstrained agent view [project:: hermes-webui] [assignee:: agent]
- [ ] Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: agent]
- [ ] Fix Perplexity thread-sync userscript [project:: perplexity-thread-sync] [assignee:: agent]
- [ ] Implement system prompt injection helper in gemini-thread-sync [project:: gemini-thread-sync] [assignee:: agent]
- [ ] Automate adding Apple Music recommendations to the user’s library from deterministic native Apple Music links [project:: music-cross-linker] [assignee:: agent] [due:: 2026-09-29]
- [ ] Automate creating named Apple Music playlists from curated recommendation sets [project:: music-cross-linker] [assignee:: agent] [due:: 2026-09-29]

---

## 📦 Archived / Deprecated Decisions

- `[DEPRECATED]` GLIC Safari sidecar Tauri app & Rust window tracker (Made irrelevant by Chrome migration)
- `[DEPRECATED]` Wails Go backend for thread-browser (Replaced by ai-os companion app)
- `[DEPRECATED]` Quartz/Docsify ai-os-wiki web server (Decommissioned in favor of direct Obsidian vault)

---

## ✅ Completed

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
