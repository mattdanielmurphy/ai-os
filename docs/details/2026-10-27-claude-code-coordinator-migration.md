# Moving the coordinator from Projects to Claude Code (2026-10-27)

## 22:30 Research: threads that never need a handoff, and a DIY coordinator

Matt asked (Code tab): he has decided to try leaving the "Everything" project for Claude Code with our own setup. Keep the best of the Projects coordinator (one place to ask, it routes and picks the model) plus everything from ai-os. He wants a thread to just keep going: no visible handoffs, and if he writes into an expired thread, the handoff (if any) happens behind the scenes in the same interface. Failing that, the handoff should happen automatically and the new thread open by itself. New word: a **chain** is a set of threads linked by handoffs. Research first; he has questions of his own still to come.

Nothing was built. This entry is research and a proposed plan.

What I read first:
- `docs/details/2026-10-23-diy-coordinator-vs-projects.md` (`claude --bg`, `claude agents --json`, inbox sockets, `claude -p --cloud`).
- `docs/details/2026-10-26-claude-code-instead-of-projects.md` (feature-by-feature mapping, hybrid plan).
- The 2026-10-22/23 cold-handoff evaluation and benchmark thread (session `8ef9547e`): resume vs handoff, measured on real threads.
- `docs/coordinator/project-instructions-slim.md`, the coordinator routing rules in `.rules/core_safety.md`, and the `context-alert` mod (`mods/context-alert/hooks/register.tsx`).
- Claude Code docs and changelog (sources at the end), and Claude Code 2.1.308 as installed.


---

### Same thread, no handoff

**Short answer: yes, this is possible in the desktop app, and it doesn't need handoffs at all for an expired cache.**

- **Claude Code already does this, but only in the terminal.** Since v2.1.299 (Oct 14), "a 200K+ token conversation left idle for about 54 minutes is compacted before its one-hour prompt cache expires, so your next message doesn't reprocess it all". The thread keeps its identity and continues from a summary. Settings: `idleCompaction` (on/off), `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` (the 200K floor).
- **It never runs in the desktop app.** The docs say "in a terminal session", and the Oct 23 benchmark found it had fired 0 times across 230 transcripts on this Mac, all of which run through the desktop app.
- **Our mod can do the same thing in the desktop app.** The mods API has `$.session.compact({ instructions })` ("the same call `/compact` makes", works between turns) and `$.session.usage()` (context size, free to call). So `context-alert` can watch each thread, and at about 50 minutes idle, while the cache is still warm and cheap to read, compact a big thread with instructions like "keep every rule and correction Matt gave word for word, the current task and the next step". When Matt writes again, the same thread simply continues.
- **Why compacting while warm is the cheap moment:** reading a warm 250k context costs a tenth of normal input; re-reading it after expiry costs a 1-hour cache write (twice normal input). The docs warn that compacting right after a cold resume is the expensive case, so the timing matters.
- **Auto-compaction still covers the other limit.** When a thread nears its context window, Claude Code compacts it automatically (`autoCompactEnabled: true` here). Together, a thread can run indefinitely.

What this means for **chains**: if threads compact in place, most chains collapse into one thread. A chain then only appears when work is deliberately moved to a new thread (a different folder or project, or a split), and the coordinator records the link.


---

### Resuming beats handoff below 250k

The premise "obviously I want a handoff if the cache expired" doesn't hold up in the data.

- **Benchmark on 6 real cold threads (Oct 23):** resuming scored 7.5/10 on recall (always 6–8); the Sonnet handoff scored 5.8 (2–8, one handoff took a declined message as its new task). Mean cost: resume $1.63, handoff $1.29 at list price.
- **Cost depends on size:** below about 200k tokens the two cost about the same; above about 250k the handoff saves roughly $0.90.
- **The current handoff writer is nearly blind in project threads:** `cold_handoff.py` drops tool calls when exporting, and in a project thread Claude's replies are tool calls, so Sonnet saw only 2–13k characters of 200–290k-token threads.
- **Measured again today (threads since Oct 20):** 70 cold resumes in project threads, median context 220k, 43 of them over 200k. Code-tab threads had only 2 cold resumes.

So the best order is: compact while warm (no cost spike, keeps the thread); if a thread goes cold anyway (Mac asleep, app closed), resume it below ~250k; only above ~250k move to a fresh context, and even that can happen in the same thread (see below).

