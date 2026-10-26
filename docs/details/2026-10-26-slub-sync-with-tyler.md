# Keep Matt and Tyler in sync on Slub (2026-10-26)

## 19:45 One easy way to stop drifting apart

Matt asked (via the coordinator, before a call with Tyler): how to keep both of them in the loop on Slub so they don't build the same idea separately, given their systems already differ. Full merge comes later.

---

### What was already planned

- The Oct 23 thread planned a private `slub-utils` monorepo with Tyler as a collaborator (plan in `docs/details/2026-10-23-slub-utils-monorepo.md`). It was never created: `mattdanielmurphy/slub-utils` does not exist on GitHub today.
- The drift is real: Tyler's `tvresync` clashed with Matt's TV Re-sync (both on ⌃⌥R), and Tyler built `tvwake` on his own.
- The monorepo is a few hours of restructuring the live Hammerspoon suite, so it isn't a "before the call" fix.

---

### Recommended: shared slub-hq repo

A tiny private GitHub repo (`slub-hq`) with Tyler as a collaborator, holding:
- `NOW.md`: one line per thing either of you is building (who, what, date). Claude adds a line when work starts and removes it when done.
- `IDEAS.md`: Slub ideas (e.g. the walking-tour app), so an idea is visible before anyone builds it.
- `CLAUDE.md`: the shared rule, "before starting any Slub app or utility, pull slub-hq and check NOW.md and IDEAS.md; if it's there, ask first."

Why: both Claudes can read and write a repo from Code or Projects with no new tools, and it takes about 10 minutes. It later becomes the home of the shared rules when you merge systems.

---

### Other options

- Shared Linear team "Slub": nicer board and phone app, but Tyler needs a Linear account and his Claude needs the Linear connector.
- Build the monorepo now: solves code drift too, but hours of work and risky to the live suite; do it after the call.
- Rejected: a group chat or doc. Agents won't check it on their own, which is the whole problem.

---

### Projects vs your own Claude Code system

- The shared repo works the same whether you stay in Projects or move to plain Claude Code, so this choice doesn't block syncing with Tyler.
- If you both run Claude Code, the `CLAUDE.md` in slub-hq becomes a shared rulebook both agents load, the first real step toward one shared system.
- Untested: whether Tyler's Claude setup will reliably follow the rule; worth checking once on his Mac.

---

### Not done yet

Nothing created. Making the repo and inviting Tyler is an outward action, so it waits for Matt's 👍. Undo: archive the repo.

## 20:35 Slack vs Telegram for Matt and Tyler

Matt asked (via the coordinator, during his call with Tyler): Slack or Telegram for how the two of them talk and stay in sync, which agents can read and post to, given he may move to his own Claude Code system.

---

### What the call said

- Tyler likes Slack because you can @Claude in a message. Free plan limits he read out: messages older than 90 days are hidden, huddles are one-on-one only.
- Matt thinks Telegram would do the same and better.
- Both said, strongly: don't get locked into Claude. Tyler dropped the Claude Teams idea for that reason and wants sync to live in a shared GitHub repo that ports to any AI.
- Tyler's two tests: what is most future-proof, and what is easy to invite ~10 testers to in about three months. He leans to "tried and true, user-friendly" platforms.

---

### Recommendation in one line

Telegram group for Matt and Tyler, slub-hq repo as the agents' shared memory, and Discord later for testers. Skip Slack.

---

### Why not Slack

- The @Claude feature is Anthropic's Slack app: exactly the Claude lock-in both of you said you want to avoid.
- Free plan hides anything older than 90 days, from people and from bots/API. Decisions you made in month one vanish for your agents in month four. Paid is per-user per-month and grows with every tester.
- It's built for coworkers, not for a public tester community.

---

### Why Telegram for the two of you

- Free, unlimited history, great phone apps, and Matt already uses it daily.
- Matt already runs a Telegram bot gateway in ai-os (`services/assistant/`, morning check-ins, news, Codex routing). Adding a Slub group to that bot is small and model-agnostic: the bot can call Claude, GPT or an open-weights model, so switching AI doesn't touch the chat.
- The Bot API is the simplest of the three for agents to post to (one HTTPS call with a token).
- Catch: Telegram bots cannot see other bots' messages in groups, and only see messages sent after they join. So Matt's agent and Tyler's agent can't talk to each other through Telegram. That's fine because they talk through the repo.

---

### Why the repo stays the agent channel

- A chat is where people talk; agents don't reliably check it on their own. A git repo (`slub-hq`: NOW.md, IDEAS.md, CLAUDE.md) is read by any agent, any model, any harness, and has full history forever.
- Bridge: a tiny GitHub Action or the bot posts a line to the Telegram group when NOW.md changes ("Tyler's Claude started: tvwake"). Humans see it on their phone, agents read the file.

---

### Discord later, for testers

- When ~10 testers arrive, Discord is the tried-and-true home for audio/music software communities: free, unlimited history, channels and roles, voice rooms, very bot-friendly.
- Don't set it up now; it's overhead for two people.

---

### Options rejected

