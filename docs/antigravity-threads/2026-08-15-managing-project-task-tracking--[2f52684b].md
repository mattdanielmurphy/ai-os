---
title: "Managing Project Task Tracking"
date: "2026-08-15"
conversation_id: "2f52684b-97d4-4941-be1f-e51c80942048"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">AND they'll reference it to me too?</span>



<span title="Responded at 9:43am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

**Yes!** The system directive explicitly mandates this for all agents:

> **Surfacing Requirement**: Agents **MUST** surface clickable links (`[PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)`) with 1-click action links whenever initiating new features or concluding tasks.

---

### What You Will See in Agent Responses

Whenever an agent starts a task or finishes working on a feature, they are required to include the board reference in their response:

```markdown
---

### 📌 Master Project Board
- 📝 **Board Status**: Updated task to `[IN_PROGRESS]` / `[COMPLETED]`
- 🔗 **View Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)
- ⚡ **1-Click Launch in Zed**: [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- 📓 **1-Click Open in Obsidian**: [Open in Obsidian](obsidian://open?vault=Personal&file=Development%2FProject%20Notes%2FGlobal%20Todos)
```

### Why This Keeps It Front of Mind
1. **On Session Start**: `preflight.py` prints the active tasks into the session banner automatically.
2. **On Task Completion**: The agent reports what was changed, checks off the item on the board, and provides the 1-click launch links right in the chat response.
3. **In Your Obsidian Vault**: [Global Todos.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Global%20Todos.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) is updated simultaneously via the symlink.

---

