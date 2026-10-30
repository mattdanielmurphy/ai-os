# Advisor answer: rules dashboard, beta rules, learning, dictation (2026-10-29)

Answers [2026-10-29-rules-dashboard-learning.md](2026-10-29-rules-dashboard-learning.md). Written by an advisor session (Opus, xhigh) for the Coordinator, which carries out §1. Nothing here was built, started or scheduled by the advisor.

Read: Matt's ask, `code-coordinator.md`, `custodian.md`, `rules-hooks/PLAN.md` + summary, slub-hq `core.md`/`NOW.md`/`IDEAS.md`, ai-os `IDEAS.md`, the read-aloud mod and `~/.hammerspoon/modules/claude_read_aloud.lua` + its log, the Claude app bundle's dictation code, `claude_pace.py` (week 5% used, about on pace → Opus is fine).

---

## 1. Action list for the Coordinator

Items 1–4 are independent: start them together. Item 5 is the Coordinator's own edit. Item 6 is the reply.

### 1. Amend the rules plan with beta rules, the dashboard and the advisor rule
- **Who:** resume [rules-hooks-d-merge-best](#local_ed0b8217-4dba-4904-a91a-bfa272b2fd22) (it wrote PLAN.md). If the thread-size guard denies the send (250k+), start a fresh thread in `~/projects/ai-os` (`use_worktree: false`) with the same brief and title `Rules plan · beta tier + dashboard`.
- **Model / effort:** Opus, high.
- **Brief:**
  > Matt replied to your PLAN.md (his message: `docs/coordinator/asks/2026-10-29-rules-dashboard-learning.md`, parts 1–3 and 6). An advisor critiqued it in `docs/coordinator/asks/2026-10-29-advisor-answer.md` §2–3 and §6; read those. Amend `docs/rules-hooks/PLAN.md` and `PLAN-summary.md`, design only, nothing built:
  > 1. Add a **beta** mode between shadow and live (§2.2 of the advisor answer): agent-authored rules may go live without Matt's 👍 only as additive reminders or action checks, never blocks, core lines, safety/school/secret rules, or anything that relaxes or exempts another rule. They are tagged `[rule:beta:<id>]`, capped at 5 live at once, expire after 21 days unless promoted, and are `matt-only` until promoted. The compiler refuses a beta rule whose trigger overlaps an official rule (that's how "never overrides official" is enforced, not by wording). Promotion needs a measurable target named when the rule is written, plus Matt's 👍 while the system is being designed; record how often he agrees with the agent's promotion advice, and allow auto-promotion only after ~9 of 10 agreements (same calibration as the §3.7 judges).
  > 2. Add the **rules dashboard** (§3 of the advisor answer) as a local-only page generated from the rule files, `fired.jsonl`, `signals.jsonl` and the weekly report. v0 is the ⏸ Reassess before/after table; v1 comes after step 5 (registry migration). On/off toggles write the rule's `mode` through the overrides file (consider exposing them in the existing ⌃⌥⌘T Tweaks panel instead of building toggles). Overlaps and dependencies come from the compiler (shared triggers, a `requires:` field); semantic clashes get one model check per rule change at compile time; misinterpretation stats come from the weekly review's sampled judge, not a per-turn audit. Not deployed to Vercel (it holds private rules). Note that no off-the-shelf tool fits (Langfuse, cc-observatory, rulesync: see advisor §3.2); keep `fired.jsonl` OTel-shaped so one could be added later.
  > 3. Add the **advisor-escalation** reminder to §4.4 C (coordinator role pack): UserPromptSubmit, central/project-coordinator role, sender = Matt, prompt over ~350 words or 4+ separate asks → inject the advisor rule (advisor answer §6).
  > 4. Add one line to the summary for each, marking beta-without-👍 as a veto candidate.
  > Commit and push with `scripts/auto_commit.py --paths docs/rules-hooks/`. Report back in your last message; the Coordinator relays it.

