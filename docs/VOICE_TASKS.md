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
- Only mail Matt's account **sent** counts (`in:sent subject:(Claude task)` + From check), so outside
  mail with that subject can't inject tasks.
- Delivery needs an unlocked screen: it shows the claude-control take-control banner (Esc cancels)
  and pastes into the project chat. Cancel or failure → emails stay, retry after 5 min.
- Logs: `tmp/voice-task-inbox/watcher.log`, `~/Library/Logs/launch-agents/voice-task-inbox.log`.
- Why not SendMessage to the coordinator: the coordinator is a cloud session; it isn't in
  `ListAgents` from a local session, and headless `claude -p` has no SendMessage/ListAgents at all.
  Only `mcp__claude-code-remote__send_message` with `@parent` from a live project thread reaches it.
- Gmail label "Claude tasks" exists; an optional filter (`subject:"[Claude task]"` → label, skip inbox)
  keeps the emails out of the inbox for the minute before they're trashed.
