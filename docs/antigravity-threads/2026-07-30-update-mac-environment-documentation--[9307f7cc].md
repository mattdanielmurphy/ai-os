---
title: "Update Mac Environment Documentation"
date: "2026-07-30"
conversation_id: "9307f7cc-f476-4fd3-9f1b-bc0c0001f88a"
source: "antigravity"
---

# Update Mac Environment Documentation

## User

Edit the file `/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`.

**Task:** Make two targeted edits:

**Edit 1:** After line 69 (`* **PopClip** (Contextual text selection popup)`) and before line 70 (`* **Shottr** (Screenshot utility)`), in the `### Automation & Productivity` section, there is no media app. We need to add a new subsection after the existing `### Automation & Productivity` block ends. Actually, insert at the end of `### Development & Editors` section (after the Obsidian bullet on line 80), add a new subsection:

Actually here is the precise instruction:

In the `## Key Installed Applications & Tools` section, after the `### Development & Editors` subsection (after the Obsidian line), add this new subsection:

```

### Media Playback
* **IINA** (primary video player, built on mpv — config at `~/.config/mpv/`)
```

**Edit 2:** After line 108 (the last line: `5. Restore a clean backup database if journal/wal lock files were corrupted during failed launch attempts.`), append a completely new section at the end of the file:

```

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
```

Please make both edits now. For Edit 1, insert the new `### Media Playback` subsection by finding the exact Obsidian line and inserting after it. For Edit 2, append the new section at the very end of the file.

---

## Assistant

Created At: 2026-07-29T18:30:01-06:00
Completed At: 2026-07-29T18:30:01-06:00
File Path: `file:///Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`
Total Lines: 109
Total Bytes: 6688
Showing lines 70 to 109
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
70: * **Yoink** (Drag-and-drop shelf utility)
71: * **PopClip** (Contextual text selection popup)
72: * **Shottr** (Screenshot utility)
73: 
74: ### Development & Editors
75: * **Antigravity IDE** & **Antigravity.app**
76: * **Xcode** & **Fork** (Git GUI)
77: * **GitKraken** & **Warp** (Modern terminal emulator)
78: * **Claude.app**
79: * **Typora** (Markdown editor)
80: * **Obsidian** (Notes application, syncs personal documents via `com.user.notesync.plist`)
81: 
82: ---
83: 
84: ## Developer Tooling & Languages (Brew & FNM)
85: Preferred CLI tools available on the path:
86: * **Node.js**: Managed with `fnm` and `nvm`.
87: * **Python**: `python@3.14` and `uv` package manager.
88: * **Deno** & **Go** & **Rust** (via `rqbit` etc).
89: * **CLI Utilities**: `ripgrep` (`rg`), `fzf`, `fd`, `ffmpeg`, `yt-dlp`, `tmux`.
90: 
91: 
92: ## Troubleshooting & Post-Migration Fixes
93: 
94: ### Raycast Database Exception (SQLCipher Key Mismatch)
95: * **Symptom**: Raycast fails to open its SQLite databases on launch, reporting: `Could not open database - wrong database key` / `SQLite error 26: file is not a database`.
96: * **Root Cause**: Post-migration, the keychain item (`database_key` under service `Raycast` in the login keychain) is either recreated with an incorrect key, or its Access Control Lists (ACLs) prevent access due to username differences (`matthewmurphy` -> `matt`).
97: * **Fix**:
98:   1. Kill all active Raycast processes: `killall Raycast`
99:   2. Retrieve the correct database encryption key from the old login keychain backup (if available, e.g. using `security find-generic-password -s Raycast -a database_key -w`).
100:   3. Recreate the keychain password item in the current active login keychain:
101:      ```bash
102:      security add-generic-password -a database_key -s Raycast -l Raycast -w <correct_key> -T /Applications/Raycast.app
103:      ```
104:   4. Correct owner permissions of `/Applications/Raycast.app`:
105:      ```bash
106:      sudo chown -R matt:staff /Applications/Raycast.app
107:      ```
108:   5. Restore a clean backup database if journal/wal lock files were corrupted during failed launch attempts.
109: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-29T18:30:03-06:00
Completed At: 2026-07-29T18:30:03-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -79,6 +79,10 @@
 * **Typora** (Markdown editor)
 * **Obsidian** (Notes application, syncs personal documents via `com.user.notesync.plist`)
 
+### Media Playback
+* **IINA** (primary video player, built on mpv — config at `~/.config/mpv/`)
+
+
 ---
 
 ## Developer Tooling & Languages (Brew & FNM)
@@ -105,4 +105,33 @@
      sudo chown -R matt:staff /Applications/Raycast.app
      ```
   5. Restore a clean backup database if journal/wal lock files were corrupted during failed launch attempts.
+
+---
+
+## IINA / mpv Subtitle Configuration
+
+IINA is configured to use a shared mpv config directory at `~/.config/mpv/`. **Do not use the IINA Advanced preferences table to set mpv options** — use the config file directly.
+
+* **Config file**: [`~/.config/mpv/mpv.conf`](file:///Users/matt/.config/mpv/mpv.conf)
+* **IINA pref**: Preferences → Advanced → "Use config directory" → `~/.config/mpv/`
+
+### Subtitle Filtering (`~/.config/mpv/mpv.conf`)
+
+Multiple layers of subtitle filtering are active:
+
+| Setting | Value | Purpose |
+| :--- | :--- | :--- |
+| `sub-filter-sdh` | `yes` | Strips SDH (Subtitles for the Deaf/Hard-of-Hearing) markers via mpv's built-in SDH filter |
+| `sub-filter-sdh-harder` | `yes` | More aggressive SDH stripping (catches edge cases the standard filter misses) |
+| `sub-filter-regex-enable` | `yes` | Enables the regex-based line filter pipeline |
+| `sub-filter-regex-append` | `\[.*?\]` | Strips bracketed descriptions, e.g. `[Audio Description]`, `[cheering]` |
+| `sub-filter-regex-append` | `\(.*?\)` | Strips parenthetical stage directions, e.g. `(whispering)` |
+| `sub-filter-regex-append` | `[♪♫]` | Strips musical lyric lines (any line containing a musical note character) |
+
+> [!NOTE]
+> `sub-filter-regex-append` removes the **entire subtitle cue** if the pattern matches anywhere in the line. Multiple `sub-filter-regex-append` entries are additive — each one registers an additional filter in mpv's pipeline.
+
+> [!TIP]
+> To temporarily disable all regex filters without removing them, set `sub-filter-regex-enable=no` in `mpv.conf` (or pass `--no-sub-filter-regex-enable` as a runtime flag).
+
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-29T18:30:04-06:00
Completed At: 2026-07-29T18:30:04-06:00
Message sent to "5944c05d-2f05-4f4a-ae38-9254f85dbeb3".

The requested edits have been completed in `/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`.

- Added the `### Media Playback` subsection following the `Obsidian` entry in the `### Development & Editors` block.
- Appended the new `## IINA / mpv Subtitle Configuration` section to the end of the document.

---
