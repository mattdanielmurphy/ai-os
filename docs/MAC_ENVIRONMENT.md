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

All agent scripts now run inside **named tmux sessions** via `~/Library/Scripts/tmux-agent-wrapper.sh`.

**Key features:**
- **tmux-accessible**: Attach with `tmux attach -t agent-<name>` to see real-time logs
- **Auto-restart on script modification**: Editing the script file triggers a restart + macOS notification
- **Two modes**: `keepalive` (long-running daemons, watched by fswatch) or `oneshot` (event/schedule-driven, watched by launchd WatchPaths)
- **Logs**: Consolidated to `~/Library/Logs/launch-agents/`
- **Helper**: Run `~/Library/Scripts/tmux-agents.sh` for a status overview

| Label / Plist | tmux Session | Script / Command | Mode | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `com.matt.agent.irig-watcher` | `agent-irig-watcher` | `irig_watcher.sh` | keepalive | 🎸 iRig audio device — switches audio output on connect/disconnect |
| `com.matt.agent.litellm` | `agent-litellm` | `run_litellm.sh` → litellm | keepalive | 🤖 LiteLLM proxy on `localhost:8082` |
| `com.matt.agent.userscript-bundler` | `agent-userscript-bundler` | `watch-and-bundle.js` | keepalive | 📦 Auto-bundles userscripts on file changes |
| `com.matt.agent.chrome-debug` | `agent-chrome-debug` | Chrome (binary, no-watch) | keepalive | 🌐 Chrome debug instance on port 9223 |
| `com.matt.agent.hermes-gateway` | `agent-hermes-gateway` | Hermes gateway (`python -m hermes_cli.main`) | keepalive | 🔮 Hermes Agent gateway |
| `com.matt.agent.rules-watcher` | `agent-rules-watcher` | `sync_rules.sh` | oneshot | 📋 Syncs `~/.gemini/GEMINI.md` → workspace (WatchPaths) |
|| `com.matt.agent.energy-monitor` | `agent-energy-monitor` | `energy_monitor.sh` | oneshot | 🔋 Battery/energy alert — every 300s (StartInterval) |
|| `com.matt.agent.gemini-ingest` | `agent-gemini-ingest` | `gemini-ingest-watch.sh` | keepalive | 📥 Auto-ingests Gemini chat archives into Hermes FTS5 search (fswatch) |
| `com.matt.agent.notesync` | `agent-notesync` | `notesync-wrapper` (binary) | oneshot | 📝 Syncs Obsidian notes (WatchPaths) |
| `com.matt.agent.backup-agents` | `agent-backup-agents` | `cp` plists to backup dir | oneshot | 💾 Daily backup at 11:30 |


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


## Troubleshooting & Post-Migration Fixes

### Raycast Database Exception (SQLCipher Key Mismatch)
* **Symptom**: Raycast fails to open its SQLite databases on launch, reporting: `Could not open database - wrong database key` / `SQLite error 26: file is not a database`.
* **Root Cause**: Post-migration, the keychain item (`database_key` under service `Raycast` in the login keychain) is either recreated with an incorrect key, or its Access Control Lists (ACLs) prevent access due to username differences (`matthewmurphy` -> `matt`).
* **Fix**:
  1. Kill all active Raycast processes: `killall Raycast`
  2. Retrieve the correct database encryption key from the old login keychain backup (if available, e.g. using `security find-generic-password -s Raycast -a database_key -w`).
  3. Recreate the keychain password item in the current active login keychain:
     ```bash
     security add-generic-password -a database_key -s Raycast -l Raycast -w <correct_key> -T /Applications/Raycast.app
     ```
  4. Correct owner permissions of `/Applications/Raycast.app`:
     ```bash
     sudo chown -R matt:staff /Applications/Raycast.app
     ```
  5. Restore a clean backup database if journal/wal lock files were corrupted during failed launch attempts.
