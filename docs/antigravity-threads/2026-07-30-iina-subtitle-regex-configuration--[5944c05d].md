---
title: "IINA Subtitle Regex Configuration"
date: "2026-07-30"
conversation_id: "5944c05d-2f05-4f4a-ae38-9254f85dbeb3"
source: "antigravity"
---

# IINA Subtitle Regex Configuration

## User

we've got some kind of IINA regex for subtitles to strip out `[Audio Descriptions]`...
one more thing to strip out: musical lyrics

---

## Assistant

Created At: 2026-07-29T18:27:29-06:00
Completed At: 2026-07-29T18:27:29-06:00

				The command completed successfully.
				Output:
				/Users/matt/Library/Preferences/com.colliderli.iina.plist

Created At: 2026-07-29T18:27:33-06:00
Completed At: 2026-07-29T18:27:33-06:00

				The command completed successfully.
				Output:
				{
  "arrowBtnAction" => 2
  "audioDevice" => "auto"
  "audioDeviceDesc" => "Autoselect device"
  "audioLanguage" => "en,eng"
  "controlBarPositionHorizontal" => 0.4935347945601852
  "controlBarPositionVertical" => 0.1930266203703704
--
  "mpvProperties" => [
    0 => {
      "name" => "sub-filter-sdh"
      "value" => "yes"
    }
    1 => {
      "name" => "sub-filter-sdh-harder"
      "value" => "yes"
    }
--
  "NSNavPanelExpandedSizeForOpenMode" => "{800, 448}"
  "NSOSPLastRootDirectory" => {length = 680, bytes = 0x626f6f6b a8020000 00000510 40000000 ... 04000000 00000000 }
  "NSSplitView Subview Frames NSColorPanelSplitView" => [
    0 => "0.000000, 0.000000, 224.000000, 258.000000, NO, NO"
    1 => "0.000000, 259.000000, 224.000000, 48.000000, NO, NO"
--
    "TB Is Shown" => 1
  }
  "NSWindow Frame AudioFilters" => "1073 837 640 410 0 0 2560 1415 "
  "NSWindow Frame EditFilterWindow" => "732 649 393 264 0 0 1728 1085 "
  "NSWindow Frame IINAFontPickerWindow" => "118 170 458 530 0 0 1728 1085 "
  "NSWindow Frame IINAMiniPlayerWindow" => "519 517 300 240 0 0 1728 1079 "
--
  "NSWindow Frame IINAPreferenceWindow" => "337 199 820 579 0 0 1728 1085 "
  "NSWindow Frame IINAWelcomeWindow" => "704 378 640 400 0 0 1728 1079 "
  "NSWindow Frame NewFilterWindow" => "618 544 620 428 0 0 1728 1085 "
  "NSWindow Frame NSColorPanel" => "66 127 224 278 0 0 1728 1079 "
  "NSWindow Frame NSNavPanelAutosaveName" => "464 473 800 448 0 0 1728 1079 "
  "NSWindow Frame SaveFilterWindow" => "727 655 403 253 0 0 1728 1085 "
  "NSWindow Frame VideoFilters" => "608 562 640 410 0 0 1728 1085 "
  "playlistAutoPlayNext" => 0
  "PluginEnabled.com.pparanoiidd.skipintro" => 1
  "PluginEnabled.com.recorder.iina-plugin" => 1
  "PluginEnabled.io.iina.opensub" => 1
  "PluginEnabled.io.iina.user-script" => 1
  "PluginEnabled.io.iina.ytdl" => 1
  "PluginOrder" => [
    0 => "io.iina.ytdl"
    1 => "io.iina.opensub"
    2 => "com.pparanoiidd.skipintro"
    3 => "io.iina.user-script"
    4 => "com.recorder.iina-plugin"
  ]
  "savedVideoFilters" => [
    0 => {
      "filterString" => "eq=gamma=%3%1.2"
      "name" => "x"
      "shortcutKey" => "x"
--
  "softVolume" => 100
  "SUAutomaticallyUpdate" => 1
  "subLang" => "en"
  "subTextSize" => 16
  "SUEnableAutomaticChecks" => 1
  "SUHasLaunchedBefore" => 1

I can see it's using mpv's built-in `sub-filter-sdh` and `sub-filter-sdh-harder` properties. Let me check for any custom regex filter too:

Created At: 2026-07-29T18:27:39-06:00
Completed At: 2026-07-29T18:27:39-06:00

				The command completed successfully.
				Output:
				  "mpvProperties" => [
    0 => {
      "name" => "sub-filter-sdh"
      "value" => "yes"
    }
--
      "name" => "sub-filter-sdh-harder"
      "value" => "yes"
    }

Got it. Right now you're using mpv's built-in SDH filters. To strip musical lyrics (lines with `♪` or `♫`), you can add a `sub-filter-regex` mpv property. Here's what to add in **IINA → Preferences → Advanced → Extra mpv options**:

**New property to add:**

| Name | Value |
|---|---|
| `sub-filter-regex` | `^[♪♫].+[♪♫]$\|^[♪♫]\s*$\|^[♩♬♭♮♯]` |

But a simpler, more robust pattern that matches what's shown in your screenshot (♪ at start/end):

```
(^|\s)[♪♫].*[♪♫](\s|$)|^[♪♫]\s*$
```

**The cleanest practical regex for IINA:**

```
[♪♫]
```

This strips any subtitle line that contains a musical note character anywhere. Since `sub-filter-regex` removes the **entire line** if the pattern matches anywhere in it, this single character class is all you need.

---

**To add it in IINA:**

1. Open IINA → **Preferences** → **Advanced**
2. Find the **Extra mpv options** section (the table where you added `sub-filter-sdh`)
3. Click **+** and add:
   - **Name:** `sub-filter-regex`
   - **Value:** `[♪♫]`

> [!TIP]
> If you ever need to strip additional music symbols (♩ ♬ ♭ ♮ ♯), use `[♩♪♫♬♭♮♯]` as the value instead.

> [!NOTE]
> `sub-filter-regex` removes the whole cue line if the pattern matches. If a cue has multiple lines (e.g. a song lyric + a spoken line), mpv will drop the entire cue. This is generally the desired behavior for caption cleaning.

---

## User

are you sure?

---

## Assistant

Good catch — it's using `~/.config/mpv/`. The settings are in the mpv config file, not the IINA UI table. Let me look there:

Created At: 2026-07-29T18:28:43-06:00
Completed At: 2026-07-29T18:28:43-06:00

				The command completed successfully.
				Output:
				sub-filter-sdh=yes
sub-filter-sdh-harder=yes
# Enable regex sub filtering
sub-filter-regex-enable=yes

# Strip anything in square brackets like [muffling sounds] or [cheering]
sub-filter-regex-append=\\[.*?\\]

# Strip anything in parentheses like (whispering)
sub-filter-regex-append=\\(.*?\\)

There's the real config. It's already using `sub-filter-regex-append`. Just add one more line:

Created At: 2026-07-29T18:28:47-06:00
Completed At: 2026-07-29T18:28:47-06:00

				The command completed successfully.
				Output:
				sub-filter-sdh=yes
sub-filter-sdh-harder=yes
# Enable regex sub filtering
sub-filter-regex-enable=yes

# Strip anything in square brackets like [muffling sounds] or [cheering]
sub-filter-regex-append=\\[.*?\\]

# Strip anything in parentheses like (whispering)
sub-filter-regex-append=\\(.*?\\)

# Strip musical lyrics (lines containing ♪ or ♫)
sub-filter-regex-append=[♪♫]

Done. Added to [mpv.conf](file:///Users/matt/.config/mpv/mpv.conf):

```
# Strip musical lyrics (lines containing ♪ or ♫)
sub-filter-regex-append=[♪♫]
```

Restart IINA and any subtitle line containing a musical note will be silently dropped.

---

## User

ok so document this better please (mac environment md I guess?)

---

## Assistant

Let me find where that lives first:

Created At: 2026-07-29T18:29:05-06:00
Completed At: 2026-07-29T18:29:06-06:00

				The command completed successfully.
				Output:
				/Users/matt/projects/ai-os/.rules/mac_env.md
/Users/matt/./.cache/uv/environments-v2

Created At: 2026-07-29T18:29:09-06:00
Completed At: 2026-07-29T18:29:09-06:00

				The command completed successfully.
				Stdout:
				
				Stderr:

Created At: 2026-07-29T18:29:13-06:00
Completed At: 2026-07-29T18:29:13-06:00

				The command completed successfully.
				Output:
				---TAIL---
# macOS Environment Reference

## macOS Context & Automation
- Refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing software or scripting automation.
- **TCC Permission Reset:** When rebuilding ad-hoc binaries on macOS, run `tccutil reset Accessibility <bundle-id>` and `tccutil reset ListenEvent <bundle-id>` if permission prompts fail.
- **Hammerspoon Reload:** After modifying files in `qwerty-midi-hammerspoon`, run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

It's just a pointer — the real doc is `MAC_ENVIRONMENT.md`. Let me check it:

Created At: 2026-07-29T18:29:16-06:00
Completed At: 2026-07-29T18:29:16-06:00

				The command failed with exit code: 1
				Output:
				grep: /Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md: No such file or directory
---
wc: /Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md: open: No such file or directory

Created At: 2026-07-29T18:29:19-06:00
Completed At: 2026-07-29T18:29:21-06:00

				The command completed successfully.
				Output:
				/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md
/Users/matt/projects/ai-os/.agy-mcp/worktrees/job-7f1a74efbfca4784/docs/active/MAC_ENVIRONMENT.md
active
archive
fan-out-fan-in-agentic-pattern.md
habits_design.md
ideas
memory

Created At: 2026-07-29T18:29:24-06:00
Completed At: 2026-07-29T18:29:24-06:00

				The command completed successfully.
				Output:
				---TOTAL LINES:
     108 /Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md

No IINA section yet. Let me see the end of the file to find the right place to append:

Created At: 2026-07-29T18:29:28-06:00
Completed At: 2026-07-29T18:29:28-06:00
File Path: `file:///Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md`
Total Lines: 109
Total Bytes: 6688
Showing lines 1 to 109
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
<truncated 3568 bytes>
tigravity.app**
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
The above content shows the entire, complete file contents of the requested file.

Good — no IINA section yet, and there's a natural "Key Installed Applications" section to extend. I'll add a **Media Playback** subsection and a dedicated **IINA / mpv Config** section.

Created At: 2026-07-29T18:29:35-06:00
Completed At: 2026-07-29T18:29:35-06:00
Permission for write_file(/Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md) was already granted by user policy.

Created At: 2026-07-29T18:29:40-06:00
Completed At: 2026-07-29T18:29:40-06:00
Subagent "file_editor" defined successfully. It can now be invoked via invoke_subagent.

Created At: 2026-07-29T18:30:00-06:00
Completed At: 2026-07-29T18:30:00-06:00
Created the following subagents:
{
  "conversationId": "9307f7cc-f476-4fd3-9f1b-bc0c0001f88a",
  "logAbsoluteUri": "file:///Users/matt/.gemini/antigravity/brain/9307f7cc-f476-4fd3-9f1b-bc0c0001f88a/.system_generated/logs/transcript.jsonl"
}
The subagents will send you a message when they have completed their task or require guidance. There is no need to poll for their responses.

Waiting for the editor to finish…

Created At: 2026-07-29T18:30:04-06:00
Completed At: 2026-07-29T18:30:04-06:00
Wait cancelled (agent already has undelivered messages from 9307f7cc-f476-4fd3-9f1b-bc0c0001f88a).

Done. [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/active/MAC_ENVIRONMENT.md) now has:

1. **`### Media Playback`** bullet under *Key Installed Applications* — IINA noted as primary video player backed by mpv config at `~/.config/mpv/`

2. **`## IINA / mpv Subtitle Configuration`** section at the bottom with:
   - Where the config lives and why to edit the file directly (not the IINA prefs table)
   - A full table of every active filter (`sub-filter-sdh`, `sub-filter-sdh-harder`, all three `sub-filter-regex-append` patterns) with purpose column
   - Notes on how `sub-filter-regex-append` works additively and how to temporarily disable

---
