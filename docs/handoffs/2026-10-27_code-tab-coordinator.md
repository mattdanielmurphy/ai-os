# Handoff: build the Code-tab coordinator and switch over now (2026-10-27, seq 1)

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-27_code-tab-coordinator.md and continue."

## Chain
- Seq 1 of `code-coordinator`. Parent: none (first in chain).
- Threads so far (oldest first; reopen with `claude --resume <id>` or `threads.py show <id>`):
  - 2026-10-27 · 826223d3-0374-41d4-8a5b-28d275542e3a · research: leaving Projects for our own Claude Code coordinator · (this handoff)

## Chain summary
- Matt is leaving the Claude Projects "Everything" coordinator **now**: it refuses every new thread (the ~30-threads-per-coordinator-chat cap, see `.rules/core_safety.md` "Hand the coordinator chat off before 30 threads"). He says he won't miss much and gains flexibility.
- Goal (his words, `VISION.md`): one place to ask for anything, trust it to route to the right thread and pick the right model; threads just keep going, he never sees a handoff; a **chain** = threads linked by handoffs.
- Research is done: `docs/details/2026-10-27-claude-code-coordinator-migration.md` (full) and `docs/details/2026-10-27-coordinator-migration-short.md` (what he needs to know). Both committed and pushed.
- Key findings: Claude Code's idle compaction (v2.1.299, compacts 200k+ threads ~54 min idle, before the 1 h cache expires) runs only in the terminal and fired 0 times in his desktop threads. The mods API has `$.session.compact({ instructions })` and `$.session.usage()`, so the `context-alert` mod can do the same in the desktop app. Resuming a cold thread beat a Sonnet handoff on recall (7.5 vs 5.8) at about equal cost below ~250k tokens. Fresh project threads start at a median 134k tokens, fresh Code-tab threads at 60k.
- Plan Matt approved by switching: (1) pinned Coordinator session in the Code tab, (2) voice tasks feed it, (3) idle compaction in the mod, (4) rules updated.

## This thread
- Read the earlier threads/notes: `docs/details/2026-10-23-diy-coordinator-vs-projects.md`, `docs/details/2026-10-26-claude-code-instead-of-projects.md`, the Oct 22–23 handoff benchmark (session `8ef9547e`).
- Checked docs: changelog, prompt caching, mods reference, agent view, agent teams, cross-session messaging, hooks, Projects docs. Sources listed in the full details file.
- Measured fresh-thread and cold-resume sizes from `~/.claude/projects/*/*.jsonl` since Oct 20: project 353 threads (median first request 134k, 70 cold resumes, median 220k, 43 over 200k); Code 71 threads (60k, 2 cold resumes).
- Wrote `VISION.md` (new) and two memories (`coordinator-migration-to-claude-code`, `chain-means-linked-threads`).
- Didn't work / rejected: auto-handoff on every expired cache (worse recall, same cost); keep-warm pings (junk turns); agent teams as coordinator (experimental, teammates not restored after resume); custom Agent SDK app (API pricing, third-party-harness limits); hooks can't compact or clear (UserPromptSubmit can only block or add context).
- Nothing was built yet.

