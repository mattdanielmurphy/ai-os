---
title: "Update Developer Tooling Documentation"
date: "2026-08-05"
conversation_id: "f8594952-77a9-4d01-8183-9e8da1cbcaed"
source: "antigravity"
---

# Update Developer Tooling Documentation

## User

In `/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`, update section `Developer Tooling & Languages (Brew & FNM)` -> `CLI Utilities` to include a note about Zellij:

```markdown
* **CLI Utilities**: `ripgrep` (`rg`), `fzf`, `fd`, `ffmpeg`, `yt-dlp`, `tmux`, `zellij` (modern Rust-based terminal multiplexer workspace; alternative to tmux with out-of-the-box mouse, floating panes, and KDL layout templates).
```

---

## Assistant

Created At: 2026-08-05T01:22:26-06:00
Completed At: 2026-08-05T01:22:26-06:00
File Path: `file:///Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`
Total Lines: 142
Total Bytes: 8430
Showing lines 1 to 142
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # macOS Environment & Automation Catalog
2: 
3: This document details the non-native software, custom automations, Launch Agents, and user utilities installed on this Mac. 
4: 
5: > [!IMPORTANT]
6: > **Instructions for AI Agents:** Check this file before proposing any software installation, scripting background processes, debugging macOS-specific behavior, or referencing paths on the host. Always check path variables and ensure they do not reference the legacy `matthewmurphy` username unless explicitly required by an existing symbolic link/volume.
7: 
8: ---
9: 
10: ## System Overview & Username Guardrail
11: * **Active User Account**: `matt`
12: * **Home Directory**: `/Users/matt`
13: * **Legacy Account**: `matthewmurphy` (Migrated in 2026. Keep in mind that some scripts/configs might still contain references to `/Users/matthewmurphy/` or CloudMounter folders like `/Users/matt/Library/CloudStorage/CloudMounter-MatthewMurphy/` which are valid folders but use the legacy name in the directory string. Translate raw `/Users/matthewmurphy/` to `/Users/matt/` where appropriate).
14: 
15: ---
16: 
17: ## Active Custom Launch Agents (`~/Library/LaunchAgents`)
18: 
19: All agent scripts now run inside **named tmux sessions** via `~/Library/Scripts/tmux-agent-wrapper.sh`.
20: 
21: **Key features:**
22: - **tmux-accessible**: Attach with `tmux attach -t agent-<name>` to see real-time logs
23: - **Auto-restart on script modification**: Editing the script file triggers a restart + macOS notification
24: - **Two modes**: `keepalive` (long-running daemons, watched by fswatch) o
<truncated 5475 bytes>
hown -R matt:staff /Applications/Raycast.app
111:      ```
112:   5. Restore a clean backup database if journal/wal lock files were corrupted during failed launch attempts.
113: 
114: ---
115: 
116: ## IINA / mpv Subtitle Configuration
117: 
118: IINA is configured to use a shared mpv config directory at `~/.config/mpv/`. **Do not use the IINA Advanced preferences table to set mpv options** — use the config file directly.
119: 
120: * **Config file**: [`~/.config/mpv/mpv.conf`](file:///Users/matt/.config/mpv/mpv.conf)
121: * **IINA pref**: Preferences → Advanced → "Use config directory" → `~/.config/mpv/`
122: 
123: ### Subtitle Filtering (`~/.config/mpv/mpv.conf`)
124: 
125: Multiple layers of subtitle filtering are active:
126: 
127: | Setting | Value | Purpose |
128: | :--- | :--- | :--- |
129: | `sub-filter-sdh` | `yes` | Strips SDH (Subtitles for the Deaf/Hard-of-Hearing) markers via mpv's built-in SDH filter |
130: | `sub-filter-sdh-harder` | `yes` | More aggressive SDH stripping (catches edge cases the standard filter misses) |
131: | `sub-filter-regex-enable` | `yes` | Enables the regex-based line filter pipeline |
132: | `sub-filter-regex-append` | `\[.*?\]` | Strips bracketed descriptions, e.g. `[Audio Description]`, `[cheering]` |
133: | `sub-filter-regex-append` | `\(.*?\)` | Strips parenthetical stage directions, e.g. `(whispering)` |
134: | `sub-filter-regex-append` | `[♪♫]` | Strips musical lyric lines (any line containing a musical note character) |
135: 
136: > [!NOTE]
137: > `sub-filter-regex-append` removes the **entire subtitle cue** if the pattern matches anywhere in the line. Multiple `sub-filter-regex-append` entries are additive — each one registers an additional filter in mpv's pipeline.
138: 
139: > [!TIP]
140: > To temporarily disable all regex filters without removing them, set `sub-filter-regex-enable=no` in `mpv.conf` (or pass `--no-sub-filter-regex-enable` as a runtime flag).
141: 
142: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T01:22:27-06:00
Completed At: 2026-08-05T01:22:27-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -90,7 +90,7 @@
 * **Node.js**: Managed with `fnm` and `nvm`.
 * **Python**: `python@3.14` and `uv` package manager.
 * **Deno** & **Go** & **Rust** (via `rqbit` etc).
-* **CLI Utilities**: `ripgrep` (`rg`), `fzf`, `fd`, `ffmpeg`, `yt-dlp`, `tmux`.
+* **CLI Utilities**: `ripgrep` (`rg`), `fzf`, `fd`, `ffmpeg`, `yt-dlp`, `tmux`, `zellij` (modern Rust-based terminal multiplexer workspace; alternative to tmux with out-of-the-box mouse, floating panes, and KDL layout templates).
 
 
 ## Troubleshooting & Post-Migration Fixes
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T01:22:28-06:00
Completed At: 2026-08-05T01:22:28-06:00
Message sent to "1ce62fc6-6678-46f6-917b-9922ad57809b".

OK. I have updated `/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md` as requested.

---