### 2. Log the ideas with honest takes
- **Who:** fresh thread, `cwd: ~/projects`, `use_worktree: false`, title `Log 10-29 ideas (TypeWhisper, rules UI)`.
- **Model / effort:** Sonnet, low.
- **Brief:**
  > Append these entries exactly (fix only formatting to match each file), then commit and push each repo (`git pull` slub-hq first; ai-os via `scripts/auto_commit.py --paths IDEAS.md`). Touch nothing else.
  >
  > **slub-hq `IDEAS.md`** (one line each, its `- date · who · idea · take` format):
  > - `2026-10-29 · Matt · Slub Dictate: a TypeWhisper-style dictation app as good as Claude's, with no silence cutoff, for Slub Utils · take: great personal fix, weak product (Wispr Flow, Superwhisper, VoiceInk, MacWhisper already compete hard); first try TypeWhisper/VoiceInk with a streaming cloud engine (Deepgram, which we already pay for) plus a custom vocabulary, and build only the glue (send to Claude, pause read-aloud). Later; project freeze applies.`
  > - `2026-10-29 · Matt · Rules dashboard + beta rules: every rule with on/off, how often it fires, how often it's misread, why it exists, overlaps and gaps; agents may run experimental "beta" rules that a dot shows, promoted on evidence · take: strong, and it's the visible face of the Slub concierge idea; cheap once the rules→hooks plan logs firings (until then there's nothing to show); beta rules need hard limits (additive only, capped, expiring) or the rule pile regrows. In docs/rules-hooks/PLAN.md.`
  >
  > **ai-os `IDEAS.md`** (its `## <title> (Matt, 2026-10-29)` + `**Honest take:**` format): the same two ideas, worded for ai-os. Mark the dictation one "parked, project freeze" and the dashboard one "folded into the rules→hooks plan".
  >
  > Report back in one line with both commit hashes.
- Also park the dictation app in Linear (team MAT, label "Parked idea") per the housekeeping rule; the thread can do it if the Linear connector is available.

### 3. Dictation: tell the read-aloud thread what was found, and patch around it
- **Who:** resume [read-aloud-2-queue-actio](#local_8a0193cd-7975-4a50-8c57-acd7a52650ca).
- **Model / effort:** Opus, medium.
- **Brief:**
  > Matt's dictation cut off mid-speech tonight (~21:08–21:21) with "Dictation stopped because it heard no words for 1 minute. Your words so far are in the message box." Diagnosis (advisor answer §5): this is Claude's own built-in stop, not our mod. In the app bundle (`ion-dist.asar`) `DictationSession` stops with `auto_silence` when 60 s pass since the last transcript the speech server returned, unless push-to-talk is held. Our `claude_read_aloud.lua` log shows no "closing idle dictation" press after 20:26, and that path only fires on an empty prompt. So the server stopped sending text for a minute while Matt talked (stall, or a poor mic feed such as Bluetooth headset mode; see the mic-held-open-headphones thread).
  > Do, in order, testing each:
  > 1. Log the active input device and its sample rate each time our code opens dictation (`hs.audiodevice.defaultInputDevice()`), so the next cutoff shows whether it was the headphones.
  > 2. Check whether pressing the toast's "Dictate again" button after an `auto_silence` stop *appends* to the message box (not replaces). If it appends, add a watcher: when that toast appears and Matt had been dictating, press "Dictate again" through `claudeControl.withInput` (it's an automation running on its own, so it takes the queue). If it replaces text, don't build it; say so.
  > 3. Confirm whether Claude's hold-to-talk mode (push-to-talk) is available in the desktop app and how to use it; the code exempts it from the silence stop.
  > Bump the mod version if you touch it (memory: mods run from a cached copy). Report back in your last message; the Coordinator relays it.