## Working on now
Build the coordinator so Matt has one place to ask again, today. Desktop Code-tab primitives it uses: `mcp__ccd_session__start_session` (title, `cwd`, worktree, `model`/`effort` at or below the caller's, linked rows; the app wakes the parent with a note when a linked session ends a turn), `SendMessage` to `local_…` ids for warm threads, `mcp__ccd_session_mgmt__set_session_model`, `clear_session` (idle linked sessions only, not ones open on screen or pinned), `mcp__ccd_sidebar__*` (groups, pins, unread), `set_remote_control` (phone access). Stopped right after the research; no files for the coordinator exist yet.

## Keep in mind
- Every-word-costs-Matt reply rules; details file per session; Readthrough via `pages readthrough … --project code`. But: **Matt doesn't want to wait for Vercel** ("I shouldn't have to wait for Vercel to upload ffs"). When he asks for a report, put it in the reply itself.
- Matt wants handoffs and new threads to happen **automatically and be opened for him**, never asked about.
- Project freeze (`.rules/core_safety.md` 1p): no new projects; build inside ai-os.
- Model choice: Opus by default; `python3 scripts/claude_pace.py` said Opus weekly 65% vs 77% even pace (under pace) at 22:50 on Oct 27. The coordinator itself must run on Opus to start Opus threads (start_session ignores higher models than the caller's). Projects' own default: coordinator Opus at low effort, threads Opus high.
- Keep the routing rules from `.rules/core_safety.md` "Coordinator Routing", with these changes: cold threads under ~250k are resumed (SendMessage) instead of handed off; over ~250k get a fresh session with a brief; the 30-thread rule is Projects-only.
- Keep the brain in plain files (portable to Codex/Gemini later): rules in `.rules/`, a thread registry JSON, briefs in markdown.
- Untested: whether a mod's `$.clock` timer fires while a desktop session sits idle; whether `$.command.run` can run `/clear`; whether linked-session notes reach the coordinator when Matt talks to it from the phone.
- Voice tasks today: `services/mac-connector/server.ts` `send_task` writes to `tmp/voice-task-inbox/queue`, and `scripts/voice_task_inbox.py` delivers into the Everything project. That must point at the new coordinator.
- Unrelated dirty files in ai-os (leave them): `apps/gemini-companion/pnpm-*.yaml`, `docs/details/2026-10-27-glass-tv-imdb-browser.md`, older untracked `docs/handoffs/*-cold*.md`.
- Matt is on a call with Tyler and had been telling Tyler to use one "Everything" coordinator; the new setup should be easy to explain to Tyler later.

## Next steps
1. Write the coordinator's instructions at `docs/coordinator/code-coordinator.md`: port the routing rules and `docs/coordinator/project-instructions-slim.md` to Code-tab tools (start_session with the right project folder as `cwd`, model from `claude_pace.py`, warm reuse via SendMessage, thread registry at `coordinator/threads.json` it keeps current, chain links, link every thread as `[title](#local_…)`).
2. Start the Coordinator session from this thread (`start_session`, `user_asked`, `cwd` `~/projects`, Opus, prompt "Read …/code-coordinator.md; you are Matt's coordinator"), pin it, turn Remote Control on, and tell Matt with its link. Test it with one real small task.
3. Re-point voice tasks: change `scripts/voice_task_inbox.py` to deliver into the coordinator (its inbox socket / SendMessage / `ccd send_message`) instead of the Everything project; test with a harmless task.
4. Idle compaction in `mods/context-alert`: at ~50 min idle and context ≥ 200k (Tweaks knob), call `$.session.compact` with instructions to keep Matt's rules, corrections, current task and next step verbatim; small corner note when it happens; stop holding cold messages under ~250k. Bump version, run its tests, check the timer fires while idle.
5. Update `.rules/core_safety.md` (coordinator routing now points at the Code-tab coordinator; Projects rules marked legacy), run `scripts/build_rules.py`, commit and push.

## Read first
- `docs/details/2026-10-27-claude-code-coordinator-migration.md`: findings, design, risks.
- `.rules/core_safety.md` sections "Coordinator Routing" and "Model Choice by Usage Pace".
- `docs/coordinator/project-instructions-slim.md`: what the old coordinator was told.
- `mods/context-alert/hooks/register.tsx`: the mod to extend (prompt.submit hold logic, `$.prompt.submit`).
- `services/mac-connector/server.ts` and `scripts/voice_task_inbox.py`: the voice front door.

## Matt's message with this handoff (verbatim)

Exactly what Matt sent with `/_handoff`, copied from the transcript by `scripts/handoff_capture.py`. Treat it as his instructions for the next thread. Quotes (`> ...` after `<!-- reply N -->`) are from the previous thread's replies; the text under each quote is his comment on it. Open every image listed.

```text
I (literally) cannot start any new threads in the Everything project, so we're basically going to switch over right now.
It doesn't seem like I'll miss much; I'll gain a lot of flexibility.
Speaking of big threads, this is 330k; your choice if you want to hand off.
```
