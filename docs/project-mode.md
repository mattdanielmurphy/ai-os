# Claude Project mode: what it is and the trade-offs

Written 2026-10-20 from how this project actually runs (what the agents in it can see and do).
Things I inferred rather than checked are marked *(inferred)*.

## What it is
- **A group chat with Claude in it.** One page: a main feed (the project chat), and any message can grow a thread.
- **Two kinds of Claude.**
  - **Coordinator**: always attached to the project chat. It reads every message, decides what each one is, keeps project memory, and starts threads. It does almost no real work itself.
  - **Thread Claudes**: one per thread. Each is a full Claude Code session that does the actual work (code, files, research, PRs) and reports back in its thread.
- **Where a thread runs.** Either in a cloud container (fresh clone of a repo, no access to your Mac), or on your Mac over **Remote Control** (real Claude Code with your shell, files, `~/.claude` skills and CLAUDE.md). This thread is the Mac kind.
- **Shared pieces.** Project memory (notes every Claude reads), project instructions (your rules), a shared file folder (cloud threads), published artifacts, PRs, and routines (scheduled runs).

## The problem it's meant to solve
- **Long-running, async work.** You drop an ask from your phone between classes, walk away, and come back to a result. No need to babysit one terminal session.
- **Many things at once without one giant session.** Each task gets its own thread with its own context, so one huge thread doesn't bloat and degrade.
- **One place to see everything.** The feed shows every task, its status, its outputs (PRs, files, artifacts) and what's waiting on you.
- **Memory that outlives sessions.** The coordinator is replaced regularly, but project memory and the feed carry over.

## Trade-offs
| You get | You pay |
|---|---|
| Phone-friendly, async, parallel threads | Each new thread starts **cold** and re-learns context; that's where the "dumb questions" come from |
| Coordinator triages everything | It wakes on every message, which costs some tokens even when the answer is "nothing to add" |
| Cloud threads keep working when your Mac sleeps | Cloud threads **can't see your Mac**: no files, skills, Reminders, QMD |
| Remote Control threads have your full Mac setup | They need the Mac awake and the app running; a worktree can only be chosen when the thread starts |
| A fixed, clean UI | You **can't customize it**: no Code-mode panels, no live context meter |
| Memory shared by every Claude | Memory only works if kept small (an index, not a dump); the coordinator has to trim it |
| Safety checks on risky steps | Some normal steps get blocked (today: pushing to `main`), and you get asked to approve |

## Compared to Hermes *(inferred from shelf/ and old configs)*
- **What Project mode gives you that Hermes did:** an always-on agent you message from your phone, task delegation to sub-agents, persistent memory, scheduled jobs.
- **What it adds:** threads you can open and steer one by one, PRs and artifacts tracked in one feed, and no server of your own to keep alive.
- **What Hermes had that this doesn't:** any model provider (Gemini, Codex, etc.), Telegram as the chat surface, and full control over the code and UI.
- **Net:** Project mode covers the "personal assistant I text" part of Hermes without the upkeep. It isn't a fit for multi-model routing or custom UI.

## How to get the most from it
- **Run threads on your Mac (Remote Control) by default** so they know your files and setup.
- **Keep `docs/ABOUT_MATT.md` current** so cold threads stop asking about you.
- **One topic per thread**, and start a fresh one (with a handoff) when it gets long.
- **Use Code mode** for long, hands-on sessions where you want your panels and the context meter.
