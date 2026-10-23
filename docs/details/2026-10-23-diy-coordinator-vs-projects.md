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

## 07:35 Start sessions in sync with the Project, no takeover

Matt: wants to start sessions without taking over his Mac while still using the Project (the takeover was the reason he forgot).

---

### One CLI command does it

Docs (claude-code-on-the-web, "Send follow-ups from the CLI"): `claude -p "message" --cloud <session-id>` queues one message into any running cloud session from any logged-in machine and exits. `--output-format json` gives `{ok, session_id, url}`. No window, no paste, no take-control queue.

The project coordinator and cloud threads are cloud sessions (the coordinator relay names `session_0175dX...`), so `send_task` in `services/mac-connector` could call this instead of `scripts/voice_task_inbox.py` pasting into the chat.

---

### What's unknown until tested

- Whether a message queued this way shows in the project chat as Matt's message, and whether the coordinator treats it with his authority or as a relay.
- The coordinator's session id changes when it's recycled, so the connector needs a lookup (e.g. the coordinator's own `get_channel_session_id` written to a file, or a list of sessions).
- Installed CLI is 2.1.212 and has no `--cloud` flag yet; needs `claude update`.
- Errors if archived: `cloud session <id> is archived`.

---

### Test plan

1. `claude update`.
2. Send one harmless message: `claude -p "test from Mac CLI, ignore" --cloud <coordinator id> --output-format json`.
3. Check how it appears in the project and how the coordinator reacts.
4. If good: swap `send_task` to use it, keep the paste route as fallback.
Undo: revert the `send_task` change; the CLI update is harmless.