### 4. Set up the learning system (weekly brief, syllabus, HN, tool scouting)
- **Who:** fresh thread, `cwd: ~/projects/ai-os`, `use_worktree: false`, title `Learning brief · weekly + syllabus`.
- **Model / effort:** Opus, high (the syllabus needs judgment; the weekly job itself runs on Sonnet).
- **Brief:**
  > Matt (2026-10-29, part 5 of `docs/coordinator/asks/2026-10-29-rules-dashboard-learning.md`): he wants to stay educated on agent tools without wasting time, become near-expert at agentic systems so he stops making amateur mistakes, get a Hacker News digest that filters noise, and keep scouting off-the-shelf tools so Slub wraps existing tools with its taste instead of building backends; what's relevant changes as projects mature. Design: advisor answer §4; follow it unless you find a real problem, and say so if you change it.
  > Build:
  > 1. `docs/learning/profile.md`: what Matt builds now (from `docs/ABOUT_MATT.md`, slub-hq `NOW.md`/`IDEAS.md`, the registry), each project's **stage** (idea / prototype / committed / has users) and its replace-a-component bar (advisor §4.3), topics he already knows, topics to skip, and a "feedback" list the weekly job reads and updates.
  > 2. `docs/learning/syllabus.md`: 8–10 short units (≤ 20 min each) built from his real mistakes in `docs/rules-hooks/C-evidence.md`, `B-audit.md` and PLAN §1 (e.g. why a watcher LLM layer is weaker than deterministic triggers, why self-improving loops die silently, eval-before-automate, context budgets, search-before-build). Each unit: the idea, his incident, one exercise he does himself, and 2 good links. One unit rides in each weekly brief.
  > 3. A **desktop scheduled task** (the same mechanism as `~/.claude/scheduled-tasks/morning-checkin`), weekly, Sunday 10:00 Mountain, Sonnet if the task lets you pick. It reads the profile, searches the week's news (vendor changelogs: Claude Code, Anthropic, OpenAI, Google; Hacker News via the Algolia API `hn.algolia.com/api/v1/search?tags=story&numericFilters=points>150,created_at_i>…`; GitHub trending in agent tooling), and writes a brief: **What changed that affects you** (max 3), **Could replace something you built** (only if it clears that project's stage bar), **HN worth your time** (max 3), **This week's lesson** (next syllabus unit). Every item says why it matters to *his* projects in one line and has a rating line: Not interesting / Interesting / Extremely interesting (the same format as the slub-hq "I thought you might find this interesting" idea, 2026-10-28, so it can become that later). Under ~600 words, 15 minutes to read. In weeks with a due date or exam in `docs/SCHOOL.md`, send only the top 3 items and no lesson.
  > 4. Delivery: save to `docs/learning/briefs/YYYY-WW.md`, publish with `pages md` (unlisted, no private details), and add one Apple Reminder "Read this week's agent brief (15 min)" due Sunday 19:00 with the link in its notes. Nothing goes to the Coordinator. Matt's ratings or comments (he can tell the Coordinator "brief: …") get appended to the profile's feedback list; the job reads it every week.
  > 5. Run it once now as a test and send the link. Add a heartbeat: if no brief file appears for 9 days, the custodian mentions it once.
  > Not a new project (it lives in ai-os docs plus one scheduled task), so the freeze doesn't block it. Commit and push. Report back in your last message with the brief's link; the Coordinator relays it.

### 5. Save the advisor rule (the Coordinator does this itself)
Matt worded it himself (part 6), so it's a rule save, not analysis. Add this section to `docs/coordinator/code-coordinator.md` after "What you do yourself", and a one-line pointer in `project-coordinator.md`. Commit and push with `scripts/auto_commit.py --paths docs/coordinator/`. It belongs in the coordinator role pack, not the global core (under the PLAN it's injected by the §4.4 C reminder).