- 📝 **Master Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)
- ⚡ **Open in Zed**: [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

---

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Agents know about this and will use it proactive?</span>



<span title="Responded at 9:43am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Please wait while `AG_CONTEXT.md` is updated.

**Yes, absolutely.** The system is architected across three distinct reinforcement layers so that every agent—regardless of platform or model—is forced to know about and proactively interact with [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md):

---

### How Agents Are Wired to Use It Proactively

```
                         ┌──────────────────────────────────────┐
                         │   1. System Directives (Compiled)    │
                         │   GEMINI.md / CLAUDE.md / HERMES.md  │
                         └──────────────────┬───────────────────┘
                                            │
                                            ▼
                         ┌──────────────────────────────────────┐
                         │   2. Preflight Turn 1 Injection       │
                         │   preflight.py reads PROJECT_BOARD   │
                         └──────────────────┬───────────────────┘
                                            │
                                            ▼
                         ┌──────────────────────────────────────┐
                         │   3. Durable Context & Live Obsidian  │
                         │   AG_CONTEXT.md + Global Todos.md    │
                         └──────────────────────────────────────┘
```

### 1. Top-Tier System Rules (`GEMINI.md`, `CLAUDE.md`, `HERMES.md`)
The protocol has been compiled into the master instruction prompt for all agents via [build_rules.py](file:///Users/matt/projects/ai-os/scripts/build_rules.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/build_rules.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/build_rules.py):
> **Master Project Board Protocol**:
> - **Single Source of Truth**: Active multi-project backlog is maintained in `~/projects/ai-os/PROJECT_BOARD.md`.
> - **Hydration & Visibility**: `preflight.py` automatically hydrates in-progress and top backlog items at the start of every session.
> - **Surfacing Requirement**: Agents **MUST** surface clickable links (`[PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)`) with 1-click action links whenever initiating new features or concluding tasks.
> - **Task Schema**: Always format tasks as `- [ ] <description> [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`.

### 2. Automatic Turn 1 Preflight Injection
At the start of **any new conversation** in **any workspace**, the agent is required to run [preflight.py](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py). 

The output of `preflight.py` is defined as a **direct top-tier extension of the agent's system prompt**, which means the agent is immediately greeted with:
```
=== ACTIVE PROJECT BOARD (PROJECT_BOARD.md) ===
Path: file:///Users/matt/projects/ai-os/PROJECT_BOARD.md
Launch: http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md

🚀 In Progress:
  - Replace Quartz with Docsify for ai-os-wiki knowledge base engine [project:: ai-os] [assignee:: agent] [due:: 2026-08-15]
  - Fix gemini-thread-sync userscript connection & verify sync daemon [project:: gemini-thread-sync] [assignee:: agent]

📋 Top Backlog:
  - Build unified Thread Browser (as extension of ai-os companion app) [project:: thread-browser] [assignee:: agent]
  - Fork Hermes WebUI for custom UI controls & unconstrained agent view [project:: hermes-webui] [assignee:: agent]
  - Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets [project:: clipboard-snippet-app] [assignee:: agent]
  - Fix Perplexity thread-sync userscript [project:: perplexity-thread-sync] [assignee:: agent]
================================================
```
The agent starts every session knowing the exact global state without you needing to prompt or remind it.

### 3. Persistent Domain Context (`AG_CONTEXT.md`)
Added directly to [AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md#L42-L43) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/AG_CONTEXT.md%3A42%3A43) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/AG_CONTEXT.md) so any subagent or external worker doing context scans will treat updating the board as standard operational procedure.

### 4. Live Obsidian Two-Way Sync
Because [Global Todos.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Global%20Todos.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) in your Obsidian vault is symlinked to `PROJECT_BOARD.md`, anytime an agent updates a task status, it instantly reflects in your Obsidian Kanban view in real-time.

---

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`e7c1013`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, scripts/preflight.py and 3 other file(s)</div></details>

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">The user has left some comments on their files.

Please respond to the user and take whatever actions they ask you to.

Comments on the file file:///Users/matt/projects/ai-os/PROJECT_BOARD.md.

The user's comment was: these are all actually still things I want to do.
well, thread-browser won't be in Wails, it'll just be an extension of our newest ai-os "gemini-companion" (which is not a good name)
But anyway, I want to still have "Thread browser" as a thing.
The user commented between lines 1 and 1, which has the below contents.
```

[DEPRECATED] Audit and run Wails thread-browser (Superseded by Antigravity / Hermes web & CLI tools)
```

The user's comment was: this really was made irrelevant by the fact that I was able to switch back to Chrome
The user commented between lines 1 and 1, which has the below contents.
```

[DEPRECATED] GLIC Safari sidecar Tauri app & Rust window tracker (Superseded by native Antigravity IDE & Hammerspoon webview)
```

The user's comment was: still relevant, still think I want to do this to have ultimate control (limitations of Antigravity are annoying)
The user commented between lines 1 and 1, which has the below contents.
```

[DEPRECATED] Fork Hermes WebUI repository (Superseded by Hermes Gateway API + direct transcript ingestion)
```

The user's comment was: no need to show here
The user commented between lines 1 and 1, which has the below contents.
```

👤 Personal Reminders (Synced to Apple Reminders)
```

<USER_REQUEST>

</USER_REQUEST></span>



<span title="Responded at 9:40am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Please wait while the subagent updates `PROJECT_BOARD.md` to reflect your comments.

Please wait while the parser is updated.

All adjustments have been applied to [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) based on your comments:

---

### Summary of Changes

1. **Restored Active Initiatives**:
   - **Unified Thread Browser**: Re-added to the active backlog as an extension of the `ai-os` desktop companion app.
   - **Fork Hermes WebUI**: Re-added to the active backlog for unconstrained custom UI controls and bypassing Antigravity view limits.

2. **Cleaned Up Personal Reminders**:
   - The personal reminders section was completely removed from the board (now living cleanly in Apple Reminders).

3. **Archived / Deprecated Notes Updated**:
   - **GLIC Safari sidecar**: Explicitly marked as deprecated/obsolete due to switching back to Chrome.
   - **Wails Go backend**: Marked as replaced by the `ai-os` companion app.

4. **Verified Pre-Flight Hydration**:
   - Tested [preflight.py](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py) to ensure both **In Progress** and **Top Backlog** items display with 1-click links at the start of new threads.

---

### Active Board Overview

| Status | Task | Project ID |
| :--- | :--- | :--- |
| 🚀 **In Progress** | Replace Quartz with Docsify for `ai-os-wiki` knowledge base | `[project:: ai-os]` |
| 🚀 **In Progress** | Fix `gemini-thread-sync` userscript connection & verify daemon | `[project:: gemini-thread-sync]` |
| 📋 **Top Backlog** | Build unified Thread Browser (in `ai-os` companion app) | `[project:: thread-browser]` |
| 📋 **Top Backlog** | Fork Hermes WebUI for custom UI controls & agent view | `[project:: hermes-webui]` |
| 📋 **Top Backlog** | Build Clipboard History GUI App with frequency tracking & AI snippets | `[project:: clipboard-snippet-app]` |
| 📋 **Top Backlog** | Fix Perplexity thread-sync userscript | `[project:: perplexity-thread-sync]` |

---

- 📝 **Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)
- ⚡ **1-Click Launch in Zed**: [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

---

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`0765244`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, PROJECT_BOARD.md and 2 other file(s)</div></details>

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">identify which To Dos are irrelevant based on decisions made since they were added, and which ones are for ME personally rather than agents, and add them to Apple Reminders</span>



<span title="Responded at 9:34am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Please wait while the subagent updates `PROJECT_BOARD.md` to reflect the pruned items and Apple Reminders sync.

### Task Audit & Actions Taken

---

### 1. 🗑️ Irrelevant / Deprecated Tasks Identified & Archived
Based on architectural decisions made across recent threads, the following items were **superseded or deprecated**:

| Task | Reason for Deprecation |
| :--- | :--- |
| **Audit & run Wails thread-browser** | Abandoned in favor of Antigravity IDE, CLI tools, and lightweight web viewers. |
| **GLIC Safari sidecar (Tauri + Rust window tracker)** | Superseded by native Antigravity IDE layout and Hammerspoon floating webviews. |
| **Fork Hermes WebUI repository** | Superseded by Hermes Gateway HTTP API (`8642`) and background transcript extractors; no custom web fork needed. |
| **Warp/tmux auto-tab for subagents** | Superseded by `agymcp` background tmux daemon management. |

---

### 2. 📲 Personal To-Dos Synced to Apple Reminders
The following personal to-dos were identified, synced directly to **Apple Reminders** via the CLI, and tagged on the board:

1. **Transfer \$1k from Scotiabank to Koho and back**
   - **Due**: 2026-08-15 12:00
   - **Notes**: Retain free Koho Essential and avoid monthly fee.
   - **Status**: ✅ Added to Apple Reminders
2. **Present new Mounjaro savings card from Apple Wallet at Costco pharmacy**
   - **Due**: 2026-08-16 12:00
   - **Notes**: Show savings card from Apple Wallet at pharmacy drop-off/pickup.
   - **Status**: ✅ Added to Apple Reminders

---

### 3. 🚀 Cleaned Active Agent Priorities in [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

- **In Progress**:
  1. `Replace Quartz with Docsify for ai-os-wiki knowledge base engine` `[project:: ai-os]`
  2. `Fix gemini-thread-sync userscript connection on Safari & complete Userscripts port` `[project:: gemini-thread-sync]`
- **Top Backlog**:
  1. `Design & build Clipboard History GUI App with frequency tracking and AI auto-snippets` `[project:: clipboard-snippet-app]`
  2. `Fix Perplexity thread-sync userscript for Safari` `[project:: perplexity-thread-sync]`
  3. `Implement system prompt injection helper in gemini-thread-sync` `[project:: gemini-thread-sync]`

---

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`18cd1d3`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, apps/gemini-companion/src-tauri/src/proxy.rs and 3 other file(s)</div></details>

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">proceed</span>



<span title="Responded at 9:32am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Please wait while the subagent updates `PROJECT_BOARD.md`, the Obsidian symlink, `preflight.py`, and the system rules. I will finalize once the subagent reports back.

Please wait while the subagent updates `preflight.py` and verifies execution.

Please wait while the subagent updates `sync_skills.py`.

The **Master Project Board** system is now live and wired into your environment:

---

### What Was Set Up

1. **Master Board Established**:
   - Created [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) at the repository root.
   - Symlinked it directly to your Obsidian vault at [Global Todos.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Global%20Todos.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) so Obsidian Kanban boards and markdown editors remain in sync.

2. **Automatic Preflight Hydration**:
   - Updated [preflight.py](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py) to automatically extract and print `🚀 In Progress` and `📋 Top Backlog` items on Turn 1 of every session across all models.

3. **System Directive Persistence**:
   - Updated [.rules/agent_logs.md](file:///Users/matt/projects/ai-os/.rules/agent_logs.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/agent_logs.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/agent_logs.md) with the **Master Project Board Protocol**.
   - Recompiled all agent directives (`GEMINI.md`, `CLAUDE.md`, `HERMES.md`) via [build_rules.py](file:///Users/matt/projects/ai-os/scripts/build_rules.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/build_rules.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/build_rules.py).

---

### 📌 Quick Links to Your Board

- 📝 **Markdown File**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)
- ⚡ **1-Click Launch in Zed**: [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- 📓 **1-Click Launch in Obsidian**: [Open in Obsidian](obsidian://open?vault=Personal&file=Development%2FProject%20Notes%2FGlobal%20Todos)
- 📁 **1-Click Reveal in Finder**: [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

---

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`4edcb6c`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, apps/gemini-companion/src-tauri/src/cloud_sync.rs and 3 other file(s)</div></details>

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">@[conversation:"Troubleshooting Persistent Bun Processes"] Ok this all sounds good... but! I want the agents to consantly open the PROJECT_BOARD.md for me so I don't forget about it etc.
We have some kind of global todo system I believe though so look into that first (not that it's great, idk what it is, yours is probably better).</span>



<span title="Responded at 9:29am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Here is the full audit of your current to-do systems, why things have felt fragmented/forgotten, and how we can implement the **`PROJECT_BOARD.md`** auto-surfacing mechanism so you never lose track of active work again.

---

### 1. Audit: What To-Do Systems You Currently Have

Across your environment, there are three separate task-tracking layers:

| System | Location | Format & Tools | Intended Role | Current Limitation |
| :--- | :--- | :--- | :--- | :--- |
| **Apple Reminders** | macOS / iOS | `apple-reminders` CLI (defined in [core_safety.md](file:///Users/matt/projects/ai-os/.rules/core_safety.md#L24-L29) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md%3A24%3A29) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md)) | Personal tasks, daily life, mobile notifications. | Great for personal to-dos, but not suited for multi-repo software features or architectural plans. |
| **Obsidian Global Todos** | [Global Todos.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Global%20Todos.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/Library/Mobile%2520Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%2520Notes/Global%2520Todos.md) | `- [ ] Task [project:: <id>] [assignee:: user\|agent] [due:: YYYY-MM-DD]` | Central multi-project backlog for Obsidian Kanban. | **Completely passive**. Agents don't read it during pre-flight, and nothing triggers it to open for you, so it got buried. |
| **DevTool Features** | `~/.devtool/features/*.md` | YAML frontmatter (`status: "in-progress"`) + [get-active-task.sh](file:///Users/matt/projects/ai-os/scripts/get-active-task.sh) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/get-active-task.sh) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/get-active-task.sh) | In-flight coding task per repository. | Fragmented into loose markdown files in hidden folders; no unified view across all projects. |

---

### 2. Why It Felt Disconnected

- **No Visual Trigger**: Tasks sat quietly inside iCloud Obsidian files or `.devtool/features/` without anything actively popping up in your editor or terminal.
- **No Preflight State Hydration**: When starting a fresh session, agents didn't show what tasks were already in flight, forcing you to remember and re-explain state.
- **Fractured Responsibilities**: Personal reminders were isolated in Apple Reminders, while coding tasks were split between Obsidian and repository subfolders.

---

### 3. The Unified `PROJECT_BOARD.md` Architecture

To make `PROJECT_BOARD.md` impossible to forget and actively present in your workflow:

```
                  ┌──────────────────────────────────────────────┐
                  │          PROJECT_BOARD.md (Master)           │
                  │    ~/projects/ai-os/PROJECT_BOARD.md        │
                  │  (Symlinked / Synced with Obsidian Vault)    │
                  └──────────────────────┬───────────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
    ┌─────────────────────────┐ ┌──────────────────┐ ┌─────────────────────────┐
    │  Preflight Turn 1 Check  │ │  Interactive CLI │ │  Every Response Footer  │
    │  preflight.py reads     │ │  `ai-os tasks`   │ │  Direct 1-Click Launch  │
    │  top 3-5 active tasks   │ │  CLI / open hook │ │  [Zed] [Obsidian] [Web] │
    └─────────────────────────┘ └──────────────────┘ └─────────────────────────┘
```

### How Agents Will "Constantly Open & Surface" It:

1. **Permanent Single Source of Truth**:
   - Create [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) at the root of `ai-os` (and symlink it to Obsidian's `Personal/Development/Project Notes/Global Todos.md` so the Obsidian Kanban view remains live).
2. **Automatic Preflight Hydration**:
   - Update [preflight.py](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py) to read and print the active `[IN_PROGRESS]` and `[TODO]` items from `PROJECT_BOARD.md` whenever any agent starts a new thread.
3. **1-Click Launch & Auto-Open Links**:
   - In responses and preflights, provide direct interactive action links:
     - **Open in Zed**: `[](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)`
     - **Open in Obsidian**: `[Open in Obsidian](obsidian://open?vault=Personal&file=Development%2FProject%20Notes%2FGlobal%20Todos)`
     - **Open in Finder / Preview**: `[](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)`
4. **System Rule Persistence**:
   - Add a rule to `.rules/` so agents are required to append new backlog items, update completion status, and surface `PROJECT_BOARD.md` when closing tasks.

---

### Would You Like To Proceed With This Setup?

If you'd like to roll this out:
1. Initialize the master [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) with active tasks from Obsidian and `ai-os`.
2. Connect it to [preflight.py](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py) so top tasks display automatically at the start of every thread.
3. Add the rule to `.rules/` and compile via `build_rules.py`.

---

<details style="margin-top: 8px; font-size: 12px; opacity: 0.75; cursor: pointer;"><summary style="outline: none; cursor: pointer;">✅ <b>Committed</b></summary><div style="padding-top: 4px; font-style: italic;">[`59ee0c5`] Update .agy-mcp/worktrees/job-7f1a74efbfca4784, Discussions.html, tmp/last_preflight.log and 2 other file(s)</div></details>

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~80k / ~410k 🟢 (optimal) | 4:45am | 105 ❓, 16 📤 |

</span>

</span>