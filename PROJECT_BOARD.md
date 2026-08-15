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

- [ ] Replace Quartz with Docsify for ai-os-wiki knowledge base engine [project:: ai-os] [assignee:: agent] [due:: 2026-08-15]
- [ ] Fix gemini-thread-sync userscript connection & verify sync daemon [project:: gemini-thread-sync] [assignee:: agent]

---

## 📋 Active Engineering Backlog

- [ ] Build unified Thread Browser (as extension of ai-os companion app) [project:: thread-browser] [assignee:: agent]
- [ ] Fork Hermes WebUI for custom UI controls & unconstrained agent view [project:: hermes-webui] [assignee:: agent]
- [ ] Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: agent]
- [ ] Fix Perplexity thread-sync userscript [project:: perplexity-thread-sync] [assignee:: agent]
- [ ] Implement system prompt injection helper in gemini-thread-sync [project:: gemini-thread-sync] [assignee:: agent]

---

## 📦 Archived / Deprecated Decisions

- `[DEPRECATED]` GLIC Safari sidecar Tauri app & Rust window tracker (Made irrelevant by Chrome migration)
- `[DEPRECATED]` Wails Go backend for thread-browser (Replaced by ai-os companion app)

---

## ✅ Completed

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