```markdown
## Big asks go to an advisor first (Matt, 2026-10-29)
You stay Opus at low effort. When Matt's message is big, plan it with an advisor before routing:
- **When:** over ~350 words or 4+ separate asks; or he asks for a critique, a design decision or "correct me if I'm wrong"; or the parts depend on each other (one part's answer changes another); or he says "think hard". Small or obvious asks: route them yourself as usual.
- **How:** save his message verbatim to `ai-os/docs/coordinator/asks/YYYY-MM-DD-<slug>.md`. Start one advisor session (`cwd` ai-os, `use_worktree: false`, Opus, effort xhigh set before its first turn; if the first turn already started at lower effort, stop it and restart, as on 10-29). Brief: "Act as the coordinator but take no actions: read the ask file and what it needs, then write a numbered action list (what, which thread or tool, draft brief, model and effort) to `asks/<same slug>-advisor-answer.md`, commit and push, and end with a short reply."
- **Then:** carry the list out as written, without re-analysing it (that's routing, not analysis). Questions it says only Matt can answer go in your reply's Actions line. Archive the advisor once its list is done.
- **Say** one line to Matt only if he'll wait more than a few minutes ("Big one; planning it first").
```

Wording for the save line: "Saved as a global rule: it applies to every coordinator, and it syncs to Tyler via slub-hq." (current rule; the PLAN's new wording isn't adopted yet).

### 6. Reply to Matt (draft, ~90 words)

> **Your beta-rules idea is right, with limits.** Agent-written rules can run without your OK only if they just add reminders, expire in 3 weeks and never touch safety or school; promotion still asks you until agents' advice matches yours.
>
> **The dashboard is a great idea but comes after the hooks log firings;** before that it would be empty.
>
> **Dictation cut off because of Claude's own 1-minute rule, not our mod.** It stops when its server returns no words for a minute, even while you talk. A thread is adding a workaround.
>
> **A weekly 15-minute brief (news, Hacker News, one lesson) is being set up.**
>
> **Actions:** Report dictation bug → Yes, help me report the dictation cutoff to Anthropic · Beta rules need my OK → No, beta rules should always need my OK

(Links to the item threads go on the matching lines once started. The Actions sentences are the only things Matt might want to change: the bug report sends a message to an outside company, so it needs his yes; the second button is the veto.)

### 7. Housekeeping
- Registry: add the threads from items 1–4 (and this advisor, `state: done` once item 5 is done), then archive this advisor session.
- Slub rule 3 (connections): the weekly brief overlaps slub-hq's "I thought you might find this interesting" digest idea (Matt, 2026-10-28); item 4 reuses its rating format. Item 6's reply doesn't need to say it; mention it if Matt asks about Tyler.

---

## 2. Critique: beta rules (part 3) and self-editing rules (part 1)

### 2.1 Where Matt is right
- **Approving every rule doesn't scale.** For an end user (his mom example), "approve this rule?" is a meaningless question. A self-learning system has to be able to change itself; the human's job should be setting limits and checking samples, not approving each change.
- **A separate, visibly marked tier is the right shape.** It's what mature systems do: Langfuse labels prompt versions `production` vs. experiment labels; feature-flag systems have staged rollouts. The "dot" means he always knows when experimental behaviour is in play.
- **Evidence-based promotion beats opinion.** The PLAN already logs every firing, so evidence exists.
- **Keeping Matt and Tyler in the loop while it's being designed** is correct and matches the PLAN's shadow → live gate.

### 2.2 Where he's wrong, or it needs a hard edge
1. **"Never overrides official rules" can't be done in wording.** Models don't apply rule priority reliably; two injected lines that conflict get resolved unpredictably. Enforce it mechanically: the compiler refuses a beta rule whose trigger (event + tool + pattern) overlaps an official rule's, and beta rules may only be reminders or action checks. They may never be blocks, core lines, or anything that relaxes, exempts or skips another rule.
2. **Agents grading their own rules invites gaming.** An agent annoyed by the "asked for an OK" check could write a beta rule that carves out an exception. That's why beta rules must be additive only, and why safety, school, secrets and screen input are off-limits.
3. **"Two weeks, dozens of threads, no issues" is a weak signal.** Matt rarely complains, so silence is the default whether a rule helps or not. Most rules fire rarely, and at ~40 signals a week the numbers are thin. Each beta rule must name, when it's written, what it should reduce (a correction type, a check failure), and promotion compares that signal before and after. "No issues" only rules out harm.
4. **Beta rules regrow the pile.** The PLAN's core problem #4 is growth (100 commits to `.rules/` in 10 days). Cap live beta rules at 5, expire them after 21 days unless promoted, and keep them out of the 60-line core.
5. **The dot is display, not enforcement.** Mods only run in the desktop app. Tag every injected beta line `[rule:beta:<id>]`, so it's visible in the CLI, over Remote Control and on Tyler's Mac too.
6. **Getting to "no human approval".** Earn it the same way as the §3.7 judges: while designing, the agent recommends promotions and Matt taps 👍 or no; log agreement; once ~9 of 10 agree, promotion of additive rules can go automatic. That's the path to the mom-ready version, with data instead of hope.

