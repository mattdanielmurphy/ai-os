# macOS Environment & Automation Catalog

This document details the non-native software, custom automations, Launch Agents, and user utilities installed on this Mac. 

> [!IMPORTANT]
> **Instructions for AI Agents:** Check this file before proposing any software installation, scripting background processes, debugging macOS-specific behavior, or referencing paths on the host. Always check path variables and ensure they do not reference the legacy `matthewmurphy` username unless explicitly required by an existing symbolic link/volume.

---

## System Overview & Username Guardrail
* **Active User Account**: `matt`
* **Home Directory**: `/Users/matt`
* **Legacy Account**: `matthewmurphy` (Migrated in 2026. Keep in mind that some scripts/configs might still contain references to `/Users/matthewmurphy/` or CloudMounter folders like `/Users/matt/Library/CloudStorage/CloudMounter-MatthewMurphy/` which are valid folders but use the legacy name in the directory string. Translate raw `/Users/matthewmurphy/` to `/Users/matt/` where appropriate).

---

## Active Custom Launch Agents (`~/Library/LaunchAgents`)

These background services are configured to launch automatically for the user:

| Label / Plist Filename | Executable / Command | Purpose | Notes |
| :--- | :--- | :--- | :--- |
| `com.chrome.debug.plist` | `/Applications/Google Chrome.app ... --remote-debugging-port=9223 --user-data-dir=/Users/matt/.chrome-debug-profile` | Dedicated Chrome debug instance. | **KeepAlive: True**, **ThrottleInterval: 2s**. Will auto-relaunch with a window after 2 seconds if quit (prevents profile lock collision). |
| `ai.openclaw.gateway.plist` | `openclaw/dist/index.js gateway --port 18789` | OpenClaw Gateway Service. | Uses node v26.3.0 under NVM. |
| `com.matthewmurphy.backup-launch-agents.plist` | `/usr/bin/rsync -av` | Backs up custom plist files. | Backs up to CloudMounter directory. Run calendar: daily at 11:30. |
| `com.matthewmurphy.energy_monitor.plist` | `energy_monitor.sh` | Bash script monitoring system energy/battery. | Runs every 300 seconds (5 minutes). |
| `com.matthewmurphy.irig-watcher.plist` | `irig_watcher.sh` | Bash script watching for iRig connection/disconnection. | **KeepAlive: True**. |
| `com.matthewmurphy.personal-sync.plist` | `watch-personal-sync.sh` | Personal sync utility. | **KeepAlive: True**. Logs to standard logs directory. |
| `com.matthewmurphy.rqbit.plist` | `/usr/local/bin/rqbit server start /Users/matt/Downloads` | Rust-based Bittorrent server. | **KeepAlive: True**. |
| `com.mattmurphy.userscript-bundler.plist` | `watch-and-bundle.js` | Automatically bundles userscripts upon file changes. | **KeepAlive: True**. Working directory: `/Users/matt/projects/userscript-bundler`. |
| `com.user.notesync.plist` | `notesync-wrapper` | Syncs Obsidian notes when target paths change. | Watches `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal`. |
| `com.mattmurphy.ai-os-rules-watcher.plist` | `sync_rules.sh` | Automatically syncs ~/.gemini/GEMINI.md to workspace repository. | **WatchPaths: ~/.gemini/GEMINI.md**. Cwd: `/Users/matt/projects/ai-os`. |


---

## Hammerspoon Automation (`~/.hammerspoon`)
Hammerspoon is used for window management, system shortcuts, and clipboard history.

* **Main Configuration File**: [init.lua](file:///Users/matt/.hammerspoon/init.lua)
  * Watches `~/.hammerspoon/` directory tree and automatically reloads configuration upon any `.lua` file modification.
  * Modular system loading:
    * `modules/clipboard` — Handles clipboard history and management.
    * `modules/keybindings` — Custom system-wide keyboard shortcuts.
* **Additional scripts**:
  * [rcmd.lua](file:///Users/matt/.hammerspoon/rcmd.lua)

---

## Key Installed Applications & Tools
These are notable tools installed on the Mac that should be favored or respected:

### Automation & Productivity
* **Alfred 5** & **Raycast** (Launcher/Workflows)
* **Hammerspoon** (Lua system automation)
* **Keyboard Maestro** (Macro engine)
* **Karabiner-Elements** (Low-level keyboard customizer)
* **AltTab** (Windows-style Alt-Tab switcher)
* **Bartender 5** & **Ice** (Menu bar organizers)
* **Yoink** (Drag-and-drop shelf utility)
* **PopClip** (Contextual text selection popup)
* **Shottr** (Screenshot utility)

### Development & Editors
* **Antigravity IDE** & **Antigravity.app**
* **Xcode** & **Fork** (Git GUI)
* **GitKraken** & **Warp** (Modern terminal emulator)
* **Claude.app**
* **Typora** (Markdown editor)
* **Obsidian** (Notes application, syncs personal documents via `com.user.notesync.plist`)

---

## Developer Tooling & Languages (Brew & FNM)
Preferred CLI tools available on the path:
* **Node.js**: Managed with `fnm` and `nvm`.
* **Python**: `python@3.14` and `uv` package manager.
* **Deno** & **Go** & **Rust** (via `rqbit` etc).
* **CLI Utilities**: `ripgrep` (`rg`), `fzf`, `fd`, `ffmpeg`, `yt-dlp`, `tmux`.
