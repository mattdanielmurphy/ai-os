---
title: "Managing Zed Project Windows"
date: "2026-08-15"
conversation_id: "bc873415-e2cd-4e80-9d00-35771a78ae60"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">holy shit, option c changes everything lol</span>



<span title="Responded at 7:28pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

It really is a game changer! ⚡

`Cmd + Alt + O` (the **Open Recent Projects** fuzzy palette) is instant in Zed. Because it fuzzy-indexes all your recent workspaces and restores your exact editor tab layout when reopened, you can freely close windows with `Cmd + W` whenever you're done with a task, knowing any project is just a 2-second shortcut away.

* **Thread Artifact**: [thread.md](file:///Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md)

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">I want a way to quickly open project folders in Zed on demand with a fuzzy search, I think using Raycast would be ideal.
I have been keeping a bunch of windows open in Zed, and as performant as Zed is, I don't think it's ideal or necessary really to have like 10 windows open in Zed. I mean, let me know, maybe it's not a real problem. If it IS a real problem, we should basically just try and keep like a buffer of 4 windows open at once in Zed, and when we want to switch to another project, the least recently accessed project window should be swapped out.
Does that make sense?
I mean, do let me know if having like 10 windows open in Zed isn't an issue, because I don't want to complicate things unnecessarily.
And by an "issue" I mean taking up a bunch of memory/CPU.</span>



<span title="Responded at 7:27pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### 1. Is Having 10 Windows Open in Zed an Issue?

**Short answer:** The Zed app itself is extremely lean, but **the background Language Servers (LSPs) spawned by each window definitely add up.**

We ran a live process inspection on your machine to see what Zed is running right now:
* **The Zed UI/Core**: Native Rust + GPUI. It consumes near **0% CPU** at idle and only ~50–100MB RAM for the windowing system (vastly lighter than Electron-based editors like VS Code or Cursor).
* **The Hidden Cost (LSPs & File Watchers)**: Every project folder opened in Zed boots up its own independent language server daemons. Currently on your machine, your open Zed windows are running **15+ background daemon processes**, including:
  * Multiple instances of `vtsls` / `tsserver` (TypeScript) allocated up to `--max-old-space-size=8192`
  * Multiple instances of `basedpyright` and `ruff` (Python)
  * Multiple instances of `tailwindcss-language-server`
  * Multiple instances of `vscode-eslint`
  * File-system watchers (`fsevents`) keeping handles on all files in each repo

**Verdict**: While 10 idle windows won't grind an Apple Silicon Mac to a halt, having 10 distinct workspaces running duplicate language servers consumes several gigabytes of RAM and triggers periodic background indexing spikes whenever git updates occur. Keeping your active workspace footprint down to **2–4 projects** is much cleaner for system resources and reduces window-switching friction.

---

### 2. Is an Automated 4-Window LRU "Eviction Buffer" Necessary?

Automating an LRU auto-closer daemon (e.g. via Hammerspoon or a background script that detects window count > 4 and kills the oldest window) is possible, but **it introduces unwanted friction**:
1. It risks discarding unsaved scratch buffers or active in-editor terminal sessions.
2. Zed already remembers open tabs and state when reopening a project folder.
3. **The real reason people hoard windows is open-friction:** when opening a project is slow or requires navigating the filesystem, you leave everything open "just in case." When switching projects takes **< 1 second via fuzzy search**, closing windows becomes effortless because reopening them is instant.

---

### 3. Quick Ways to Fuzzy-Open Projects in Zed via Raycast

Here are the best ways to get instant fuzzy opening:

### Option A: Raycast "Projects" or "Zed Recent Projects" Extension (Recommended)
Raycast has official community extensions designed specifically for this:
1. Open Raycast (`Cmd + Space` or your shortcut) -> type **"Store"**.
2. Search for **"Projects"** (by Thomas Paul Mann) or **"Zed"**.
3. In the extension settings, point your projects directory to `~/projects` (or your default workspace path) and set the default application to **Zed**.
4. Now, pressing your shortcut and typing the project name lets you fuzzy filter and press `Enter` to instantly open it in Zed.

---

### Option B: Dedicated Raycast Script Command
If you prefer a direct local script that scans `~/projects` using `fd`, you can create a Raycast script command:

```bash
#!/bin/bash

### Required parameters:

### @raycast.schemaVersion 1

### @raycast.title Open in Zed

### @raycast.mode silent

### @raycast.packageName Developer

### ### Optional parameters:

### @raycast.icon ⚡

### @raycast.argument1 { "type": "text", "placeholder": "Project Name (fuzzy)", "optional": false }

QUERY="$1"
PROJECT_DIR="/Users/matt/projects"

### Fuzzy match project folder using fd
MATCH=$(/opt/homebrew/bin/fd --max-depth 2 --type d . "$PROJECT_DIR" | grep -i "$QUERY" | head -n 1)

if [ -n "$MATCH" ]; then
    /usr/local/bin/zed "$MATCH"
    echo "Opened $MATCH in Zed"
else
    echo "No project matching '$QUERY' found"
    exit 1
fi
```

---

### Option C: Zed's Built-in Project Switcher
If Zed is already focused:
* `Cmd + Alt + O`: Opens the **Recent Projects** fuzzy palette.
* `Cmd + Shift + O`: Opens the **Open Workspace** folder browser.

---

### Thread & Task Tracking
* **Thread Artifact**: [thread.md](file:///Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/bc873415-e2cd-4e80-9d00-35771a78ae60/thread.md)
* **Master Project Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~40k / ~410k 🟢 (optimal) | 2:30pm | 🟡 Uncommitted (1) | 113 ❓, 19 📤 |

</span>

</span>