### 2.3 What changes in the PLAN
- §3.2/§3.3: `mode` gains `beta` (`off | shadow | beta | live`), with fields `target:` (what it should reduce) and `expires:`.
- §3.8 step 2–3: proposals go shadow (3 days, silent) → beta (live, tagged, no 👍 if additive) → official (👍 for now). Blocks and core lines still need 👍 at every stage.
- No change to the rollout order. `beta` is one more enum value in step 2's format; the learn loop stays step 9, because it needs the dispatcher and a few weeks of signals.

---

## 3. Critique: the rules dashboard (part 2)

### 3.1 Honest take
Strong idea, and the right one for Slub: it's the visible face of the "concierge gives each task only the rules it needs" product (slub-hq IDEAS, 10-29). Three corrections:
1. **Timing.** Today rules are prose in `.rules/`; there's no firing data, no per-rule state, nothing to toggle. Built now, it would be a nice view of nothing. Almost every panel Matt listed falls out of the PLAN's own data once steps 2 and 5 exist: rule files (kind, circle, mode, why, since, review, tests), `fired.jsonl`, `signals.jsonl`, the weekly `rulehook.py report`. So: v0 = the ⏸ Reassess before/after table, rendered as a page; v1 after step 5.
2. **"Self-audit can run automatically since it has no side effects."** Right about safety, wrong about cost: judging whether a rule was misread means a model reading transcripts, which uses quota across 15+ threads. Do it in the weekly review, sampled, skipped when `claude_pace.py` says the week runs hot.
3. **Clashes, overlaps, dependencies, gaps.** Overlaps (same trigger) and dependencies (`requires:`) are deterministic: compute them in the compiler for free. Semantic clashes need a model, but only once per rule change, at compile time. Gaps come from signals (corrections with no matching rule), which the weekly review already finds.

Privacy: the dashboard shows Matt-only rules (school, Mac paths), so it shouldn't be a public Vercel UUID page. Serve it locally (`pages.test` dev, not deployed). Toggles: the ⌃⌥⌘T Tweaks panel already renders on/off switches from JSON files; exposing rule modes there may beat building toggles (shared-modules rule).

