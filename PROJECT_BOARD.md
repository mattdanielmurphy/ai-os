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
- [ ] Fix gemini-thread-sync userscript connection on Safari & complete Userscripts port [project:: gemini-thread-sync] [assignee:: agent]

---

## 📋 Active Engineering Backlog

- [ ] Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: agent]
- [ ] Fix Perplexity thread-sync userscript for Safari [project:: perplexity-thread-sync] [assignee:: agent]
- [ ] Implement system prompt injection helper in gemini-thread-sync [project:: gemini-thread-sync] [assignee:: agent]

---

## 👤 Personal Reminders (Synced to Apple Reminders)

- [ ] Transfer $1k from Scotiabank to Koho and back around noon [project:: personal] [assignee:: user] [due:: 2026-08-15 12:00] (📲 In Apple Reminders)
- [ ] Present new Mounjaro savings card from Apple Wallet at Costco pharmacy [project:: personal] [assignee:: user] [due:: 2026-08-16 12:00] (📲 In Apple Reminders)

---

## 📦 Archived / Deprecated Decisions

- `[DEPRECATED]` Audit and run Wails thread-browser (Superseded by Antigravity / Hermes web & CLI tools)
- `[DEPRECATED]` GLIC Safari sidecar Tauri app & Rust window tracker (Superseded by native Antigravity IDE & Hammerspoon webview)
- `[DEPRECATED]` Fork Hermes WebUI repository (Superseded by Hermes Gateway API + direct transcript ingestion)
- `[COMPLETED/SUPERSEDED]` Warp/tmux auto-tab script (Superseded by agymcp background tmux sessions)

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
