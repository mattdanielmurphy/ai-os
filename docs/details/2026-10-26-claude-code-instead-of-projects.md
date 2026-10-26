# Could Claude Code replace Projects? (2026-10-26)

## 01:10 Inventory, mapping, recommendation

Asked (via the coordinator): Matt is frustrated with Projects friction (the Everything Shelf thread viewer can't update itself because thread lists have no public API) and wants to know whether he could rebuild everything he likes about Projects with Claude Code on his Mac instead of chat mode. He's moving to Chrome over Claude.app. Discuss only: project freeze, build nothing.

Read first: the earlier thread "Coordinator vs DIY connector" and its details file `docs/details/2026-10-23-diy-coordinator-vs-projects.md` (which found `claude --bg` background sessions and `claude -p … --cloud <id>` no-takeover messaging, and made `send_task` use the latter). Checked the installed CLI today: Claude Code 2.1.308 has `--bg`, `claude agents --json`, `attach`, `--remote-control`, `--cloud`. Nothing was changed.

---

### Short answer

Yes for almost everything, with three real gaps: emoji reactions, the phone's one-chat-with-cards view, and threads that run while the Mac is off. The surprise is that the Claude desktop Code tab already has a native coordinator pattern (a session that starts linked sessions and gets a note when each one finishes), so the DIY version is smaller than it sounds.

---

### What Projects gives you, and the Claude Code version

| Projects feature | Claude Code equivalent | Status |
|---|---|---|
| Coordinator that routes to threads | A long-lived Code session with your routing rules; it starts linked sessions (desktop `start_session`) or `claude --bg` sessions | Have it today |
| Coordinator wakes when a thread finishes | Desktop app sends the parent a note when a linked session ends a turn; for `--bg`, a Notification hook posts to the coordinator's inbox | Have it (desktop) / small build (bg) |
| Threads on your Mac (Remote Control) | Every Code session is already on your Mac; `--remote-control` makes it reachable from phone and claude.ai/code | Have it |
| Thread list you can read and build on | `claude agents --json` lists every session with state (working, blocked, done). This is the public API the Shelf is missing | Have it; this fixes the Shelf |
| Project memory | Your memory folder, CLAUDE.md, `.rules/`, QMD | Have it (better, no 16k limit) |
| Project instructions | `.rules/` compiled into CLAUDE.md | Have it, no size limit |
| Phone access | Claude mobile app's Code tab shows Remote Control sessions | Have it, but as a session list, not one chat with cards |
| Notifications | PushNotification tool (phone push), plus your Hammerspoon toasts | Have it |
| Emoji quick replies | No reactions in Code sessions | Gap: short text replies ("y", "next") or your own front end |
| Checklists and thread cards | Code sessions have task lists; no card view across sessions | Gap without your own front end |
| Cloud threads (Mac off) | `claude --cloud` sessions exist, but they don't report back to a Mac coordinator | Partial gap |
| Routines / scheduled check-ins | launchd + `claude -p`, or cloud routines | Have it |
| Library / attachments | Project folder files, pages on Vercel | Have it |
| Read-aloud | Not in Code sessions; the claude.ai chat keeps it | Gap (keep voice chat as a front door) |
| Mods (bands, panes, toasts) | Work in the desktop Code tab, not on the web | Won back, but only in Claude.app, not Chrome |

---

### The Chrome catch

Moving to Chrome and leaving Claude.app pull in opposite directions. In Chrome, Code sessions open at claude.ai/code, which shows Remote Control sessions from your Mac, but mods don't draw there and there's no linked-session note system. So in Chrome you'd want your own small front end: a page (pages.test) that reads `claude agents --json`, shows each session as a card with its state, and has emoji buttons that send "yes", "next", and so on into a session. That page is also the self-updating Shelf.

---

### Recommendation

Go hybrid, in three steps, and only after the freeze lifts:

1. **No-build trial (an afternoon).** Run one desktop Code session as the Slub Utils coordinator, using its built-in linked sessions. Keep the Everything project for everything else. If the wake-ups and phone access feel right, continue.
2. **Small build (about a day).** Add `spawn_session`, `list_sessions`, `message_session` to the Mac connector (designed on 2026-10-23), plus one hook that tells the coordinator when a background session finishes. Then voice chat and the phone can feed it without a takeover.
3. **Own front end (a few days, optional).** The Chrome page above with cards, statuses and emoji buttons. This is what replaces the Projects page and the Shelf. Only worth it if steps 1-2 stick.

Rejected: switching everything at once (loses cloud threads and the phone card view on day one, and you'd rebuild your routing rules under pressure); staying on Projects only (the Shelf and other API walls won't go away).

---

### Untested and risky

- Whether `--bg` sessions appear on the phone over Remote Control (still untested from 2026-10-23).
- Whether the desktop linked-session notes reach a coordinator you are viewing from Chrome or the phone (they're a desktop app feature).
- The Notification hook for `--bg` sessions may only fire while `claude agents` is open; needs a check.
- Undo: nothing to undo; nothing was built.
