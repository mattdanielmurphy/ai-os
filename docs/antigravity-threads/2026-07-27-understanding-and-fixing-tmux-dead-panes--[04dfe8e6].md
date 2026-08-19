---
title: "Understanding and Fixing Tmux Dead Panes"
date: "2026-07-27"
conversation_id: "04dfe8e63f4cf0e9"
source: "antigravity"
---

# Understanding and Fixing Tmux Dead Panes

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Note-Taking Directive: When asked to "make a note about this" OR if we discuss anything interesting or ideas about future projects, you MUST proactively output a JSON tool call to save it as a note, or update an existing note. The JSON must be inside a ```tool_call codeblock. Schema: {"tool":"save_note","args":{"title":"Note Title","content":"Markdown content...","update":false}}. The userscript will execute this automatically and save it to Development/Project Notes/.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-07-27 16:43 MDT-6] [context to this point is 0]




[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

I don't get how tmux works...

I have a pane running claude code, and I want to exit claude code and do somethign else; but when I close claude code with ctrl c or even doing /exit, it says pane is dead

---

## Assistant

That happens because the tmux pane was launched running `claude` directly as its root process, rather than launching an interactive shell (like `zsh`) that then ran `claude`.

In tmux, a pane exists **only as long as the command that created it is running**. When you exit Claude Code, that root command finishes, so tmux marks the pane as dead instead of dropping you back into a shell prompt.
Tmux pane showing the dead state. Source: GitHub

How to fix it right now

If you're currently staring at a `Pane is dead` screen:

**To close the dead pane entirely:** Press `Ctrl+b` then `x` (and type `y` to confirm).

**To respawn a fresh shell inside that exact same pane:** Press `Ctrl+b` then type `:respawn-pane -k` and press **Enter**.

How to prevent it from happening again

When spawning new tmux windows or splitting panes, make sure tmux starts a shell instead of launching single-purpose CLI apps directly.

**Launch a shell first, then run your command:**
Create a standard window/pane (which boots your default `zsh` session) and type `claude` manually. When you exit Claude Code, you'll drop right back to your command prompt.

**If launching via scripts or `tmux split-window`:**
Instead of running:

Bash

```
tmux split-window 'claude'

```


Wrap it inside a shell session:

Bash

```
tmux split-window 'zsh -c "claude; exec zsh"'

```


The `exec zsh` trick ensures that even after `claude` terminates, a fresh shell replaces it immediately so the pane stays active.

**Global tmux setting (Optional):**
If you never want dead panes to stick around under any circumstance, add this to your `~/.tmux.conf`:

Code snippet

```
set -g remain-on-exit off

```


This forces tmux to automatically destroy the pane the moment its process closes, rather than freezing on the "Pane is dead" notice.

Want to fix a script or keybinding that is spawning these dead panes?
Yes

---

## User

Please summarize this entire thread and save it as a note. Output a `save_note` tool call.

---

## Assistant

▶
 ⚡ Save note: "Tmux 'Pane is Dead' Cause and Solutions"
Running…

---
