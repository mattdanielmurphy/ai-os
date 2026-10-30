# Agentic systems syllabus (one unit per weekly brief)

Ten short units, each ≤ 20 minutes, each built from a mistake Matt's own setup actually made. The weekly brief takes the next unit whose **Status** is `next`, then marks it `done (YYYY-WW)` and sets the following one to `next`. Exam weeks (see `docs/SCHOOL.md`) skip the lesson.

Sources for the incidents: `docs/rules-hooks/C-evidence.md`, `B-audit.md`, `PLAN.md` §1–2.

---

## 1. Deterministic triggers beat an always-on LLM watcher
**Status:** next
- **Idea:** If you can name the moment a rule matters (a tool call, a path, the end of a turn), a script at that moment is free, instant and never forgets. A model "watching everything" costs quota every turn, misses things, and can't tell a pattern from one anecdote.
- **Your incident:** The hang guard denied 77 risky commands and the input guard 46 screen grabs: agents kept forgetting, hooks caught every one. Your live-watcher idea became a weekly tuner instead (PLAN §2 row 8).
- **Exercise:** Pick three rules from `.rules/` and write, for each, the exact tool call or moment where it applies. Any rule you can't name a moment for is a judgement rule; mark it.
- **Links:** [Claude Code hooks guide](https://docs.claude.com/en/docs/claude-code/hooks-guide) · [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## 2. Self-improving loops die silently unless something checks they ran
**Status:** pending
- **Idea:** Any background job that "improves things" needs a heartbeat: a file it must write, and a separate cheap check that complains when that file is stale. Otherwise it fails and nobody notices.
- **Your incident:** Hermes's curator and `transcript_evaluator.py` both stopped working without anyone noticing; the per-reply details file ritual died when the coordinator moved to the Code tab (4 of 138 replies), with no complaint.
- **Exercise:** List every scheduled job on your Mac (`la list` or launchd). For each, write where its "I ran" evidence lives. Circle the ones with none.
- **Links:** [Healthchecks.io: how dead man's switches work](https://healthchecks.io/docs/) · [Google SRE book: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)

## 3. Measure before you automate (evals, small and honest)
**Status:** pending
- **Idea:** Before adding a rule or hook, write down the number it should move and measure it once now. Then you can tell if it worked, and delete it if not.
- **Your incident:** ~100 commits touched `.rules/` in 10 days with no before/after numbers; evidence only arrived with the C study (e.g. 15% of replies asked for an OK they didn't need).
- **Exercise:** For the "don't ask for OKs you don't need" rule, define the metric and how you'd count it from transcripts. Don't build it; just write the definition.
- **Links:** [Hamel Husain: Your AI product needs evals](https://hamel.dev/blog/posts/evals/) · [Anthropic: Define success criteria](https://docs.claude.com/en/docs/test-and-evaluate/define-success)

## 4. One source of truth; generated copies only
**Status:** pending
- **Idea:** Every hand-kept copy of a rule drifts. Keep one source and generate the rest, or don't copy at all.
- **Your incident:** Rules live in `.rules/`, `~/.claude/CLAUDE.md` and memory; they now disagree on rm, the freeze, undo and approvals (B §3.2). The "save every rule in three places" rule caused it.
- **Exercise:** Pick one rule and find every place it's written (`grep -r`). Count the versions and note where they differ.
- **Links:** [rulesync](https://github.com/dyoshikawa/rulesync) · [AGENTS.md convention](https://agents.md/)

## 5. Context is a budget, not a bucket
**Status:** pending
- **Idea:** Every always-loaded word costs tokens on every turn and dilutes attention. Load rules only where they matter (path packs, hooks) and keep a hard line budget.
- **Your incident:** ai-os sessions load ~17,000 words of rules; other projects get a drifted 4,100-word copy, and six topic files reach no session at all (B §3.1).
- **Exercise:** Count the words in your current `~/.claude/CLAUDE.md`. Mark which paragraphs matter in under 10% of sessions.
- **Links:** [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Claude Code memory docs](https://docs.claude.com/en/docs/claude-code/memory)

## 6. Search before you build
**Status:** pending
- **Idea:** A 10-minute search for an existing tool usually beats a day of building. Use what you find as ingredients; build only the glue and the taste.
- **Your incident:** Dictation cutoffs led toward building a dictation app, when TypeWhisper, VoiceInk and Superwhisper already exist (advisor answer §5); the rules dashboard search found no fit, which is also a valid result.
- **Exercise:** Take one thing on your project list and spend 10 minutes finding three existing tools. Write one line each on what they'd save you.
- **Links:** [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) · [GitHub topic: ai-agents](https://github.com/topics/ai-agents)

## 7. Fan-out costs more than it looks
**Status:** pending
- **Idea:** Each new agent starts cold and re-reads context. Parallel agents are worth it only for truly independent work whose results you don't need to merge by judgement.
- **Your incident:** Coordinators sent 32 messages into threads already at 250k–399k tokens, re-reading huge histories at full price (C #1), until `thread_size_guard.py` landed.
- **Exercise:** Look at one recent multi-thread task. Estimate tokens per thread; would two threads have done it?
- **Links:** [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) · [Cognition: Don't build multi-agents](https://cognition.ai/blog/dont-build-multi-agents)

## 8. Handoffs must be pushed, not left to be read
**Status:** pending
- **Idea:** A message that depends on the receiver remembering to check a file will eventually be lost. Deliver it into the receiver's live input.
- **Your incident:** A Slub Bot task never arrived: it was filed under "Done" in an inbox read only at session start, pointing at an old coordinator (C #4).
- **Exercise:** Draw how a voice task reaches a worker today. Mark every step where a human or agent must "remember to look".
- **Links:** [Martin Fowler: Event-driven architecture](https://martinfowler.com/articles/201701-event-driven.html) · [Claude Code headless/SDK](https://docs.claude.com/en/docs/claude-code/sdk)

## 9. Conflicting rules: a hook can only enforce one side
**Status:** pending
- **Idea:** When two rules point opposite ways ("wait for 👍" vs. "just do it"), the model picks at random. Resolve the conflict into one rule before adding enforcement.
- **Your incident:** Six "wait" rules and four "just do it" rules collide; you objected six times to unnecessary OK requests (C #2, PLAN §0.3).
- **Exercise:** Write the one sentence that decides "act or wait" for every case you can think of. Test it on three past replies.
- **Links:** [Anthropic: Claude prompting best practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) · [OpenAI: Model spec (chain of command)](https://model-spec.openai.com/)

## 10. When it's the platform, not the agent
**Status:** pending
- **Idea:** Some failures come from the harness (permission classifier, app bugs, built-in timeouts), not the model. Diagnose the layer before writing a rule.
- **Your incident:** ~16 "asked for an OK" replies were forced by the auto-mode classifier (C); the dictation cutoff was Claude's built-in 60 s silence stop, not your mod (advisor §5).
- **Exercise:** Take the last thing an agent did that annoyed you. Write which layer caused it: model, prompt/rule, tool, harness, or app.
- **Links:** [Claude Code permissions/settings](https://docs.claude.com/en/docs/claude-code/settings) · [Simon Willison on agents](https://simonwillison.net/tags/ai-agents/)
