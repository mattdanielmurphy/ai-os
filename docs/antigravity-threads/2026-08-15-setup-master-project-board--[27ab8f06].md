---
title: "Setup Master Project Board"
date: "2026-08-15"
conversation_id: "27ab8f06-bced-4608-ae53-734a37c277da"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please perform the following file creations, edits, and symlink setups:

1. Create `/Users/matt/projects/ai-os/PROJECT_BOARD.md` with the following content:
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
```

2. Link / Symlink `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/Global Todos.md` to `/Users/matt/projects/ai-os/PROJECT_BOARD.md` via `run_command`:
```bash

ln -sf "/Users/matt/projects/ai-os/PROJECT_BOARD.md" "/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/Global Todos.md"
```

3. Edit `/Users/matt/projects/ai-os/scripts/preflight.py`:
Add a helper function:
```python

def get_project_board_summary():
    board_path = os.path.expanduser("~/projects/ai-os/PROJECT_BOARD.md")
    if not os.path.exists(board_path):
        return []
    
    in_progress = []
    backlog = []
    current_section = None
    
    try:
        with open(board_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if "## 🚀 In Progress" in line_str or "## In Progress" in line_str:
                    current_section = "in_progress"
                    continue
                elif "## 📋 Backlog" in line_str or "## To Do" in line_str:
                    current_section = "backlog"
                    continue
                elif line_str.startswith("## "):
                    current_section = None
                    continue
                
                if line_str.startswith("- [ ]") and current_section:
                    task_text = line_str[5:].strip()
                    if current_section == "in_progress":
                        in_progress.append(task_text)
                    elif current_section == "backlog":
                        backlog.append(task_text)
    except Exception:
        pass
    
    return in_progress, backlog
```

In `main()` of `preflight.py`, when `is_first` is true (after printing the recent thread context block), print:
```python

        in_progress, backlog = get_project_board_summary()
        if in_progress or backlog:
            print("=== ACTIVE PROJECT BOARD (PROJECT_BOARD.md) ===")
            print("Path: file:///Users/matt/projects/ai-os/PROJECT_BOARD.md")
            print("Launch: http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md\n")
            if in_progress:
                print("🚀 In Progress:")
                for item in in_progress[:4]:
                    print(f"  - {item}")
            if backlog:
                print("\n📋 Top Backlog:")
                for item in backlog[:4]:
                    print(f"  - {item}")
            print("================================================\n")
```

4. Edit `/Users/matt/projects/ai-os/.rules/agent_logs.md`:
Append:
```markdown

## Master Project Board Protocol
- **Single Source of Truth**: Active multi-project backlog is maintained in `/Users/matt/projects/ai-os/PROJECT_BOARD.md` (synced with Obsidian `Personal/Development/Project Notes/Global Todos.md`).
- **Hydration & Visibility**: `preflight.py` automatically hydrates in-progress and top backlog items at the start of every session.
- **Surfacing Requirement**: Agents MUST surface clickable links (`[PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)`) with 1-click action links whenever initiating new features or concluding tasks.
- **Task Schema**: Always format tasks as `- [ ] <description> [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`.
```

5. Run `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` via `run_command` to compile rules into `GEMINI.md`, `CLAUDE.md`, and `HERMES.md`.

Verify that everything works and report back.</span>



<span title="Responded at 9:32am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The master project board infrastructure has been successfully established.

### Summary of Actions
- **Project Board**: Created [`PROJECT_BOARD.md`](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) and symlinked it to your Obsidian `Global Todos.md`.
- **Pre-flight Hydration**: Updated [`preflight.py`](file:///Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/preflight.py) to automatically parse the project board and display "In Progress" and "Top Backlog" items at the start of every session.
- **Protocol Documentation**: Added the **Master Project Board Protocol** to [`agent_logs.md`](file:///Users/matt/projects/ai-os/.rules/agent_logs.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/agent_logs.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/agent_logs.md), formalizing task schema and visibility requirements for agents.
- **Rules Sync**: Successfully ran `build_rules.py` to propagate these updates to your system-wide agent rules (`GEMINI.md`, `CLAUDE.md`, `HERMES.md`).

You can access your consolidated task board at any time via:
[PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | PPLX Quota |
| :--- | :--- | :--- |
| ~40k / ~410k 🟢 (optimal) | 4:30am | 105 ❓, 16 📤 |

</span>

</span>