**Same-tab fallback for a big cold thread (needs a test):** a mod can intercept a prompt before it reaches the model (`prompt.submit` → `{ drop }`), run Sonnet on the transcript file outside the session, then submit the brief plus Matt's message back into the same session (`$.prompt.submit({ text, asUser: true })`). Whether the mod can also clear the old context first (`$.command.run` with `/clear`) is not documented; if it can't, the fallback is a new session opened automatically.


---

### Leaving Projects saves on every thread

- **A fresh project thread starts at a median of 134k tokens; a fresh Code-tab thread at 60k** (353 project threads and 71 Code threads since Oct 20, first request each).
- That ~74k difference is paid on every new thread and on every cold resume. At last week's pace it dwarfs what any handoff saves.
- Projects' coordinator also works "from recent messages, recent threads, and project memory rather than its full history" (docs), and every cloud thread gets project instructions capped at 16k. Our own coordinator has neither limit.
- The 30-threads-per-coordinator-chat cap that hit on Oct 27 is a Projects limit; nothing in the Code tab docs mentions one (not verified).


---

### Coordinator parts already in the Code tab

The desktop Code tab already has most of a coordinator built in. A session (the coordinator) can:

- **Start threads** with `start_session`: title, folder (`cwd`), worktree or not, permission mode, and **model and effort** (same family as the coordinator or cheaper). These are "linked sessions" shown as rows in the sidebar.
- **Be woken when a thread finishes**: the app continues the parent session with a note quoting the thread's report whenever a linked session ends a turn. This is Projects' "wakes on thread events".
- **Send follow-ups to a warm thread** with `SendMessage` (arrives as a labelled message, starts a turn if idle).
- **Switch a thread's model** (`set_session_model`), **rename** it, **archive** it, file it in **sidebar groups** (a group per area or chain), **pin** it, mark it **unread** (= waiting on you).
- **Clear an idle thread it started** (`clear_session`, the `/clear` command) and send it a brief, so a fresh context lives in the same sidebar row. Refused while Matt has that thread open on screen or pinned.
- **Reach the phone**: Remote Control serves desktop sessions to the Claude mobile app and claude.ai/code.

