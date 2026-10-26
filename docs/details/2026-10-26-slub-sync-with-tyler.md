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
