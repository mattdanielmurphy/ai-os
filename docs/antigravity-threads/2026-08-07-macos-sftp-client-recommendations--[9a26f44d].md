---
title: "macOS SFTP Client Recommendations"
date: "2026-08-07"
conversation_id: "9a26f44d0afbcd87"
source: "antigravity"
---

# macOS SFTP Client Recommendations

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-07 12:17 MDT-6] [context to this point is 0]




[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```







[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

SFTP clients for macos? Maestral cant do it right

---

## Assistant

Maestral is strictly an open-source Dropbox client, so using it for general remote connections or SFTP won't work.

Here are the best SFTP clients for macOS, broken down by how you like to work:

1. Top Premium Mac-Native Clients
**Transmit 5** *(by Panic)*

**Best for:** The gold standard standalone Mac file transfer experience.  
Empiric Apps

**Highlights:** Native macOS UI, Keychain integration, multi-pane navigation, sync rules, fast transfer engine, and support for SFTP, WebDAV, S3, and cloud hosts.  
AlexHost

**Pricing:** Paid ($45 one-time, 7-day trial).  
AlexHost

**ForkLift 4** *(by BinaryNights)*

**Best for:** Dual-pane file management + SFTP server browsing in one tool.  
Empiric Apps

**Highlights:** Functions as both a full Finder replacement (batch renaming, folder comparison) and an SFTP/remote client.  
AlexHost

**Pricing:** Paid ($29.95).  
AlexHost

2. Best Free & Open-Source Clients
**Cyberduck**

**Best for:** A lightweight, reliable GUI client without license fees.  
SFTP To Go

**Highlights:** Native macOS Keychain support, drag-and-drop, bookmarking, and Cryptomator encryption support.  
SFTP To Go

**Pricing:** Free / Open Source (Donationware).  
Empiric Apps

**FileZilla**

**Best for:** Heavy-duty queue management and cross-platform consistency.  
AlexHost

**Highlights:** Site Manager, active/failed transfer queues, deep directory browsing.  
AlexHost

**Pricing:** Free. UI feels dated compared to Transmit or ForkLift, but it gets the job done reliably.  
FileZilla
+ 1

3. Mount Remote SFTP Drives Directly in Finder

If you want your SFTP server to appear like a native folder or mounted volume in macOS Finder:

**Mountain Duck** *(by the creators of Cyberduck)*: Mounts SFTP servers as local disk volumes directly in Finder.

**rclone (`rclone mount`)**: CLI-based free tool that lets you mount remote SFTP, SSH, or S3 targets anywhere in your local file tree.

4. Built-in Terminal Tools (Zsh)

If you already use SSH keys in `~/.ssh/config`, you don't necessarily need a GUI:

Bash

```
# Direct SFTP session using existing SSH configuration
sftp username@hostname

# Sync directories over SSH/SFTP via rsync
rsync -avz -e ssh ./local-dir/ username@hostname:/remote-dir/

```

Where would you like to go next?
Configure ssh config for seamless terminal SFTP
Set up rclone to mount an SFTP server in Finder

---

## User

[2026-08-07 12:18 MDT-6] [context to this point is 763]




[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```

so I just want something that mounts a drive on my mac and ideally is able to set files to stay downloaded but otherwise just has things available on cemand

---

## Assistant

What you're describing—files staying on the remote server, showing up in Finder on demand, downloading only when opened, and letting you right-click to **"Keep Offline Always"** or **"Free Up Space"**—is known as **Smart Synchronization** or the **macOS File Provider framework**.

The Top Pick: Mountain Duck

**Mountain Duck** (built on the Cyberduck core) is the cleanest implementation for SFTP on macOS for this specific requirement.  
Apple

**How it works:** It hooks into macOS's native `File Provider` system (the same system Dropbox and OneDrive use in `~/Library/CloudStorage/`).

**On-Demand Access:** Your entire SFTP filesystem is listed in Finder, taking up zero disk space until you open a file.

**Pinning Files:** You can right-click any file or folder in Finder and select **"Keep Offline"** (it downloads and stays synced) or **"Make Online Only"** (purges local cache to free space).  
Apple

**Protocols:** SFTP, WebDAV, S3, FTP, and standard cloud providers.  
Apple

Alternative: ExpanDrive

**ExpanDrive** is another strong option that operates similarly.  
ExpanDrive

**How it works:** Maps SFTP as a native network drive using the macOS File Provider extension.  
ExpanDrive

**Features:** Supports background caching, SSH agent integration (`~/.ssh/config` / `ssh-agent`), and on-demand file streaming.  
ExpanDrive

Free / DIY CLI Option: `rclone mount`

If you prefer an open-source option, you can use `rclone` with VFS caching:

Bash

```
rclone mount my-sftp-server:/ /Users/matt/SFTP-Drive \
  --vfs-cache-mode full \
  --vfs-cache-max-age 24h

```


**Behavior:** Reads files on demand and caches them locally during access.

**Drawback:** It doesn't give you native Finder right-click context menu options to "pin" specific files for offline availability like Mountain Duck does.

Recommendation

If you want **native Finder icons, right-click pinning, and full integration with macOS File Provider**, **Mountain Duck** is the most polished option for SFTP.

---