- Slack: lock-in and the 90-day wall (above).
- iMessage/WhatsApp/Signal: no clean bot access for agents (WhatsApp's API is business-only and paid; Signal has no official bot API).
- Matrix/Zulip self-hosted: most future-proof on paper but too much upkeep now.

---

### Untested / risky

- Not verified: whether Claude's Slack app works on Slack's free plan. Didn't matter for the recommendation.
- The bridge (NOW.md → Telegram post) doesn't exist yet; it's a small build after the repo exists.
- Nothing was created or sent. slub-hq and the Telegram group both wait on Matt's 👍 (outward actions involving Tyler).

## 20:50 slub-hq created

Matt 👍'd setting up slub-hq and a Slub Telegram group.

---

### What exists now

- Private repo https://github.com/mattdanielmurphy/slub-hq (local: ~/projects/slub-hq) with README, NOW.md, IDEAS.md, DONE.md, and the agent rule in CLAUDE.md plus an identical AGENTS.md (so non-Claude agents like Codex read it too, keeping it model-neutral as Matt and Tyler wanted).

---

### What's blocked

- Tyler isn't invited: I couldn't find his GitHub username anywhere on the Mac (not a collaborator on any of Matt's repos). Need it from Matt.
- Telegram group: bots can't create groups or add people, so Matt has to make the "Slub" group with Tyler in the Telegram app. I tried to look up Matt's existing bot's username to add to the group, but reading the bot token was blocked as credential access, which is correct. Matt can add his bot himself if he wants agents in the chat.
- Habit gate: no tap data was stored for today's practice page (doc 2026-10-26 missing), so nothing was scored. Done was recorded by the Mac side.

---

### Undo

Archive or delete the repo on GitHub; move ~/projects/slub-hq to Trash.

## 21:37 Shared Google Calendar

Matt asked (during the call): shared Google Calendar? Tyler asked on the call how either of them can add things.

---

### Answer

- Yes. Make one extra calendar called "Slub" inside Matt's Google Calendar (Settings > Add calendar > Create new calendar), then under that calendar's "Share with specific people" add Tyler's Google email with "Make changes to events". Both of them can then add, move and delete Slub events, and it shows on both phones next to their own calendars.
- Agents: Claude's Google Calendar connector can list and create events on any calendar Matt can see, so agents can add Slub meetings. It can't create the calendar itself, so that one step is manual. It's also model-neutral: any agent or app can reach Google Calendar.
- Rejected: an iCloud shared calendar (Tyler may not be on Apple; worse agent access).
- Not done: creating it. Matt is screen-sharing on a call, so I didn't drive his browser; and Tyler's Google email isn't on file.

## 22:03 Telegram bot on Claude without the API

Matt asked: can we add a Telegram bot that connects to Claude without using the Claude API?

---

### Answer: Claude Code Channels

- Yes. Claude Code has an official Telegram "channel" plugin (research preview). It runs inside a Claude Code session on Matt's Mac and uses his Claude subscription, so no API key and no API bills.
- Setup per official docs (https://code.claude.com/docs/en/channels): make a bot with Telegram's @BotFather, `/plugin install telegram@claude-plugins-official`, save the bot token with the plugin's configure command, restart with `claude --channels plugin:telegram@claude-plugins-official`, then pair. Only paired (approved) senders can reach it.
- Catches: needs a Claude Code session running on the Mac (it stops when that session stops); research preview, so it may change; not yet verified whether it works inside a group chat like Slub Club or only in direct messages.
- Lock-in check: the bot is Matt's own (BotFather token), so later the same bot can be pointed at another backend (his existing Telegram gateway with Codex, or an open-weights model) without Tyler changing anything.
- Not done: nothing installed. Needs Matt in Telegram for BotFather, and he's on a call.

## 22:06 One bot with fallback to Tyler's Mac

Matt asked: one bot that runs on his Mac, falling back to Tyler's Mac when his is unavailable?

---

### Answer

- Possible, but not built in. A Telegram bot can only be read by one computer at a time; if both Macs run it, Telegram rejects the second (409 Conflict) and messages get split or dropped.
- Small build: a standby script on Tyler's Mac checks every minute or so whether Matt's Mac is serving the bot (e.g. a heartbeat Matt's Mac writes to slub-hq or the VPS). If the heartbeat is stale, Tyler's Mac starts its own Claude Code Telegram session; when Matt's comes back, Tyler's steps down.
- Rejected: probing Telegram itself for the 409 as the health check, because the probe interrupts Matt's live connection.
- Catch: the fallback Claude only knows what's on Tyler's Mac, so both should keep shared context in slub-hq.
- Untested; nothing built yet.

## 22:15 Bot with failover built

Matt asked "why after the call?" Real cause: I assumed he was too busy on the call; there was no technical reason. Started immediately.

---

### What's built (slub-hq/bot)

- Installed Claude Code's official Telegram plugin (telegram@claude-plugins-official 0.0.7) on Matt's Mac.
- Group chats work: read the plugin source. Groups are opted in one by one and by default the bot answers only when @mentioned or replied to.
- `supervise.sh` runs every minute (launchd) on each Mac. Priority list matt then tyler. Heartbeats are one auto-edited comment per Mac on slub-hq issue #1 (collaborators can edit their own comments; a gist was rejected because Tyler couldn't write to Matt's gist; commits every minute were rejected as noise).
- Hand-back uses a "claim" step: the plugin gives up after ~8 failed 409 retries, so the two Macs must never poll at once.
- `session.sh` keeps `claude --channels plugin:telegram@claude-plugins-official` running in tmux, restarting it if it exits.
- `install.sh <name>` installs the plugin, asks for the token hidden (never shown to agents), and loads the launchd job.

---

### Tested

- Simulated two Macs on one machine: B alone starts; A returns and claims; B steps down; A starts; A goes stale; B takes over. All correct.

---

### Not tested / risks

- The real bot: no token yet (Matt has to make it in @BotFather).
- First launch in tmux may show the folder-trust prompt; I'll check the session after install.
- Tools outside the allowlist would make the session wait on a permission prompt nobody sees.
- `--channels` is a research-preview flag and isn't in `claude --help`.

---

### Undo

`launchctl bootout gui/$(id -u)/ca.slub.bot`, `claude plugin uninstall telegram@claude-plugins-official`, delete bot/ in slub-hq.
