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
- [ ] Establish Master PROJECT_BOARD.md and active preflight state hydration [project:: ai-os] [assignee:: agent] [due:: 2026-08-15]
- [ ] Fix gemini-thread-sync userscript connection on Safari [project:: gemini-thread-sync] [assignee:: agent]

---

## 📋 Backlog / To Do

- [ ] Transfer $1k from Scotiabank to Koho and back around noon to retain free Koho Essential [project:: personal] [assignee:: user]
- [ ] Present new Mounjaro savings card from Apple Wallet at Costco pharmacy [project:: personal] [assignee:: user]
- [ ] Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: user]
- [ ] Audit and run Wails thread-browser [project:: ai-os] [assignee:: agent]
- [ ] Implement system prompt injection in gemini-thread-sync [project:: gemini-thread-sync] [assignee:: agent]
- [ ] Fix Perplexity thread-sync userscript for Safari [project:: perplexity-thread-sync] [assignee:: agent]
- [ ] Map out thread review workflow [project:: ai-os] [assignee:: user]
- [ ] Build GLIC Safari sidecar (Tauri + gemini.google.com native webview) [project:: glic] [assignee:: agent]
- [ ] Fork Hermes WebUI + port agy tool-call/thoughts rendering from ai-os Tauri [project:: hermes-webui] [assignee:: agent]
- [ ] Build unified thread browser into Hermes WebUI fork [project:: thread-browser] [assignee:: agent]
- [ ] Warp/tmux auto-tab for agy MCP subagent visibility [project:: ai-os] [assignee:: agent]
- [ ] Resolve Safari CORS loopback block for gemini-thread-sync daemon [project:: gemini-thread-sync] [assignee:: agent]
- [ ] Port userscripts (Gemini + Perplexity) to Safari using Userscripts Safari Extension [project:: gemini-thread-sync] [assignee:: agent]
- [ ] Write Rust prototype for Safari window tracking bounds using core-graphics/cocoa [project:: glic] [assignee:: agent]
- [ ] Configure Tauri v2 multi-webview setup for Gemini and Perplexity toggles [project:: glic] [assignee:: agent]
- [ ] Initialize Hermes WebUI fork repository and configure styling overrides [project:: hermes-webui] [assignee:: agent]

---

## ✅ Completed

- [x] Clean up ai-os docs (active/archive subfolders) [project:: ai-os] [assignee:: agent]
- [x] Unload rogue Quartz ai-os-wiki LaunchAgent to stop CPU/memory runaway [project:: ai-os] [assignee:: agent]
- [x] Set up Obsidian Project Notes vault folder and index [project:: ai-os] [assignee:: agent]
- [x] Strategize and clean up global todo system [project:: ai-os] [assignee:: agent]

---

## 🏷️ Metadata Schema (For Agents & Automation)
Format: `- [ ] Task Description [project:: <project-id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`
- **`project`**: Project ID matching active repo or Obsidian note.
- **`assignee`**: `user` (for Matt) or `agent` (for AI agents).
- **`due`**: (Optional) Due date in `YYYY-MM-DD`.
