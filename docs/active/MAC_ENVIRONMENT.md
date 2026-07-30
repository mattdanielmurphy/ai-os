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

## Crontab Automations
* **ping_agy.py**: Runs via cron at 10:00, 15:00, 20:00, and 01:00. Checks `ag-quota --all --json`. If the 5-hour quota is fully replenished (100%) and weekly quota > 0%, it sends a `say hi` prompt to `tmux` sessions `agy_matt` (iammattmurphy) and `agy_darryl` (darryl.l.murphy) to keep the 5hr window distributed. (Script: `~/.local/bin/ping_agy.py`)


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

### Media Playback
* **IINA** (primary video player, built on mpv — config at `~/.config/mpv/`)


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

---

## IINA / mpv Subtitle Configuration

IINA is configured to use a shared mpv config directory at `~/.config/mpv/`. **Do not use the IINA Advanced preferences table to set mpv options** — use the config file directly.

* **Config file**: [`~/.config/mpv/mpv.conf`](file:///Users/matt/.config/mpv/mpv.conf)
* **IINA pref**: Preferences → Advanced → "Use config directory" → `~/.config/mpv/`

### Subtitle Filtering (`~/.config/mpv/mpv.conf`)

Multiple layers of subtitle filtering are active:

| Setting | Value | Purpose |
| :--- | :--- | :--- |
| `sub-filter-sdh` | `yes` | Strips SDH (Subtitles for the Deaf/Hard-of-Hearing) markers via mpv's built-in SDH filter |
| `sub-filter-sdh-harder` | `yes` | More aggressive SDH stripping (catches edge cases the standard filter misses) |
| `sub-filter-regex-enable` | `yes` | Enables the regex-based line filter pipeline |
| `sub-filter-regex-append` | `\[.*?\]` | Strips bracketed descriptions, e.g. `[Audio Description]`, `[cheering]` |
| `sub-filter-regex-append` | `\(.*?\)` | Strips parenthetical stage directions, e.g. `(whispering)` |
| `sub-filter-regex-append` | `[♪♫]` | Strips musical lyric lines (any line containing a musical note character) |

> [!NOTE]
> `sub-filter-regex-append` removes the **entire subtitle cue** if the pattern matches anywhere in the line. Multiple `sub-filter-regex-append` entries are additive — each one registers an additional filter in mpv's pipeline.

> [!TIP]
> To temporarily disable all regex filters without removing them, set `sub-filter-regex-enable=no` in `mpv.conf` (or pass `--no-sub-filter-regex-enable` as a runtime flag).

