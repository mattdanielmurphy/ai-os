---
title: "Tmux Read-Only Attach Mode"
date: "2026-08-10"
conversation_id: "11db57cdb5bd95bc"
source: "antigravity"
---

# Tmux Read-Only Attach Mode

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-10 16:41 MDT-6] [context to this point is 0] possible to tmux attach in a read-only way so I can't accidentally enter input?

---

## Assistant

Yes, you can attach to a tmux session in read-only mode using the `-r` flag.

How to use it

Run the following command in your terminal:

Bash

```
tmux attach-session -r -t <session_name_or_id>

```


Or simply:

Bash

```
tmux a -r

```

Key Details

**Blocked Keys:** In read-only mode, any key combinations or typing you attempt will be ignored by the session.

**Detaching:** You can safely exit the read-only view without affecting the running session by pressing **`Ctrl+b`** followed by **`d`**.

---
