---
title: "Zed SSH Connection Error Troubleshooting"
date: "2026-08-05"
conversation_id: "f3943e72296cb67b"
source: "antigravity"
---

# Zed SSH Connection Error Troubleshooting

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-05 16:00 MDT-6] [context to this point is 0] @Flash trying to connect to a remote SSH project folder with Zed editor, and I'm getting this error.

---

## Assistant

It looks like you might have missed pasting the exact error message or output log!

Paste in the text or terminal error snippet you're seeing in Zed when trying to connect over SSH, and we can troubleshoot it.

---

## User

[2026-08-05 16:00 MDT-6] [context to this point is 65] failed to connect: unix_listener: path "/var/folders/qh/kq45r0096kgddmdkjqr2f1980000gr/T/tmp.ass1TdJedP/zed-ssh-sessionCrD5Iy/ssh.sock.zECD52S69KU32ybc" too long for Unix domain socket.

---

## Assistant

This error occurs because macOS (and Unix systems in general) has a strict character length limit for Unix domain socket paths (typically **104 or 108 characters**).

Because your macOS temporary directory path (`/var/folders/qh/kq45r00.../T/`) is already long, adding Zed’s nested session folder pushes the total path length past this limit, causing the SSH listener creation to fail.

Here is how to fix it:

1. Set `TMPDIR` to a Shorter Path (Quick Fix)

You can launch Zed from your terminal with a shortened temporary directory path so that socket paths remain under the character limit.

Run this command in your macOS Terminal:

Bash

```
TMPDIR=/tmp zed

```


If this resolves the issue, you can create an alias in your shell configuration (`~/.zshrc` or `~/.bashrc`):

Bash

```
alias zed="TMPDIR=/tmp zed"

```

2. Override OpenSSH Socket Pathing in `~/.ssh/config`

If Zed invokes `ssh` using your global SSH configuration, you can force OpenSSH control sockets to use a shorter path pattern.

Open your SSH configuration:

Bash

```
nano ~/.ssh/config

```


Add or update the `ControlPath` directive under `Host *` or your specific host entry:

Code snippet

```
Host *
    ControlPath /tmp/ssh-%r@%h:%p
    ControlMaster auto
    ControlPersist 10m

```

3. Configure `~/.zed/settings.json` (Zed-Specific)

If you have specific SSH settings configured inside Zed, inspect your Zed preferences (`Cmd + ,` or `zed: open settings` in the command palette) and ensure your SSH remote definitions aren't generating unusually long host aliases or session tags.

Would you like help setting up a permanent shell alias or SSH configuration fix?
Yes

---