### 3.2 Existing tools checked
- **Claude Code's built-in OpenTelemetry export** (metrics, events; traces in beta) plus ready-made stacks such as [cc-observatory](https://pypi.org/project/cc-observatory/) (hooks → SQLite + OTel → Grafana) and the [SigNoz guide](https://signoz.io/blog/claude-code-monitoring-with-opentelemetry): good for usage and tool-call telemetry, nothing about rules. Worth borrowing the OTel event shape for `fired.jsonl` so a Grafana view can be added later for free.
- **[Langfuse](https://langfuse.com/docs/prompt-management/features/prompt-version-control)**: traces, evals and prompt versions with labels (`production`, experiment labels like `prod-a`/`prod-b`). Its label model *is* the beta/official idea, so copy the concept. Don't adopt it: it's built for LLM apps calling an API, not Claude Code sessions; self-hosting needs Postgres, ClickHouse, Redis and object storage (heavy for the VPS, which needs Matt's OK for heavy containers); protected labels are a paid feature.
- **Braintrust / LangSmith / Arize Phoenix**: eval and tracing platforms, same mismatch; Braintrust and LangSmith are hosted SaaS.
- **Rule sync tools** ([rulesync, agentsync, SyncAI](https://dev.to/pederaa/how-to-sync-cursor-rules-claudemd-and-agentsmd-across-projects-without-config-drift-23f8)): generate CLAUDE.md/AGENTS.md/.cursorrules from one source. They solve the PLAN's drift problem for text, not triggers, firing data or tiers. Not needed: the PLAN's compiler already does one source → many outputs.
- **Agent frameworks with self-editing** (Hermes skills, Letta's self-editing memory, DSPy/GEPA prompt optimizers): show the pattern works with an eval set. GEPA-style "propose, test against real cases, keep winners" is what the weekly review already does with C's transcripts as tests.
- **Verdict:** no tool does a rules registry with firing telemetry and tiers for Claude Code hooks. Build the thin view over the PLAN's data; borrow Langfuse's labels and OTel's event shape.

---

## 4. Education setup (part 5)

### 4.1 One channel, not three
A weekly brief, a syllabus and an HN digest as three feeds would recreate the noise he wants to avoid. One weekly brief carries all three, plus the tool scouting. ~15 minutes, Sunday. Daily HN is exactly the time sink; weekly top-3 filtered by his profile is the point.

### 4.2 Mechanism
- **Scheduler:** a desktop scheduled task, like the existing `morning-checkin`. It runs on his Mac with his tools (web search, `pages`, `apple-reminders`) and needs no new infra. Rejected: routing through the Coordinator inbox like the custodian (it would fill the Coordinator's context with research); a cloud routine (no access to his Mac's `pages`/Reminders); self-hosting [Horizon](https://railway.com/deploy/horizon-aug-26-ai-news-radar) or similar news radars (another system to run during the freeze, and it doesn't know his projects).
- **Sources:** vendor changelogs; HN via the Algolia search API with a points floor (no scraping, no new service); GitHub trending for agent tooling. Optional later: [hnrss](https://github.com/kakwa/hnrss) feeds if he wants them in a reader.
- **Output:** `docs/learning/briefs/YYYY-WW.md` → `pages md` (unlisted, matches his "pages on Vercel" and "shareable Markdown" rules; the brief holds nothing private) → one Apple Reminder with the link (matches his reminders rule and shows on his phone).
- **Model:** Sonnet for the weekly job (summarising and filtering); Opus high once to build the profile and syllabus.

### 4.3 The scope filter that changes over time
`docs/learning/profile.md` holds each project's stage and a bar for "replace something you built":

| Stage | Recommend replacing a component when… |
|---|---|
| Idea | Any off-the-shelf tool does it reasonably well: use it. |
| Prototype | It's clearly better and the swap is under a day. |
| Committed | It removes a whole piece of backend he'd otherwise maintain. |
| Has users | Only for security, deprecation, or a cost/quality jump users would notice. |

Stages are updated by the job from evidence (commits, `NOW.md`, users) and by Matt's feedback. Ratings on each item (Not / Interesting / Extremely interesting) feed the profile's topic weights. This matches the slub-hq digest idea (Matt, 2026-10-28), so the brief can become Tyler's version later.

### 4.4 Syllabus
Built from his own incidents, so each lesson fixes a mistake he actually made: watcher-LLM vs. deterministic triggers, loops that die silently (Hermes curator, `transcript_evaluator.py`), rules drift from multiple copies, eval before automate, context and token budgets, search before build, fan-out cost. One unit per week, each with an exercise he does himself. This isn't school work, so no ghostwriting limits apply, but it shouldn't compete with school: weeks with a due date or exam in `SCHOOL.md` get only the top 3 items and no lesson.

---

## 5. Dictation cutoff (part 4): diagnosis

**It's Claude's built-in silence stop, not our mod.** Evidence:
- The message text lives in the Claude app bundle (`/Applications/Claude.app/Contents/Resources/ion-dist.asar`, message id `Gj3KdYf5lm`, stop reason `auto_silence`).
- The rule in `DictationSession`: on each audio-level tick, if `silenceAutoStopMs > 0` and more than that time has passed since `lastTranscriptAt` (the last text the speech server returned), and push-to-talk isn't held and no mic switch is in progress, it stops with `auto_silence`. Its own follow-up line says "If you were speaking, check your microphone."
- So it counts **time since the last transcript**, not silence on the mic. If the speech server stops returning text for 60 s while Matt talks (a stall, or a poor or wrong mic feed), it stops mid-speech.
- Our side: `claude_read_aloud.lua` presses ⌘D to close dictation only when the prompt is empty and our own auto-dictate opened the mic; its log shows no such press after 20:26 tonight, and a ⌘D press wouldn't produce that message anyway.
- Not proven: what stalled. Hypotheses, most likely first: the mic was a Bluetooth headset in low-quality call mode (see [mic-held-open-headphones](#local_75fe3954-f9ea-44d9-b02c-ff329970734f)); a server-side stall; a long pause while thinking. Item 3 adds input-device logging so the next one tells us.
- No app logs were found for it (`~/Library/Logs/Claude` has no dictation lines).

**Workarounds:** hold-to-talk is exempt from the stop (if the desktop app offers it); TypeWhisper (already wired to the read-aloud Interrupt button) for long dictations; an automatic "Dictate again" press if it appends (item 3); and a bug report to Anthropic, which needs Matt's yes because it sends a message to an outside company.

---

## 6. The sub-coordinator (advisor) pattern (part 6)

The text to save is in §1 item 5. Why this shape:
- **It's the existing "no analysis in the coordinator" rule made concrete.** The Coordinator already must send analysis to a thread; the advisor is that thread, with a fixed output (a numbered action list) the Coordinator can carry out mechanically at low effort.
- **Triggers are deterministic where possible** (word count, number of asks, explicit phrases), so the PLAN can turn them into a UserPromptSubmit reminder in the coordinator role pack (§4.4 C) instead of hoping a low-effort model notices.
- **Effort must be set before the first turn.** Today's advisor had to be stopped and restarted to pick up xhigh. Check whether `start_session` accepts an effort; if not, the restart works.
- **The advisor takes no actions** (no threads, schedules or builds). That keeps one actor responsible for the registry and avoids two coordinators starting the same thread.
- **Cost:** one Opus xhigh session per big dump, maybe 2–4 a week. Worth it against the cost of a low-effort coordinator mis-routing a six-part message.
- **Rejected:** raising the Coordinator's own effort on big messages (its context grows with analysis it shouldn't hold, and effort can't change mid-turn); a cheap model splitting the message (splitting is easy; the hard part is the cross-part judgment, as in parts 1–3 here).

---

## Sources
- [cc-observatory](https://pypi.org/project/cc-observatory/) · [SigNoz: Claude Code monitoring with OpenTelemetry](https://signoz.io/blog/claude-code-monitoring-with-opentelemetry) · [local Claude Code observability stack](https://dev.to/yudayakumar/i-built-a-local-observability-stack-for-claude-code-traces-tool-calls-tokens-and-cost-3ce8)
- [Langfuse prompt version control and labels](https://langfuse.com/docs/prompt-management/features/prompt-version-control)
- [Syncing CLAUDE.md, AGENTS.md and Cursor rules (rulesync, agentsync)](https://dev.to/pederaa/how-to-sync-cursor-rules-claudemd-and-agentsmd-across-projects-without-config-drift-23f8)
- [Horizon AI news radar](https://railway.com/deploy/horizon-aug-26-ai-news-radar) · [hnrss](https://github.com/kakwa/hnrss) · [CondenseIt write-up](https://dev.to/wildlifechorus/i-built-a-self-hosted-news-digest-that-re-ranks-itself-based-on-what-you-actually-read-4l44)
