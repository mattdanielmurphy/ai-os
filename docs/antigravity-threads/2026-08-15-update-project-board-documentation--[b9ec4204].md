---
title: "Update Project Board Documentation"
date: "2026-08-15"
conversation_id: "b9ec4204-0f78-4c1e-9020-33abd1004207"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please update `/Users/matt/projects/ai-os/PROJECT_BOARD.md` to incorporate Matt's feedback:

1. Restore Thread Browser to Active Engineering Backlog, updated as an extension of the `ai-os` companion app (not Wails).
2. Restore Forking Hermes WebUI to Active Engineering Backlog (for full UI control and overcoming Antigravity limits).
3. Remove the `👤 Personal Reminders` section completely (they are now in Apple Reminders).
4. In Archived/Deprecated, note that GLIC Safari sidecar was made irrelevant by switching back to Chrome.

Here is the exact updated content to write to `/Users/matt/projects/ai-os/PROJECT_BOARD.md`:

```markdown

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
```</span>



<span title="Responded at 9:41am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The `/Users/matt/projects/ai-os/PROJECT_BOARD.md` has been successfully updated according to your instructions.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~35k / ~410k 🟢 (optimal) | 4:40am | 105 ❓, 16 📤 |

</span>

</span>