Also available, but not the first choice:
- **Agent teams** (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`): a lead with teammates, shared task list, idle notifications. Teammates aren't restored after a resume and live inside the lead's process, so they don't suit a coordinator that runs for weeks.
- **Agent view / `claude --bg`** (research preview): background sessions under a supervisor, `claude agents --json` for state, inbox sockets for scripts. Terminal-native, so it gets idle compaction for free, but it loses the desktop app's mods, panes and browser. Plan B if the desktop route disappoints.


---

### What Projects does that we'd rebuild

| Projects feature | Our version | Status |
|---|---|---|
| One conversation that routes everything | A pinned "Coordinator" Code session in `~/projects`, with the routing rules from `.rules/` | Have the parts |
| Picks thread model and effort | Coordinator picks per task using `claude_pace.py` (Opus by default, Sonnet when the week runs hot or the task is tiny) | Have the parts |
| Reuses warm threads, starts new ones otherwise | Same rule as today (scope, last turn < 45 min, < ~40 messages), but cold threads are resumed below ~250k instead of handed off | Rule change |
| Wakes when threads finish | Desktop linked-session notes | Built in |
| Overview: working / waiting on you / ready / idle / resolved | Sidebar groups, unread dots and pins; later the Shelf reading a local registry | Partly built in |
| Project memory and instructions | `.rules/`, CLAUDE.md, memory, QMD | Have it, no 16k cap |
| Phone access | Remote Control | Have it, but as a session list, not cards |
| Emoji quick replies | Mod band buttons on the Mac; typed "👍" on the phone | Gap on phone |
| Cloud threads that run with the Mac off | `start_session` with `target: "cloud"` for tasks that only need GitHub | Partial (no local files) |
| Thread limit per coordinator chat (~30) | None known | Better |


---

### Proposed design

1. **Threads that never go cold (mod).** In `context-alert`: at ~50 min idle, if the context is over a threshold (start at Anthropic's 200k; a Tweaks knob), call `$.session.compact` with instructions that keep Matt's rules, corrections, current task and next step. Show a small corner note "compacted while idle". Drop the hold-and-👍 flow for cold threads under ~250k: they just resume. Above ~250k and cold: same-tab brief if the mod can clear, else open a new session automatically. This also helps today, because project threads on the Mac run in the desktop app and load the same mod.
2. **The coordinator (one Code session).** Pinned, Remote Control on, runs on Opus at low effort (it must be Opus to start Opus threads). Its prompt is the routing section of `.rules/` plus a small registry file it keeps (thread id, title, chain, area, folder, model, state, last turn), so its own compactions never lose track of open threads.
3. **Front doors.** Voice tasks (`send_task` in the Mac connector) post to the coordinator instead of pasting into the project chat; the Shelf reads the registry instead of hearthbot.
4. **Trial side by side** for a few days with Everything still running, then switch.


---

### Build steps

1. **Idle compaction in the mod** (an hour or two, plus a real test on one big thread). Highest value, smallest change, works before any migration.
2. **Coordinator session** (an afternoon): routing prompt, registry, pace-based model choice, a test with three real tasks.
3. **Front doors and Shelf** (a day): voice inbox to the coordinator, Shelf on the registry.
4. **Benchmark compaction vs resume** with the existing bench method, so the 200k / 250k thresholds come from data.


---

### Keeping it portable

Matt's worry is lock-in, especially for Slub. What keeps this flexible:

- **The brain stays in plain files**: rules in `.rules/` (already compiled into CLAUDE.md, AGENTS.md for Codex and GEMINI.md), the thread registry as JSON, briefs and details as markdown. Any agent can read them.
- **Harness-specific calls stay thin**: `start_session`, `SendMessage` and the mod are the only Claude-Code-only parts; a Codex or Gemini CLI adapter could use the same registry later.
- **Stay inside the official harness for subscription use**: Anthropic restricted Opus on subscriptions through third-party tools (OpenCode, OpenClaw) earlier this year, and `--bare` / Agent SDK paths authenticate with an API key. Building on Claude Code itself avoids that wall; a custom SDK app would bill at API prices.
- Projects, by contrast, keeps the coordinator's behaviour, thread list and limits on Anthropic's side, with no public API (the Shelf problem).


---

### Untested and risky

- Whether a mod's timer fires while a desktop session sits idle and unfocused, and whether the app keeps that session's process alive. If not, compaction needs a different trigger (e.g. a launchd job that messages the session, which would cost a turn).
- Whether `$.command.run` can run `/clear` from a mod (needed for the same-tab fallback on big cold threads).
- Quality of compaction summaries vs full resume: not measured yet (step 4).
- Whether linked-session wake-ups reach the coordinator when Matt is talking to it from the phone over Remote Control (it runs in the desktop app, so probably yes).
- Compaction on threads Matt never returns to is wasted usage; the 200k threshold keeps that rare, and the cost is about a tenth of the context plus the summary.
- The desktop app must be open and the Mac awake; Projects cloud threads didn't need that.


---

### Rejected

- **Auto-handoff on every expired cache**: loses recall (5.8 vs 7.5) and costs about the same below 250k.
- **Keep-warm pings** (a tiny message every ~55 min): adds junk turns to every thread and makes the model reply each time.
- **Agent teams as the coordinator**: experimental, teammates aren't restored after a resume.
- **A custom Agent SDK app**: API pricing and third-party-harness restrictions.
- **Switching everything at once**: no cloud threads and no phone cards on day one.


---

### Sources

- Claude Code changelog (2.1.299 idle compaction, 2.1.302 `/config` row, 2.1.304 resume warning): https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- Prompt caching in Claude Code: https://code.claude.com/docs/en/prompt-caching
- Mods reference (`$.session.compact`, `$.session.usage`, `prompt.submit`): https://code.claude.com/docs/en/plugins/mods/reference
- Projects docs: https://code.claude.com/docs/en/claude-projects
- Agent view: https://code.claude.com/docs/en/agent-view
- Agent teams: https://code.claude.com/docs/en/agent-teams
- Cross-session messaging: https://code.claude.com/docs/en/cross-session-messaging
- Hooks: https://code.claude.com/docs/en/hooks
- Third-party idle-compaction write-up: https://www.remio.ai/post/claude-code-idle-compaction-saves-cache-but-resumes-from-a-summary
- Third-party harness restrictions (blog, unverified): https://ucstrategies.com/news/why-developers-are-suddenly-turning-against-claude-code/


---

### Undo

Nothing to undo: research only. `VISION.md` got a short entry for the idea.

## 22:45 Short version of the Readthrough

Matt asked for another version of the Readthrough with only what he really needs to know, all details cut. Wrote `docs/details/2026-10-27-coordinator-migration-short.md`: the four findings, the four-step plan, what he'd lose (threads with the Mac off, phone card view), the one untested risk, and the 👍 ask. Published it as its own Readthrough (`--thread coordinator-migration-short`) so the full one stays as it was. Dropped: sources, the feature table, portability, rejected options, agent teams and agent view, cost maths.

## 22:55 Switching over now; handoff to a fresh thread

Matt can't start any new threads in Everything, so he is switching to the Code-tab coordinator right away. This thread was at 330k tokens and he left the handoff to me. Chose to hand off: above ~250k a fresh context pays off (per the benchmark), and the build is a new phase. Wrote `docs/handoffs/2026-10-27_code-tab-coordinator.md` (seq 1 of chain `code-coordinator`) and started the next session automatically, since Matt wants new threads opened for him, not offered. Its order: coordinator instructions and session first (unblocks him), then voice tasks, then idle compaction in the mod, then rules. Also noted his correction: when he asks for a report, put it in the reply instead of making him wait for a Vercel deploy.

## 23:15 Coordinator instructions written; session proposed

- Wrote `docs/coordinator/code-coordinator.md`: the routing rules from `.rules/core_safety.md` and `project-instructions-slim.md`, ported to Code-tab tools (start_session with `user_asked`, project folder as `cwd`, model from `claude_pace.py`, SendMessage for warm and cold-under-250k threads, fresh brief above 250k, registry, links as `#local_…`). Dropped: the 30-thread count, `/coord` prefix, HANDOFF.md-at-40-messages (Projects-only).
- Created the empty registry `coordinator/threads.json` (`{"threads": []}`).
- Could not start the Coordinator session myself: this session was started by another session, and the app refuses `user_asked` starts from it. Proposed it as a card instead (one click for Matt). It runs in the ai-os folder, since a card can't take a different `cwd`; it can still start threads in any folder.
- Its first turn pins itself and asks to turn on Remote Control.
- Undo: archive the Coordinator session; `git revert` this commit.

## 23:10 Remaining pieces: voice tasks, idle compaction, rules

- **Voice tasks go to the Coordinator.** Nothing outside the desktop app can type into a Code-tab session, so `scripts/coordinator_inbox.py` keeps an outbox (`tmp/coordinator-inbox/pending`). The context-alert mod, in the session named in `coordinator/session.txt` (the Coordinator's CLI id `9093268e-…`), polls it every 30 s and submits each message as a prompt; each poll touches a heartbeat. `voice_task_inbox.py` tries this route first when the heartbeat is under 3 min old, else falls back to the old Everything routes. A successor coordinator runs `coordinator_inbox.py claim`; every session re-reads the owner file each poll, so the handover is live. Rejected: `claude -p --cloud` (needs a cloud session id; the Coordinator is local), the messaging socket env var (per session, not reachable from launchd).
- **Idle compaction (mod 0.6.0).** Each minute: if the thread is ≥ 50 min idle, ≥ 200k tokens, cache still warm, and not compacted since its last turn, call `$.session.compact` with instructions to keep Matt's rules, corrections, current task and next step verbatim; small toast after. Knobs `compact.idleMinutes`, `compact.minTokens`, `hold.minTokens` in `~/.hammerspoon/tweaks/context_alert.json` (Tweaks panel "Context alert").
- **Cold threads under 250k aren't held any more**; tests moved to 300k threads, plus a test for when compaction is due. 33/33 pass; `claude plugin validate` passes. Installed 0.6.0.
- **Rules**: `.rules/core_safety.md` Coordinator Routing now names the Code-tab Coordinator, adds the resume-under-250k rule, marks the 30-thread rule Projects-only. Rebuilt with `build_rules.py`.
- **Untested**: the mod loads 0.6.0 only after the app or session restarts, so the live poll and compaction haven't run in the real Coordinator yet; whether `$.clock.every` keeps firing while a desktop session sits idle is still unknown.
- Undo: `git revert` this commit, then `claude plugin update context-alert@ai-os-mods` after reverting the version.
