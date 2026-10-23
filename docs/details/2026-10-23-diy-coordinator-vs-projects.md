# DIY coordinator vs Projects (2026-10-23)

## 07:15 Can a connector setup replace the Projects coordinator?

Asked (via coordinator): compare Projects mode with a DIY setup (chat or Claude Code + an MCP server that spawns background sessions, no Mac takeover). Research only, nothing changed.

---

### Background spawn works

Checked docs (code.claude.com: agent-view, headless, sessions, cross-session-messaging, remote-control):

- **Spawn**: `claude --bg --name "<title>" "<prompt>"` starts a session under a supervisor process. No terminal, no window, no screen input. Survives closing the shell and sleep; stops on shutdown. Idle unattached sessions get their process stopped after ~1h but resume on the next message.
- **List/state**: `claude agents --json` (documented as the scripting interface): state working/blocked/done/failed, status busy/waiting/idle, waitingFor.
- **Message a running session**: no `claude send` CLI. But every session binds an inbox socket (Unix socket); the docs say a script can post a line to it, and an idle session starts a new turn with it. Sessions in the agent list also message each other with SendMessage. `claude --resume <id> "<prompt>"` from a terminal also sends to a running bg session, but not from a script with piped output.
- **Wake the coordinator**: the `Notification` hook fires `agent_needs_input` / `agent_completed` for background sessions (docs say while agent view is open, so a long-lived `claude agents` may be needed). A hook script can post to the coordinator's inbox socket, which wakes it. That rebuilds Projects' "wake on thread event".
- Installed Claude Code is 2.1.212; much of this (attach by name, peek replies, notice-when-idle) is newer. Needs `claude update` first.

---

### What Projects still wins

- **Wakes for free** on every thread message, reaction and PR event; DIY only wakes on what hooks report.
- **Phone UI**: one chat with thread cards and statuses. DIY on the phone = the Code session list (Remote Control), no cards.
- **Cloud threads** that run with the Mac off. DIY sessions are Mac-only.
- **Shared project memory, routines, Custom view, Library/attachments.** DIY has memory files and launchd instead (already built).

---

### What DIY wins back

- Visual mods (bands, panes, toasts) and the `/` menu, because the coordinator is a Code-tab session.
- Read-aloud and voice: only if the front end is a regular claude.ai chat (the existing Mac connector already works there). A Code session has no voice mode.
- No Mac takeover: today `send_task` pastes into the project chat via the take-control queue. `--bg` + socket needs none.
- Full control over routing rules, no 16k instructions limit, no brief/relay overhead.

---

### Biggest gap: a chat can't be woken

A claude.ai chat (voice or regular) only acts when Matt speaks; it can poll (`check_updates`) but nothing pushes into it. So "chat as coordinator" can't react to threads finishing. The workable shape is: coordinator = a Code-tab session on the Mac with Remote Control (phone access), hooks wake it; voice chat stays a front door that drops tasks in.

Untested: whether `--bg` sessions also show up over Remote Control on the phone (the auto-connect setting covers interactive processes; docs don't say for bg).

---

### Build size

Small, on top of `services/mac-connector` (already an MCP server on his Mac):
- 4 tools: `spawn_session` (wraps `claude --bg`), `list_sessions` (`claude agents --json`), `message_session` (inbox socket), `read_session` (tail of transcript/peek). ~200-300 lines TS + tests.
- 1 Notification hook (~40 lines) that posts completions to the coordinator's socket.
- Coordinator prompt: port routing rules from `.rules/`.
- Roughly a day to a working prototype, a couple more days to trust it.

---

### Recommendation

Keep Projects as the main coordinator for now. Build the 4 tools as a side experiment, mainly to replace the screen-takeover `send_task`. Switch over only if a week of use shows the hook wake-ups are reliable. Rejected: chat-only coordinator (can't be woken); full rewrite now (big, and loses cloud threads + phone cards).
