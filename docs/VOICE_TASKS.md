# Voice tasks: voice chat → project coordinator

Voice Claude (Claude app voice chat) has no direct line to the Everything project: voice
mode only exists in chat, and chat's tools are connectors (Gmail, Notion, Craft, Claude
Docs), not projects. So voice Claude emails the task to Matt, and his Mac passes it on.

```
voice Claude --Gmail--> Matt's own inbox --IMAP, every 60s--> scripts/voice_task_inbox.py
   --> Hey Claude's Hammerspoon paste (bin/hey-claude send_to_claude) --> Everything project chat
   --> coordinator handles it like any message from Matt; email moved to Gmail Trash
```

## Paste this into voice chat

> **How to send my tasks to my project coordinator**
>
> When I ask you to hand something to "the project", "the coordinator" or "my Mac", or say "send that as a task", email it. Don't ask me to confirm each one.
>
> 1. Send one email per task, from my Gmail to my own Gmail address (the same account you send from). Never send it to anyone else.
> 2. Subject: `[Claude task] <short title>`. Keep the bracket tag exactly like that; it's how my Mac finds it. Keep the title under 8 words.
> 3. Plain-text body, in this order:
>    - **Ask:** what I want, in my own words where you can.
>    - **Context:** anything from our conversation the coordinator needs (names, links, decisions, what I already tried). Write it so someone who didn't hear us can act on it.
>    - **Urgent:** yes or no.
> 4. No signature, and don't reply inside an old email thread; start a new email each time.
> 5. Then just tell me "Sent to your project." Within about a minute my Mac posts it into my project chat and moves the email to Trash. If my Mac is asleep or locked it waits and goes through when I'm back.

## For agents

- Watcher: `scripts/voice_task_inbox.py` (launchd `com.matt.agent.voice-task-inbox`, every 60s).
  `--dry-run` lists pending tasks; `install` / `uninstall` manage the agent.
- Credentials: `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` (Google app password) in `~/projects/ai-os/.env`.
- Only mail Matt's account **sent** counts (`in:sent subject:(Claude task)` + the `\Sent` label), so
  outside mail with that subject can't inject tasks. No From check: Gmail sends as his domain alias.
- Delivery happens right away when the screen is unlocked (no idle wait since 2026-10-21): the
  take-control banner shows first (Esc cancels), and a draft in the project chat box blocks it.
  Cancel or failure → tasks stay, retry after 5 min.
- Logs: `tmp/voice-task-inbox/watcher.log`, `~/Library/Logs/launch-agents/voice-task-inbox.log`.
- Why not SendMessage to the coordinator: the coordinator is a cloud session; it isn't in
  `ListAgents` from a local session, and headless `claude -p` has no SendMessage/ListAgents at all.
  Only `mcp__claude-code-remote__send_message` with `@parent` from a live project thread reaches it.
- The watcher acts as the Gmail filter: on each run it moves task emails out of the inbox into the
  "Claude tasks" label (X-GM-LABELS), so no Gmail settings rule is needed.

## Faster route: the Mac connector (MCP)

`services/mac-connector` is a custom connector voice Claude can call directly: search notes, read
files and `send_task` (seconds instead of the 60s mail poll). Gmail stays as the fallback. When the
connector is on, voice Claude should prefer `send_task` over email.

## Saving calls

- `save_call` (connector tool): voice Claude runs it at the end of a call. It writes
  `Voice calls/<date> <time> <title>.md` in the Obsidian vault (summary, new facts, to-dos, what Matt
  said), runs `qmd update`, and queues one coordinator task to file facts and act on to-dos.
- `scripts/pull_voice_chats.py` (launchd `com.matt.agent.voice-chat-pull`, daily 3:30): copies every
  claude.ai voice chat (`platform == "VOICE"`) to `Voice calls/Transcripts/` via Matt's signed-in
  Chrome (browser-use CDP, claude.ai's internal API). Calls without a save_call go to the coordinator
  for review.
- Line for claude.ai Settings → Profile → preferences: "In voice chats, at the end of every call (or
  when I say bye / that's it), run the My Mac connector's save_call before you finish."

## Voice Claude speech quirks (tested 2026-10-21)

- Speed: `set_voice_mode_session_speed`, slowest is 0.8x. No timed silences.
- Pauses: single ellipses between words (`The... moon...`) or spaced double ellipses (`The... ... moon`) add pauses cleanly.
  Triple spaced ellipses glitch the British voice (a stray "art" before each word, once a made-up sentence). Hyphens did little.
- Matt found the slow 0.8x pace calming at bedtime.

## Reviewing calls

Unsaved calls queue a "Review unsaved voice calls" task; handle it with the `_review-voice-calls` skill
(`skills/_review-voice-calls/SKILL.md`, helper `scripts/review_voice_calls.py`).

## Replies back to voice Claude

Voice Claude can't be pushed to; it only acts when Matt speaks. So replies ride on the connector:
- An agent finishing a voice task runs `python3 ~/projects/ai-os/scripts/voice_reply.py "<title>" "<result>"`
  (the pasted task text says so). It lands in `tmp/voice-outbox/`.
- Every connector tool result carries any new replies, and the connector's instructions tell voice Claude
  to call `check_updates` (instant) at the start of each reply after it sent a task, so Matt hears the
  result on his next sentence. `wait_for_update` (≤50s) is for "I'll wait for it".
