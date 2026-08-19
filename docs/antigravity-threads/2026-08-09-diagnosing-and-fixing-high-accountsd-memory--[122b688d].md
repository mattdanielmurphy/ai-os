---
title: "Diagnosing and Fixing High `accountsd` Memory"
date: "2026-08-09"
conversation_id: "122b688d0cf6735d"
source: "antigravity"
---

# Diagnosing and Fixing High `accountsd` Memory

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-09 16:53 MDT-6] [context to this point is 0] accountsd 3.29 GB 2 260 588 matt 0.0 2:58:15.83 0 Apple 0.0 0.00 0 bytes 0 bytes 0 bytes Yes No Yes (null) No 0 bytes 0 0 bytes 0 0 bytes 0 bytes - 0 bytes 0 bytes No (null)




why is accountsd using so much memory?




Is there some app that makes it easy to get notified when processes are using too many resources for what they are?

---

## Assistant

Why `accountsd` Is Using ~3.3 GB of RAM

`accountsd` is the background daemon responsible for managing account credentials, tokens, and single sign-on authentication across macOS (iCloud, Apple ID, Mail, Contacts, Calendars, App Store, and third-party account integrations).

Normally, it should consume a tiny footprint (under 50–100 MB). When it reaches 3.29 GB, it is almost always due to one of three things:

**Authentication Retry Loop / Memory Leak:** An account (iCloud, Google Mail, Exchange, or a third-party app requesting system tokens) is stuck in an authentication loop. As `accountsd` handles thousands of rapid token or sync requests, an internal leak causes its memory to swell continuously.

**Database / Cache Corruption:** The local Accounts database (`~/Library/Accounts/Accounts3.sqlite`) or Keychain token store has corrupted entries, causing the daemon to repeatedly read and hold cached state in memory.

**Stuck Client Request:** An app querying the Accounts framework got into an unhandled state, causing `accountsd` to accumulate unreleased memory allocations.

How to Fix It
1. Kill the Daemon (Quick Reset)

`accountsd` is managed by `launchd`, so killing it will instantly free the RAM and restart the daemon clean:

Bash

```
killall accountsd

```


*(Alternatively, select `accountsd` in Activity Monitor and click the stop sign icon to force quit).*

2. Clear Corrupted Account Caches

If memory creeps back up after killing it, reset its database cache:

Bash

```
# Terminate the process
killall accountsd

# Clear local Accounts database cache (it rebuilds automatically)
rm -rf ~/Library/Accounts/Accounts3.sqlite*

```

3. Cycle Accounts

If the leak returns, go to **System Settings > Internet Accounts** (and **Apple ID / iCloud**), disable and re-enable Mail/Calendar sync, or toggle the offending account off and on to break the auth retry loop.

Apps to Alert You on Resource Hogs

If you want proactive notifications when a background process or app consumes excessive CPU or RAM:

1. App Tamer

**What it does:** Built specifically to watch background and foreground processes. You can set thresholds (e.g., alert or automatically throttle if an app uses >X% CPU or excessive RAM).

**Why it fits:** Unlike passive menu-bar monitors, App Tamer actively detects runaway background daemons and lets you limit or pause them automatically.

2. Stats (Free & Open Source)

**What it does:** A lightweight macOS menu bar system monitor.

**Alerting capability:** You can configure popup notifications for high memory pressure or CPU spikes directly from the menu bar preferences.

3. Custom `launchd` Watchdog Script

If you prefer a tailored, lightweight background daemon without third-party GUI software, you can run a simple periodic script with `launchd` that inspects process RSS/CPU via `ps` or `top` and sends a native macOS notification via `osascript`:

Bash

```
#!/usr/bin/env bash
# Threshold in KB (3 GB = 3145728 KB)
THRESHOLD=3000000

# Find processes exceeding memory threshold
ps -eo pid,rss,comm | awk -v limit=$THRESHOLD '$2 > limit && $1 != "PID" {print $0}' | while read -r pid rss comm; do
  mb=$((rss / 1024))
  name=$(basename "$comm")
  osascript -e "display notification \"Process $name (PID $pid) is using ${mb} MB of RAM.\" with title \"High Resource Warning\""
done

```

---
