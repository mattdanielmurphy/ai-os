# Rules → hooks: the merged plan (D)

Written 2026-10-29. This is a design only: no rule, hook or setting was changed. It merges [A-architecture.md](A-architecture.md) (how), [B-audit.md](B-audit.md) (which rules deserve to live) and [C-evidence.md](C-evidence.md) (which rules break, and when), all xhigh second passes. It also draws on the slub-hq README, `setup/core.md`, today's call notes (`slub-hq/notes/calls/2026-10-29.md`), `.rules/*.md`, `~/.claude/CLAUDE.md`, `docs/coordinator/code-coordinator.md` and `~/.claude/settings.json`. There is no slub-hq `VISION.md`.

The short version for Matt is [PLAN-summary.md](PLAN-summary.md).

---

## 0. In short

1. **Deletion matters as much as hooks.** Most sessions get the wrong text (B §3.1): ai-os sessions load ~17,000 words, every other project gets a ~4,100-word hand-kept copy that has drifted, and six topic files reach no session at all. The school rule and the freeze are missing outside ai-os. Step 0 is a text clean-up, before any code.
2. **The costliest failures happen at two moments** (C): sending work to another thread (already guarded since 10-30) and the end of a turn. Rollout goes in C's cost order: the school guard and the end-of-turn "don't ask for OKs you don't need" check come first. Rules that agents already follow (bun, secrets, rm, `/tmp`) come later, because those hooks are insurance.
3. **One "act or wait" rule replaces ten.** Today six "wait" rules and four "just do it" rules collide. A hook can only enforce one side, so the rule has to be clear before the check exists.
4. **Architecture: A's design, made smaller at the start.** One rule per Markdown file. Five channels, cheapest first: native deny, path packs, one dispatcher, a few gated model judges, and a core of 60 lines or fewer. The runtime knows the session's role and who reads the reply. The four guards that work today stay as they are until the dispatcher has proven itself.
5. **New finding: an end-of-turn check can't un-send a reply.** Claude Code shows the reply before the Stop hook runs. So checks that lead to an *action* (commit and push, fix the Actions line, report a voice task) continue the turn. Checks about *prose* (length, shorthand, bare paths) remind the agent on its next turn instead of making Matt read and hear the reply twice.
6. **The per-reply details file, Readthrough and reel go.** A details file is written only when a reply overflows its budget; Readthroughs and reels are made on request. The ritual died on its own when the coordinator moved to the Code tab, with zero complaints (C).
7. **Matt's watcher idea becomes a weekly tuner, not a live layer.** Every turn records evidence for free. Once a week one review proposes at most 3 tested rule changes for Matt's 👍. A heartbeat line makes sure it can't die unnoticed the way Hermes's curator and `transcript_evaluator.py` did.
8. **Tyler gets rules by circles.** The shared core is live for both of them. Matt's recommended defaults arrive switched off until Tyler says Yes. Matt-only rules never leave Matt's Mac. This follows today's call decision: "Matt's own rules never apply to Tyler automatically."
9. **Added after Matt's reply (2026-10-29):**
   - **Beta rules (§3.10):** agent-written rules can go live without a 👍, but only as tagged, capped, expiring add-ons. They can never block anything or relax another rule.
   - **A local rules dashboard (§3.11):** v0 at the reassess gate, v1 after the registry migration. Toggles go through the Tweaks panel.
   - **The advisor rule (§4.4 C):** coordinators get a reminder to send big asks to an advisor first.

   Sources: Matt's message in `docs/coordinator/asks/2026-10-29-rules-dashboard-learning.md` (parts 1–3, 6) and the advisor's critique in `…-advisor-answer.md` (§2, §3, §6).

---

## 1. Honest assessment

**What's right about the current system.**
- Most rules are good preferences that come from real incidents.
- Where hooks exist, they work. The hang guard denied 77 risky commands and the input guard denied 46 unapproved screen actions. The forgetting kept happening, but none of it reached Matt (C).
- Many text rules are followed fine: commit and push (3 of 185 editing sessions never committed), bun, secrets, quiz menus after their rule. Those don't need new hooks urgently.

**What's wrong.** Four problems, in order of weight:
1. **Distribution.** The same rule exists in up to three hand-kept copies (`.rules/`, `~/.claude/CLAUDE.md`, memory), and they now disagree on rm, the freeze, undo and approvals (B §3.2). The rule "save every new rule in three places" is what creates the drift.
2. **Contradictions.** The act/wait muddle (B §3.6) is the root of C's top behavioural failure. Some rules also fight Claude Code's own built-in instructions ("commit only when asked", "publish as Artifacts", "ask with menus"). Text loses those fights, so those rules need hooks most.
3. **Size and style.** About 40% of the text is incident stories and dated amendments. The Gemini-era ALL-CAPS "invariants" make models over-apply rules.
4. **Growth.** About 100 commits touched `.rules/` in 10 days. With no budget, any clean-up regrows within weeks. A line budget enforced by the compiler matters more than any single hook.

**What hooks will not fix.**
- Clarity, taste, honest takes, and knowing when a fork is real. These stay judgment.
- A hook can tell an agent its reply was 240 words. It can't make the next reply good.
- Some "asked for an OK" moments are caused by Claude Code's auto-mode safety check, not by the agent (C: about 16 replies). Permission allow-rules fix those, not hooks.

**The migration itself breaks the freeze a little.** About 60 rule files, a compiler, a dispatcher and tests make a new system to maintain. It's justified because it *removes* about 90% of the always-loaded text and cuts Matt's corrections. To keep it honest, the rollout has a stop-and-reassess gate after step 4 (§5). If C's numbers have improved by then, the remaining steps are optional.

**This is Slub in miniature.** On today's call Matt and Tyler named the core Slub product as a coordinator that gives each task only the rules it needs. This system is that, for one person. Its firing log (`fired.jsonl`) is product research; keep it.

---

## 2. Where A, B and C disagreed, and what I picked

| # | Question | A says | B says | C says | Picked, and why |
|---|---|---|---|---|---|
| 1 | Rollout order | Infrastructure first: skeleton, port 4 guards, denies, then Stop checks | Delete dead rules first | The cost order: sends (done), OKs, school, handoffs, length, Actions | **C's cost order, with A's safety rails and B's deletion as step 0.** The first fixes ride on existing guards, so no infrastructure has to exist before value lands. |
| 2 | Port the 4 working guards into the dispatcher in step 1 | Yes | — | They work (77 and 46 denials) | **No, port them last (optional).** It adds risk for about 10 ms of speed. A's own first pass said the same. |
| 3 | Low-evidence denies (rm, npm, `/tmp`, `gh --private`) | Early (step 2) | Block | Mostly followed; no harm found | **Later (step 5), as a cheap port of the tested Codex guard.** It's insurance. Secret reads are the exception: one `permissions.deny` line, no code, so they go early. |
| 4 | Details file on every reply | Pending | Overflow-only, or auto-generated at session end | Enforce it or drop it; it died silently | **Overflow-only; Readthroughs and reels on request; no auto-generator.** Transcripts are already exported and searchable in QMD, which covers autopsies. Nobody missed the ritual. *Veto candidate.* |
| 5 | How end-of-turn checks act | Continue the turn via `additionalContext` | Block once | Block once | **Split by check type** (§3.6). Action checks continue the turn. Prose checks remind on the next turn, because the long reply has already been shown and read aloud. |
| 6 | Input guard when Hammerspoon is unreachable | Pick one | Matt decides | — | **Fail closed.** Matt's latest words (10-28, after a test moved his mouse) say so. The deny message tells the agent how to get Hammerspoon back. |
| 7 | Who gets the model judge for "asked an OK it didn't need" | Coordinators only, async | — | It's everywhere | **A deterministic check for everyone, plus a model judge for coordinators only** (low volume, high stakes), shadow first. |
| 8 | Matt's live watcher layer | Weekly tuner + coordinator judge | — | — | **A's verdict, simplified.** No daily triage stage: one weekly review reads the signals directly. Plus a heartbeat. Fewer moving parts is the lesson from Hermes. |
| 9 | Review at every Stop/PreCompact (Matt's ask) | Capture every turn, review in batches | — | — | **Batches.** One turn can't tell a pattern from an anecdote, and a model call per turn across 15+ threads costs real quota to say "fine". *Veto candidate.* |
| 10 | School enforcement | Pack + core line | PreToolUse `ask` on writes | Inject + a PostToolUse code-diff block | **Inject + `ask` on every agent write under school folders.** The AST diff is clever, but it's brittle across languages. Add it only if the `ask`s turn out to be too frequent. |
| 11 | Quiz `multiSelect` deny | Deny | Deny | Mostly fixed (20% after the rule) | **Deny anyway, in step 5.** It's deterministic and free, and it also enforces "no menus outside quizzes". |
| 12 | Handoff threshold (40 messages / 200k / 250k) | — | Pick the hook's | — | **250k, the hook's.** Delete the others. |
| 13 | "Syncs to Tyler" line said on every saved rule | — | Contradicts today's call | — | **Today's decision wins.** New wording: "saved for all your agents; offered to Tyler in his next digest". |
| 14 | Classifier-forced OK asks | — | — | Permission allow-rules | **Adopt, in step 1, with the crossword `main` deny shipped first.** Otherwise the allow-rules would make a public-production push *easier*. *Veto candidate (it widens what runs without a check).* |
| 15 | UI design gates (think alone, exemplars, 3–4 separate options, mixer) | One pack | Merge into one flow | — | **One design flow** (§4.4 D). Separate-agent options only for "for the world" Slub products. *Veto candidate.* |
| 16 | Registry format | One Markdown file per rule | One source, generated copies | — | **A's format, plus B's tags** (circle, kind, review date). It's plain Markdown, so it fits Slub core rule 7. |
| 17 | do.test links | — | Re-test whether still needed | No link complaints since 10-24 | **Keep for now; one quick test decides** (§8). |
| 18 | Agents editing their own rules (Matt's reply: approving every rule won't scale for an end user like his mom) | Every change needs Matt's 👍 | — | — | **A beta tier with hard edges** (§3.10). Additive rules can go live without a 👍. Promotion to official still needs one, until agents' advice has matched Matt's about 9 times in 10. "Never overrides official rules" is enforced by the compiler, not by wording. *Veto candidate.* |

---

## 3. Final architecture

### 3.1 Five channels, cheapest first

| Channel | Mechanism | Used for |
|---|---|---|
| 1. Native deny | `permissions.deny` in settings | Secret `Read`s (`.env*`, `*credentials*`, private keys). No code at all. |
| 2. Path packs | Generated `~/.claude/rules/<pack>.md` with `paths:` frontmatter; Claude Code loads a pack when a matching file is read or edited | UI and web, Swift/HUD. For folders outside the session's working directory (`~/.hammerspoon`, `~/Documents/School`), the dispatcher injects the pack instead (needs a test, §8). |
| 3. Dispatcher | One command hook per event, `rulehook.py <event>`, reading a compiled index | Blocks, just-in-time reminders, end-of-turn checks, signal capture |
| 4. Model judges | Async `asyncRewake` hooks on the coordinator's Stop, behind a deterministic precheck | 4 coordinator judgments (§3.7) |
| 5. Core | A generated `~/.claude/CLAUDE.md`, ≤ 60 lines | Judgment rules that have no trigger |

Desktop mods (context-alert, action-bar, read-aloud) never *enforce* rules. They only run in the desktop app; command hooks also run in the CLI, over Remote Control and on Tyler's Mac.

### 3.2 Rule kinds

Every rule has exactly one primary kind; a rule that can't name one doesn't get in.

| Kind (A's name) | What it is | Contract |
|---|---|---|
| **Hard block** (`deny`) | PreToolUse denies the call, or `ask`s Matt | Only for costly or irreversible actions. The reason says what to do instead. Every deny's tests include its known workarounds (Codex lesson: `find -delete`). |
| **Just-in-time reminder** (`nudge`, `pack`) | ≤ 200 characters injected at the moment it matters, or a topic pack loaded when its files are touched | Prefer a *fact* over a principle ("Pace: 61% of the week used at 48% elapsed, Opus OK"). Tagged `[rule:<id>]`. |
| **End-of-turn check** (`check`) | Stop dispatcher inspects the reply and the touched repos | One folded message per turn at most. Action checks continue the turn; prose checks remind on the next turn (§3.6). |
| **Judgment** (`core`) | A line in the always-loaded core | Only when no trigger exists, and only inside the 60-line budget |

Two supporting kinds:
- **Auto:** a tool just does it, so the rule text can go (e.g. `orphans.cjs` inside `pages deploy`).
- **Signal:** silent evidence capture for the learn loop; it never injects text.

### 3.3 One rule = one Markdown file

The format is A §4 unchanged, with B's tags added. Example:

```markdown
---
id: school-no-ghostwriting
kind: deny            # deny | nudge | pack | check | core | auto | signal
circle: matt-only     # shared-core | slub | matt-recommended | matt-only
roles: [all]          # central | project-coordinator | worker | subagent | all
on: { event: PreToolUse, tool: 'Edit|Write|NotebookEdit|Bash', test_fn: school_write }
decision: ask
say: "Graded school work: explain, hint or critique only. Never write, fix or add logic. Matt approves this write."
mode: shadow          # off | shadow | beta | live   (beta: §3.10)
fail: open
since: 2026-10-23
review: 2027-01-31
requires: []          # rule ids this one relies on (feeds the dashboard's dependency view)
# beta rules only:  target: <the signal it should reduce>   expires: <date, ≤ 21 days out>
tests: { fire: [...], pass: [...] }
---
Full rule text, why, Matt's words, history (for humans, Tyler and the learn loop; never injected).
```

**Where the files live**
- `slub-hq/setup/rules/`: `shared-core` and `slub` rules. Both Matt and Tyler must agree to a change (core.md's rule).
- `ai-os/rules/`: `matt-recommended` and `matt-only` rules. These replace `.rules/*.md` gradually.
- `slub-hq/setup/<person>/overrides.md`: per-person `mode` and `params`.

**The compiler** (`build_rules.py` gains this step; it stops writing `GEMINI.md`/`HERMES.md`, which are shelved) emits:
1. `rules-index.json` for the dispatcher (no Markdown parsing at runtime).
2. The path packs.
3. The generated `~/.claude/CLAUDE.md` core. After step 7, agents never hand-edit it.
4. The settings fragment.
5. Tyler's export.

It **refuses to compile** when:
- a rule has no kind, or has no tests, or a test fails;
- a `say` line is over 200 characters, or doesn't tell the agent what to do;
- the core is over 60 lines (a new core line means an old one moves out);
- an incident patch is past its `review` date with no fires and no renewal;
- a rule exported to Tyler contains a Matt-only path (`do.test`, `~/.hammerspoon`, `claude-control`);
- a beta rule breaks any of §3.10's limits (its kind, a trigger that overlaps an official rule's, the cap, the expiry date, a missing `target:`).

The compiler also writes the facts the dashboard (§3.11) needs: rules that share a trigger (overlaps), and `requires:` links in both directions (relies on / relied on by).

**Rules about rules** (B §6.1) live in a short authoring guide for whoever writes rules. They are never loaded into working agents: one home per rule, firm calm wording ("do X, because Y"), stories go in the body or a changelog and are never injected, proactive behaviour over skills Matt must remember.

### 3.4 Runtime

As in A §5:
- one `rulehook.py` per event (PreToolUse, PostToolUse, PostToolBatch, UserPromptSubmit, SessionStart, SubagentStart, Stop);
- `python3 -I -S`, with a matcher union so Read, Grep and Glob never spawn Python;
- a per-session state file, and every firing logged to `fired.jsonl`;
- at most 600 characters per call and about 1,500 per turn;
- **fail open**, with a kill switch (`AIOS_RULES=off` or `~/.claude/rules.off`) and `shadow` mode per rule.

The **fail-closed** rules (screen input and Bash secret reads) stay in **separate handlers** with `onFailure: "block"`. A dispatcher crash can't disable them, and a crash in them can't take the dispatcher down.

**Changed from A:** the four existing guards (`bash_timeout_guard`, `input_guard`, `browser_pane_guard`, `thread_size_guard`) keep their own settings lines until step 5 at the earliest. Steps 1–2 *extend* two of them rather than replacing them.

**Prompt cache:** SessionStart output must be stable per role (no live facts, no timestamps). Live facts only go in mid-conversation injections.

### 3.5 Who is running, and who reads the reply

Taken from A §6, which is the piece that fixes C's main caveat.

**Role**, resolved once per session and cached:
1. Desktop session metadata → `coordinator/threads.json` role.
2. The title (`… · Coordinator`), as a fallback.
3. `AIOS_ROLE` env.
4. Default `worker`.

Subagents are identified by `agent_id`.

**Sender**, classified at UserPromptSubmit using `habit_gate.py`'s existing list:
- `matt`: plain text, a voice task, a `<wake>` from his thread;
- `relay`;
- `peer` (`<cross-session-message`);
- `event` (`<side-sessions-event`, `<task-notification`, `<ci-monitor-event`);
- `schedule`.

**Reader:** Matt reads the reply when the sender was `matt`, or when the session is a coordinator and the sender wasn't a peer. Reply checks (length, Actions line, links) run **only when Matt reads the reply**. Repo checks run for everyone.

### 3.6 End of turn: action checks vs prose checks

The Stop hook runs **after** the reply is on screen, and read-aloud may already be speaking. Continuing the turn adds a second message under the first, plus a visible "Stop hook feedback" line. That's fine when the continuation *does* something. It's bad when it just rewrites prose: Matt would read and hear both versions, which breaks "every word costs Matt" and "no repeats".

| Check | Type | What happens |
|---|---|---|
| Asked for an OK it didn't need (§4.4 A) | action | Continue: "do it (commit, push, make it live, start the thread), or name the real fork in one line" |
| Actions line lint (≥ 2-word verb + object labels, no bare numbers, no "I'll…" steps that only Matt can do) | action | Continue: print a corrected `**Actions:**` line only (needs test §8 #2) |
| Voice task finished without `voice_reply.py` | action | Continue: send the voice reply |
| Reply says "saved as a rule" but nothing changed in the rule files this turn | action | Continue: save it now |
| Coordinator started a session but didn't update `threads.json` | action | Continue: update the registry |
| New repo or `~/projects/<new>` this session, no `NOW.md` line (Slub core 1) | action | Continue: add the line |
| Code edited after the last run/test command | action | Continue: "run it or a test, then report" (shadow first; heuristic) |
| Over 150 words with no detail asked for; "**You:**" shorthand; bare `~/` paths; `open https://` commands; unlinked `local_` ids; `[Your Name]` placeholders | prose | Nothing now. On the next prompt from Matt, one line: "your last reply was 240 words / had 3 bare paths; keep this one ≤ 100 and link paths." Logged as a signal. |

All failing action checks fold into **one** message per turn. `stop_hook_active` true means nothing fires. An escape hatch, `<!-- rules: skip <id> because … -->`, logs the reason instead of fighting (the action-bar mod must hide it).

### 3.7 Model judges (coordinators only)

A §8 unchanged: an async `asyncRewake` command hook on the coordinator's Stop. A deterministic precheck runs first: the reply asks something, or the turn did more than 8 non-registry reads. Only then does a background `claude -p --model haiku` judge run (use the alias, never a hard-coded ID). It wakes the coordinator only on a violation.

The four judgments, all evidenced by C:
- asked Matt for an OK it didn't need;
- did analysis instead of routing;
- relayed a project coordinator's update;
- told Matt to do something an agent could do.

Each runs in shadow for a week; Matt checks 10 verdicts before it goes live.

### 3.8 The learn loop (Matt's ask, A §13, simplified)

1. **Capture, every turn, no model.** Signals go to `~/.claude/rule-state/signals.jsonl` (local only, pruned after 60 days):
   - corrections from Matt;
   - explicit rule statements ("from now on…");
   - explicit rules that never got saved;
   - checks that were ignored;
   - a deny followed by a similar allowed command (a workaround);
   - skip comments.
   Unsaved rules also trigger the "save it now" action check, which is the fast lane.
2. **Weekly review, one Sonnet session** (skipped when `claude_pace.py` says the week is over pace). It reads the signals, pulls small transcript windows and proposes **at most 3** rule-file diffs, built from the real moments as tests, all starting in shadow. Proposals come in this order: adherence fixes (move a broken rule up a channel), then trigger fixes, then merges and retirements, then new rules (≥ 2 independent signals, or one explicit unsaved statement). *Change from A:* no daily Haiku triage stage. At about 40 signals a week, one session can read them all directly.

   The same session also does two more jobs:
   - It samples a few firings per rule and judges whether the agent understood the rule. Those are the dashboard's "misread" numbers (§3.11). Doing this per turn would cost quota across 15+ threads.
   - It gives each beta rule's promotion advice (§3.10).
3. **What happens to a proposal.** It runs silently in shadow for 3 days. Then:
   - **An additive reminder or action check** may go **beta**: live and tagged, with no 👍 needed, within §3.10's limits.
   - **Anything else** (a block, a core line, a change to an official rule, a retirement) waits for Matt's 👍 in the Coordinator: one plain sentence per proposal plus an Actions line. Apply = merge, build, shadow for 3 days, then live if it fires as estimated. Skip = suppressed for 60 days. No answer in 14 days = it expires quietly.
   - **Shared (`slub`) proposals** also go to `inbox/tyler.md`. They never go beta, because a beta rule is `matt-only` until it's promoted.
4. **It can't die quietly.** The Coordinator's per-turn fact line says "learn loop last ran N days ago" once N > 10. The loop also pauses itself and says so once if acceptance stays under 30% for 4 weeks, or if one rule file gets churned more than 3 times in 30 days (the Hermes curator looped for 25 days unnoticed).

### 3.9 Testing and measurement

- Inline fire/pass tests per rule.
- Unit tests for each named check.
- **Replay** of the dispatcher over C's ~535 transcripts using the C scripts (`docs/rules-hooks/c-scripts/`), which gives firing rates and false positives before anything goes live.
- A golden set of 30 hand-labelled final replies for the Stop checks.
- A p95 latency test (≤ 30 ms on pure-regex paths).
- A weekly `rulehook.py report` with fires per rule, compliance (e.g. a commit within 2 calls of the nudge) and skips with reasons. Rules firing more than 50 times a week with low compliance get rewritten. Rules with zero fires in 30 days get their trigger checked, then expire at `review`.

### 3.10 Beta rules: agent-written, live, fenced in

Matt's reply: agents should be able to write rules ("asking my mom to approve rules is useless"), as a lower tier of experimental rules that never override official ones. A dot shows when they're running, and they get promoted on evidence. He also wants to stay in the loop while the system is being designed. The advisor's critique (§2) holds: the idea is right, but each part needs a mechanical edge.

`mode` gains a value between shadow and live: `off | shadow | beta | live`.

**Hard limits.** The compiler refuses any beta rule that breaks one, so none of these depend on wording:

| Limit | Why |
|---|---|
| **Additive only:** a just-in-time reminder or an action check. Never a block, never a core line, never a safety, school, secrets or screen-input rule, and never anything that relaxes, exempts or skips another rule. | Stops an agent annoyed by a check from writing its own exception |
| **No trigger overlap with an official rule** (same event + tool + pattern) | This is how "never overrides official" is enforced. Models don't reliably apply priority between two conflicting injected lines. |
| **Tagged `[rule:beta:<id>]`** on every injected line | The "dot" is display only and works only in the desktop app (a mod reads `mode: beta` in the index). The tag is visible everywhere: in the CLI, over Remote Control, in transcripts. |
| **At most 5 beta rules live at once** | Growth is problem #4 (§1). Beta must not regrow the pile. |
| **Expires 21 days after going beta** unless promoted | No silent accumulation |
| **`circle: matt-only` until promoted** | Nothing experimental reaches Tyler |
| **`target:` named when it's written:** which signal it should reduce (a correction type, a check failure) | "Two weeks, no issues" is weak evidence. Matt rarely complains, so silence is the default either way. |

**Promotion to official.**
- The weekly review compares the rule's `target` signal before and after, and recommends promote, extend or drop. "No issues" only rules out harm; promotion needs the target to have moved.
- **While the system is being designed, promotion needs Matt's 👍** (shared rules: Tyler's too).
- Every recommendation and Matt's answer are logged. Once about 9 in 10 of the agent's promotion calls match his, promotion of *additive* rules can go automatic. That's the same calibration as the §3.7 judges, and it's the route to a version his mom could use, based on data rather than hope. Blocks and core lines always need a 👍.

**Rollout.** No change to the step order. `beta` is one more enum value in step 2's format, and the first beta rules can only come from the learn loop (step 9).

### 3.11 The rules dashboard

Matt: "a really fucking good idea". He wants to see every rule; switch rules on and off; see what's enabled, how often each one fires and how often it's misread; why it exists; overlaps, dependencies and clashes; and gaps where a rule is missing.

**It's a view over data the plan already produces.** Building it before that data exists would show nothing.

| Panel | Source |
|---|---|
| Every rule: kind, circle, mode (beta shown with its dot and expiry), why, since, review date | Rule files |
| How often it fires, by role, plus compliance | `fired.jsonl` + the weekly `rulehook.py report` |
| Troublesome or misread | Sampled judge verdicts from the weekly review (§3.8); never a per-turn audit |
| Overlaps (shared triggers) and dependencies (relies on / relied on by) | The compiler, from triggers and `requires:` (free and deterministic) |
| Clashes in meaning | One model check per rule change, at compile time, stored with the rule |
| Gaps | Signals with no matching rule (corrections the weekly review couldn't map) |
| Beta rules and their promotion advice | Rule files + the weekly review |

**Versions**
- **v0, at the ⏸ Reassess gate:** the before/after table of C's numbers, rendered as one page.
- **v1, after step 5** (the registry migration), when every rule is a file with a mode: the panels above.

**Toggles.** On/off writes the rule's `mode` into `slub-hq/setup/matt/overrides.md` (never into the rule file itself). The first choice is to expose those modes in the existing ⌃⌥⌘T Tweaks panel, which already renders switches from JSON, instead of building new toggles (the shared-modules rule). A toggle takes effect on the dispatcher's next call.

**Local only.** It shows Matt-only rules (school, Mac paths), so it's served at `pages.test` and **never deployed to Vercel**.

**Existing tools checked** (advisor §3.2): none fits.
- Langfuse's prompt labels are the beta/official idea, so copy the concept. Don't adopt the tool: it's built for API apps, heavy to self-host, and protected labels are paid.
- Claude Code's OpenTelemetry export and cc-observatory cover usage, not rules.
- rulesync and agentsync only sync text.

Keep `fired.jsonl` in OTel event shape, so a Grafana view can be added later at no cost.

---

## 4. The slimmed rule set

The kinds below use §3.2's names: **block**, **remind** (just in time), **check** (end of turn), **judgment** (core), **auto**, **delete**. The detailed "why" for each verdict is in B §4. I've added a reason only where my call differs from B's or wasn't settled there.

### 4.1 Delete or shelf (step 0)

| Rule | Why |
|---|---|
| Universal progressive disclosure (`<details>`, `<br>`, span max-width) | It contradicts "the Code tab shows raw HTML". Keep the idea as a Slub product pattern in IDEAS, not as a rule. |
| Span-only styling invariant | A Gemini-era renderer patch; wrong on every surface now. Also remove it from `ui_web.md` and the Codex frontend pack. |
| `thread.md` deprecation | A rule about something that no longer exists |
| Agent logs, `DEVELOPMENT_JOURNAL`, `wiki-engine`, project board | Dead since about 10-20 (the tool isn't even installed; Linear replaced the board) |
| `preflight.py` before any work | Last ran 10-27; it mostly checks an Antigravity quota. Pulling is rarely needed, since this Mac is the main writer. |
| Emoji quick replies, "Reply 👍 to…" (rules, `~/.claude/CLAUDE.md`, memory) | Reactions don't work in the Code tab since 10-27; the Action bar replaced them |
| Projects-era routing (`cmsg_`, warm-thread 45 min, 30-thread cap, `/coord`, pointer-only project instructions, same-experience-in-project-threads) | Projects mode was dropped on today's call. Shelf it. |
| HANDOFF.md after ~40 messages | Contradicts the 250k hook |
| Path migration `matthewmurphy` → `matt`; project-root detection advice | Finished, or just script advice |
| Model family naming | Cosmetic, and it clashes with the exact model IDs the harness provides |
| Skill/workflow parity with `~/.gemini/global_workflows` | Antigravity is shelved |
| `gemini_only.md`, `subagent_leaf.md`, `LEAF.md`, `codex_only.md`, `ios.md`, most of `mac_env.md` | Shelved tools or no content. The TCC reset tip moves to saved methods. |
| "Migrate any npm project to bun before your main task" | Forces scope creep into every task. The ban itself stays (§4.4 E). |
| "New utilities welcome / from-scratch flag lifted" | Suspended by the freeze: kept in its rule file as `mode: off`, so it isn't lost |
| Memory files that restate rules (`make-it-live-by-default` "offer undo", `emoji-quick-replies`, and similar) | Memory holds facts; rules live in one place. Two of these already contradict the rules. |
| The three-copies rule ("save in `.rules/`, `~/.claude/CLAUDE.md` and the project instructions") | It is what creates the drift. Replaced by: one rule file, then build. |

### 4.2 Merges

| Into | From |
|---|---|
| **Act or wait** (new, §4.4 A) | Always push · make it live · obvious wants · ideas wait for 👍 · restate complex logic · drive the web app yourself · close threads without asking |
| **Palette only** (UI pack) | Never terracotta · no orange · light mode default (3 copies) · never invent a colour |
| **One design flow** (UI pack) | Think alone first · curated exemplars · 3–4 separately made options · UI Mixer · match a named style |
| **Hand over the work** (core) | "Try this" comes with a command · folder link + run command · link every file/folder/service/thread |
| **Ideas in files** (core) | Matt's ideas rule + Slub core rule 4 |
| **Reminders pack** | Apple Reminders · no sleep reminders · habits off the calendar (each was stated 3 times) |
| **HUD pack** | HUD slots · HUDs move/resize/snap · live tweaks (narrowed to UI and feel work) · shared modules |
| slub-hq `CLAUDE.md` | Drop its re-numbered copy of core rules 1–7 and keep `@setup/core.md` |

### 4.3 New rules

| Rule | Kind | Why |
|---|---|---|
| **Act or wait** (§4.4 A) | judgment + check | The root of C's top behavioural failure |
| **Conflict order:** safety > Matt's latest explicit words > freeze > everything else | judgment | One line prevents many wrong guesses (B §6.9) |
| **Checkpoint and done.** Each project names its next checkpoint (0.0.1 style). Done = tested, pushed, live or installed, `NOW.md` updated, the other person told if it touches him. Flag polish past the checkpoint once. | judgment | Turns "call out wheel-spinning" into something checkable. Matt on the call: "fighting the urge to keep improving will be a constant." |
| **Honest saved-rule claims** | check | C #4: a coordinator called a project-memory note a global rule |
| **Memory isn't rules.** Writing always/never/from-now-on wording into a `memory/` dir → "memory is this project only; global rules go to the rule files (project coordinators: send it to the Coordinator)" | remind (PostToolUse) | C #4 (10-29 Glass TV Coordinator) |
| **Cost note before fan-outs:** the 3rd `start_session`/Agent in one turn, or a reel/TTS/deploy → state the rough cost in one line | remind | Fan-outs have no budget today (B §6.5) |
| **Permission allow-rules** for `git push` / `gh pr merge` (crossword `main` stays denied) | settings | C: about 16 OK asks were forced by the classifier, not chosen by the agent |
| **Active-project limit:** ≤ 3 `NOW.md` lines per person | *proposal only* | It's a Slub-circle rule, so it needs Tyler's yes. Offer it; don't adopt it alone. |
| B's "48h school due dates at Coordinator start" | *not adopted* | B itself rates it weak, with nag risk, and the habit gate already covers logic practice. Matt can ask for it. |

### 4.4 The full register

#### A. How agents decide and talk (mostly judgment, in the core)

| Rule | Kind | Trigger / note |
|---|---|---|
| **Act or wait.** Wait only for (a) an idea Matt hasn't asked you to build, (b) something irreversible or that reaches other people or the public, (c) a real fork where his taste decides and the outcomes differ, (d) the visual direction of a new product. Otherwise do it, test it, push it, make it live, then report. | judgment + **check** | Stop: an ask phrase about commit/push/merge/live/close/archive/start-a-thread, or any ask phrase while a touched repo is dirty or unpushed → continue. Coordinator judge for "plain wants". |
| Every word costs Matt (≈ 8 lines + one before/after example) | judgment + prose check | Reader = Matt, > 150 words, no detail asked → reminder on the next turn |
| Clarity beats brevity; no "You:" shorthand | judgment + prose check | Regex `^\*\*You:` |
| Important things go in the reply, never only in a file | judgment | — |
| **Details file only for overflow**; Readthrough and reel on request | judgment | Formatting quirks (per-bullet anchors, `---` spacing, 2-word bold labels) move to a details-file how-to |
| Read-aloud: no repeats | judgment | — |
| One plain-text question at most; menus only for quizzes | judgment + **block** | AskUserQuestion with any `multiSelect: false` → deny (step 5) |
| Action bar format | judgment + **check** | Actions lint (action check) |
| Hand over the work: link threads, files, folders, services; folder link + run command after changes | judgment + prose check | Bare paths, `open https://`, unlinked `local_` ids, linked `.md` that doesn't exist |
| "Why did you do that?" gets the real cause first | judgment | All agents, not just coordinators |
| No placeholders; identity file only when needed | remind | PostToolUse on Write content matching `\[Your [A-Z]`, plus the prose check |
| Rules Matt gives: one rule file + build; say "saved for all your agents; offered to Tyler in his next digest" | judgment + **check** + remind | Write in `.rules/`/`rules/` → "run the build"; dishonest claim → check |

#### B. Life and school

| Rule | Kind | Trigger |
|---|---|---|
| **School: never write graded work** | judgment (1 line) + **block (`ask`)** + remind | Edit/Write/Bash writes under `~/Documents/School/**`, `~/projects/school/**` or course-code folders (from `SCHOOL.md`) → `ask` Matt + inject the school pack. Reads → inject once per session. |
| PHIL 120 ramp; the allowed list (explain, hint, critique, subtractive trims, the three `_…-without-ghostwriting` skills) | remind | School pack |
| Quizzes via `_quiz-with-tap-menus` | remind | Matt says "quiz me / study / practice" |
| Apple Reminders (+ no sleep reminders, habits off the calendar) | remind | Matt's prompt has to-do wording (remind me, I need to call, by Monday, follow up) |
| Music: resolver links, no AI music | remind | Music words in Matt's prompt |
| Obsidian vault path | remind | Note / wiki / vault / Obsidian words |
| Old AI threads (`threads.py` recipe) | remind | "Gemini", "Antigravity", "that earlier conversation" |
| ABOUT_MATT first; search the Mac before asking | judgment (2 lines) | — |
| QMD recall | auto (exists) | — |
| Voice tasks report back | **check** (action) | The prompt began "🎙️ Voice task" and there was no `voice_reply.py` call |
| Check-in habit gate | auto (exists) | — |

#### C. Coordinators (role pack, injected at SessionStart and after compaction, coordinator roles only)

| Rule | Kind | Trigger |
|---|---|---|
| `code-coordinator.md` / `project-coordinator.md` content (split before routing, meta stays, starting threads, briefs, say nothing after starting, show 5 at a time, housekeeping without asking) | remind (role pack) | SessionStart for `central` / `project-coordinator`. Fix its stale "details files and emoji replies" line in step 0. |
| Thread size 250k | **block** (exists) | SendMessage |
| Model by pace | remind (fact) | PreToolUse `start_session` / Agent: the current `claude_pace.py` verdict (10-min cache) |
| Registry updated after starting a thread | **check** (action) | — |
| No analysis in the coordinator | remind + judge | More than 8 non-registry Read/Grep calls in one turn → "route this to a thread" |
| Don't relay project coordinators' updates; start the thread for an obvious bug | judge | Coordinator Stop (shadow first) |
| Project coordinators forward global rules to the central one | remind | Memory-save reminder in project-coordinator sessions |
| **Big asks go to an advisor first** (Matt, 2026-10-29). The coordinator stays Opus at low effort. For a big ask it saves Matt's message to `docs/coordinator/asks/`, starts one Opus xhigh advisor that writes a numbered action list but takes no actions, then carries the list out as written. Full text: `code-coordinator.md`, "Big asks go to an advisor first". | remind (role pack) | UserPromptSubmit, role `central` or `project-coordinator`, sender = Matt, and the prompt is over ~350 words or has 4+ separate asks → inject the advisor rule (advisor answer §6). Phrases like "correct me if I'm wrong", "think hard" and "critique" trigger it too. Parts that depend on each other stay judgment. |
| Cloud: blocked sites go through the Mac | remind (role pack) | Cloud sessions only. Caveat: cloud sessions don't run user-level hooks (§9). |

#### D. Building and design

| Rule | Kind | Trigger |
|---|---|---|
| Test or run after every change; report honestly | judgment + **check** (action, shadow first) | Code edited after the last Bash run/test |
| Fix root causes; don't strip custom work (span clause removed) | judgment | — |
| Marginal change; checkpoint and done; call out wheel-spinning | judgment | — |
| **Freeze** (end condition: until Matt says the Tyler merge has started) | judgment | — |
| Look for existing tools first | judgment + remind | New-project signals: `git init`, `gh repo create`, `pages new`, `mkdir ~/projects/<new>` |
| Slub check-before-building (pull, read `NOW.md`/`IDEAS.md`) | remind | Same new-project signals |
| Systems over one-offs; save working methods | judgment | — |
| Ship-ready = self-contained, README, one-step run; settings and onboarding only for "for the world" builds | judgment | — |
| Ideas: log with an honest take, build waits for 👍 (ideas stated as ideas, not asides) | judgment + remind | Idea wording in Matt's prompt ("what if", "idea:", "could we") |
| **One design flow:** new UI or redesign → if Matt named a style, restate its traits; show 3 exemplar links or quick renders (light and dark); he picks; build; compare side by side with the reference. Offer "think alone first" once for open-ended product UX. Separately-made options and the UI Mixer only for "for the world" Slub products, or when he asks. | remind (UI pack) + remind | UI files; Matt's prompt says "redesign / new UI / new screen" |
| UI pack: palette roles only, light and dark, no stock look, icons not text alone, every press shows it landed, discoverable, no orphans, Esc/click-outside closes modals, Mantine over hand-rolled widgets, no Tailwind unless asked, pages live in `~/projects/pages` | remind (pack) | `**/*.{css,scss,html,tsx,jsx,vue,svelte}`, `pages/**`, `*.swift` views |
| Palette | **blocked on Matt** | No palette is picked (since 10-22), so "never invent a colour" can't be followed. A colour lint comes only after he picks one, or blesses an interim one. |
| No orphans | auto | `orphans.cjs` runs inside `pages deploy` |
| HUD pack: slots, move/resize/snap, Tweaks, shared modules | remind (pack) + auto | Swift/hud-kit/Hammerspoon HUD files; PostToolUse on `hud_slots.json` runs `hud_layout_test.lua` |
| Hammerspoon pack: reload method, `withInput` / `claude-control lock` for automations | remind (pack, dispatcher-injected) + auto | `~/.hammerspoon/**`, `qwerty-midi-hammerspoon/**`; PostToolUse runs that project's reload |
| Menu bar: ask Matt to click through it | remind | Edits containing `NSStatusItem` / `hs.menubar` |
| puma-dev `.test` domains | remind | Starting a dev server, editing `launch.json` |
| VPS database first | remind | Database/hosting words in Matt's prompt |
| Verify model IDs before hardcoding | remind | Write/Edit content with `claude-` / `gpt-` / `gemini-` strings |
| Pages on Vercel, not Artifacts; shareable Markdown via `pages md` | remind | PreToolUse on the Artifact tool (fights the harness prompt, so it needs a reminder) |
| Skills: `_` prefix, action-first names; run `sync_skills.py` | remind + auto | Writes under `skills/` |
| Vendor code secret scan | remind | `git clone` or vendor/fork wording |
| AbletonMCP routing | remind | Ableton words |
| Git tracking, narrowed to `~/projects/*` and config folders, mentioned in one line | judgment | — |
| AG_CONTEXT.md | remind (fact) | SessionStart: "this project has AG_CONTEXT.md (N lines); read it before changing code" |

#### E. Safety and the machine (mostly blocks)

| Rule | Kind | Step | Note |
|---|---|---|---|
| Secret reads | **block**, fail closed | 1 (`Read` via `permissions.deny`), 5 (Bash `cat/head/grep/less` on `.env*`) | `.env.example` is blocked too; acceptable. The deny text names `aios-env` and "open it in VS Code for Matt". |
| Commit secret gate | auto (exists in `auto_commit.py`) | — | — |
| Screen input without a `claude-control` ticket | **block**, fail closed | 1 | Extend `input_guard` to `mcp__computer-use__*` and the Chrome `computer`/`form_input` tools (C: 31 unguarded calls). The 700 words of tool docs move to `claude-control --help` and the deny text. |
| `hs -c 'hs.reload()'` | **block** | 1 | Added to the hang guard. Two ~50-minute hangs on 10-28, and the rule reaches no session today (B §3.1). |
| Hang guard, browser-pane guard, thread size | **block** (exist) | — | — |
| Push to `daily-mini-crossword` `main` | **block** | 1 | Must land with, or before, the allow-rules |
| `rm`/`rmdir`/`find -delete`/`find -exec rm` outside tmp, scratchpad, caches, `node_modules`, old worktrees | **block** | 5 | The 10-23 allowlist, not the old "never rm" |
| npm/npx/pnpm/yarn → bun | **block** | 5 | Ignore matches inside heredocs (C's false positives) |
| `gh repo create` without `--private`; `git init` in `~` | **block** | 5 | — |
| System `/tmp` (allow `/private/tmp/claude-*`) | **block** | 5 | — |
| Automations take the input queue | remind | 6 | Hammerspoon/KM pack |
| No command may hang a thread | auto (exists) + 1 core line | — | — |
| Never act as someone else (Slub 8) | judgment | — | — |

#### F. Slub core (`setup/core.md`, circle `slub`; changes need both Matt and Tyler)

| Rule | Kind | Note |
|---|---|---|
| 1 Visible by default | judgment + **check** (action) | New repo or project folder this session, no `NOW.md` line → add it |
| 2 Check before building | auto (pull exists) + remind | New-project signals |
| 3 Look for connections | judgment, **reworded with a trigger**: "when your work touches a repo, file or idea named in NOW/IDEAS/notes, say so in one line" | Tyler called it vague |
| 4 Ideas in files | judgment | Merged with Matt's ideas rule |
| 5 Tasks per person | auto | `slub-sync.sh` should surface `TASKS.md` (it doesn't today) |
| 6 Inbox | auto (exists) | — |
| 7 Model-neutral, Slub-only | remind | Edits in slub-hq |
| 8 Never act as someone else | judgment | — |
| Header "forever" | reword | Pending Tyler's OK (call decision) |

The **draft core** (what every session always loads) is in Appendix A: about 55 lines including the Slub core. Today that's ~17,000 words in ai-os and ~4,100 elsewhere.

---

## 5. Rollout

Ordered by C's cost ranking. Each step is small, testable and can be undone on its own. Nothing is deleted until its replacement is live and measured, except dead rules (step 0).

| Step | What | C/B evidence it addresses | Done when | Undo |
|---|---|---|---|---|
| **0. Text fixes** (no code) | (1) Delete §4.1. (2) Write *act or wait* + the conflict order. (3) Put the school line, the freeze and act-or-wait into `~/.claude/CLAUDE.md` now (missing outside ai-os). (4) Fix the rm, "syncs to Tyler", emoji and details-file lines. (5) Delete contradicting memory files. (6) Fix `code-coordinator.md`'s stale lines. (7) Replace the three-copies rule with "one place + build". | B §3.1–3.2, §5; C "fix the conflicts before hooking them" | grep finds none of B §5's contradictions; a session in a non-ai-os folder sees the school, freeze and act-or-wait lines | Back up `~/.claude/CLAUDE.md` first (it isn't in git); `git revert` for the rest |
| **1. Tool-moment gaps on existing guards** | (a) School guard: small standalone hook, `ask` + inject. (b) `hs.reload` pattern added to the hang guard. (c) `input_guard` fail-closed + computer-use/Chrome matchers. (d) Crossword `main` deny, **then** allow-rules for push/merge (after test §8 #3). (e) `permissions.deny` for secret `Read`s. | C #3, C "not rule breaks", B §3.1, C (31 unguarded input calls) | Fire/pass tests per change; replay over C's transcripts shows no false positives; a test session editing a lab file gets the `ask` | Remove the settings lines; `git revert` the guard edits |
| **2. Stop dispatcher** (shadow, then live) | `rulehook.py` skeleton (state, log, kill switch, shadow), sender/reader classification, the minimal rule-file format + compiler step. Action checks: OK-ask, Actions lint, voice task, honest saved-rule claim. Prose checks as next-turn reminders. Signal capture starts here. | C #2 (6 complaints), #6, #5, #8 | Replay + golden set ≥ 90% right; 3 days live shadow with < 1 false nudge a day; then live | `mode: shadow`, or the kill switch |
| **3. Saving rules and handoffs** | Memory-isn't-rules reminder; rule-file write → "run the build"; role resolution; pace fact on `start_session`. Separately, the thread that built the 10-30 inbox forwarder tests it end to end (C #4: delivery must not depend on reading a file at session start). | C #4 | A test write of "always X" to a project memory triggers the reminder; the forwarder delivers a test line to the live Coordinator | `mode: off` |
| **4. Coordinator role pack** | SessionStart injection for coordinator roles (also after compaction); registry check; "no analysis" reminder; SubagentStart leaf digest | B §4.6, A §6 | Coordinator and worker sessions see different digests; a compacted coordinator still has its pack | `AIOS_RULES_ROLES=off` |
| **⏸ Reassess** | Re-run C's scripts on the week since step 2. That table is **dashboard v0** (§3.11): one local page. | — | Matt sees one before/after table: OK-asks, reply lengths, Action labels, complaints. **If the main numbers are fixed, steps 5–10 are optional.** | — |
| **5. Registry migration + low-evidence blocks** | Move `.rules/` text into rule files area by area. Port the Codex `tool_guard` rules *from the rule files* (rm incl. `find -delete`, npm, `/tmp`, `gh --private`, `git init ~`, Bash secret reads) + the quiz `multiSelect` deny. Shadow 2 days. Optionally fold the four old guards into the dispatcher. | B §3.4, C (insurance) | Shadow log clean; the compiler passes with every rule having a kind and tests | `mode: shadow` per rule |
| **5b. Dashboard v1** | The local page over the rule files, `fired.jsonl`, `signals.jsonl` and the weekly report; rule modes exposed as switches in the Tweaks panel through the overrides file | Matt's reply, part 2 | Every rule shows its mode, fires and overlaps; flipping a switch changes the dispatcher's next decision | Stop serving the page; the overrides file reverts with git |
| **6. Packs and prompt reminders** | UI, HUD, Hammerspoon, school (fold in step 1's hook), reminders/music/old-threads/ideas/rules prompts (sender = Matt), the advisor-escalation reminder for coordinators, AG_CONTEXT fact, Artifact → pages, skills, model IDs, fan-out cost note, `NOW.md` check. Batches of ≤ 10, shadow each. | B §4 | `InstructionsLoaded` shows the packs loading; < 1 prompt reminder per 5 of Matt's prompts | Delete the generated pack files; `mode: off` |
| **7. Shrink the core** | Generate `~/.claude/CLAUDE.md` (≤ 60 lines) from the rule files. `ai-os/CLAUDE.md` becomes ai-os project notes only. A rule's text leaves the core after its hook has been live a week, **rule by rule**. | B §3.1, A §1 | Core ≤ 60 lines; C's numbers re-run and no worse | Rebuild with `--full` |
| **8. Coordinator judges** | The four async judges, shadow for a week | C #2 (coordinator plain wants), #7 | Matt agrees with 9 of 10 sampled verdicts | `mode: shadow` |
| **9. Learn loop review + beta rules** | First weekly review after ≥ 2 weeks of signals. From then on it may put additive rules in beta (§3.10). | Matt's ask and reply | Matt keeps or kills it after the first report; beta rules stay within the limits, checked by the compiler | `mode: off`; unload the job; all beta rules → `off` via one override |
| **10. Tyler** | §7: export, plugin or settings install, offers in shadow until he says Yes | Call decisions | Tyler's agent explains the shared rules in plain English, and he says Yes or No to each | Uninstall the plugin |
| *(later)* Codex adapter | `tool_guard`/classifier read `rules-index.json` | A §1 (guard drift) | — | — |

**Targets** (C's scripts re-run two weeks after step 2):
- replies to Matt that end by asking for an OK: 15% → < 5%;
- Code-tab worker replies to Matt over 150 words: 47% → < 20%;
- one-word Action labels: 0;
- oversize sends: 0;
- agent writes to school files without Matt's `ask`: 0;
- always-loaded rules: < 1,500 words in every session (today ~17,000 in ai-os, ~4,100 elsewhere, with the school rule missing).

---

## 6. How it works for each kind of session

| | Central Coordinator | Project coordinator | Worker (Matt-facing) | Worker started by a session | Subagent |
|---|---|---|---|---|---|
| Always loaded | Core (≤ 60 lines incl. Slub core) | Core | Core | Core | Leaf digest (5 lines, SubagentStart) |
| SessionStart / after compaction | Coordinator pack, registry path, own id | Coordinator pack + project-coordinator delta + project name | AG_CONTEXT fact | AG_CONTEXT fact | — |
| Blocks | All | All | All | All | All (they're tool-level) |
| Reminders | Pace on `start_session`, send size/title, rule saves, memory saves, no-analysis | Same + "send global rules to the Coordinator" | Packs, new-project, rule/memory saves, prompt reminders (sender = Matt) | Packs, new-project | None |
| Action checks | All, incl. registry update | All, incl. registry update | All | Repo, voice and NOW.md checks only (the reader is an agent) | None |
| Prose checks | Yes (Matt reads) | Yes (Matt reads, unless the sender was a peer) | Yes | No | No |
| Model judges | 4, shadow first | Later, if the Coordinator's prove useful | No | No | No |

**After compaction:** SessionStart with `source: compact` re-injects the role pack. Today a compacted coordinator relies on remembering a file it read hours ago.

**Cloud sessions** don't run Matt's user-level hooks, so they get only what a repo's own settings and `CLAUDE.md` give them. They're rare now that Projects mode is dropped; accept the gap.

---

## 7. Sync to Tyler

Built on A §11 and B §3.3, shaped by today's call.

**Circles** (Matt's word on the call), as the `circle:` tag:

| Circle | Who | How it reaches Tyler |
|---|---|---|
| `shared-core` | Matt, Tyler, Kristy | Live for everyone. Today that's one rule: projects are visible by default. |
| `slub` | Matt and Tyler, on Slub work | Live for both, from `slub-hq/setup/rules/`. Changes need both to agree. |
| `matt-recommended` | Matt's defaults that might suit Tyler | Exported (sanitized) to `slub-hq/setup/matt/rules/`. **Off on Tyler's Mac until he says Yes.** |
| `matt-only` | Matt's Mac, life, school, Hammerspoon | Never exported, never in Tyler's queue |

**How it ships**
- **Code:** the dispatcher is a `slub-rules` plugin in the existing `slub-mods` marketplace, *if* plugin command hooks fire in the desktop Code tab and over Remote Control (§8 #5). Otherwise INSTALL.md gains one step that adds the settings lines. Python stdlib only; paths come from env (`AIOS_HOME`, `AIOS_REGISTRY`).
- **Rule files:** read live from slub-hq, which `slub-sync.sh` already pulls at every session start. A shared rule edit reaches Tyler on his next session with no plugin update.

**Tyler's worries from the call, and the answers**
- *"If your handoff rule quietly overrode mine, I'd think something was broken."* Offers arrive switched off. Every injected line is tagged `[rule:id]`, and `rulehook.py why <id>` prints the rule's file. A `conflicts` report lists his own rules that touch the same triggers. `params` overrides let him keep his own thresholds without forking a rule.
- *"Psychotic levels of clarity."* Every few days (the call's cadence) his agent gets one digest of new or changed `matt-recommended` rules. Each has a plain-English line on what it changes in practice, then Yes / No / Later. This reuses `CHANGES.md` and `slub-answers.json`, deduplicated and titled by the rule's own name, not its section. Changes to how slub-hq itself works also get a short note in `inbox/tyler.md`.
- *Rules he can't run.* The export lint refuses Matt-only paths in anything offered to him.

**His own data stays his.** His agent can run the same learn loop on his own signals; signals never leave the Mac they were captured on.

**Kristy** gets only `shared-core`, which is also the only rule she asked for.

---

## 8. Must-test before building (each blocks the step named)

1. **How a Stop continuation looks in the Code tab** (step 2): does Matt see the "Stop hook feedback" line and a second message, and does read-aloud read both? This confirms §3.6's split.
2. **Does the action-bar mod pick up an `Actions:` line from a continuation?** (step 2: Actions lint)
3. **Do permission allow-rules stop the auto-mode classifier from forcing an ask on `git push origin main`?** (step 1d) If not, drop 1d and live with those asks.
4. **Do user-level `~/.claude/rules/*.md` `paths:` globs match absolute paths outside the session's working directory?** (step 6) If not, the dispatcher injects all packs, as it already must for Hammerspoon and School.
5. **Do plugin `hooks.json` command hooks fire in the desktop Code tab and over Remote Control?** (step 10)
6. **Role lookup** from the desktop session metadata, plus its fallbacks (step 3).
7. **Is do.test still needed** in the Code tab, now that plain markdown links open in the file pane? (step 0 wording)

---

## 9. Risks

- **A dispatcher bug breaks every session.** Mitigations: fail-open, the kill switch, shadow mode, replay tests, and the fail-closed rules in separate handlers.
- **Reminders become wallpaper**, as `CLAUDE.md` did. Mitigations: the `once` defaults, character caps, facts over principles, reader-aware checks, the weekly report, and expiry dates.
- **Blocks teach workarounds** (Codex: `find -delete`). Mitigations: keep blocks few, test known workarounds, and log "deny, then a similar allowed command" as a signal.
- **Prose reminders arrive one turn late.** That's the honest limit: no hook runs before a reply is shown. Prose quality stays mostly judgment.
- **Shrinking the core can drop a rule that had no trigger.** Step 7 goes rule by rule. Each removed line must name the hook or pack that replaces it, or it stays.
- **School `ask`s may get frequent** during cleanup sessions Matt asked for. If so, add an "approved for this session" flag, or C's code-diff check.
- **Fail-closed input** blocks every `open`/focus while Hammerspoon is down. That's intended; the deny text gives the restart route.
- **Allow-rules widen what runs without a check.** Pushes are pre-approved by Matt, crossword `main` stays denied, and nothing else is widened.
- **The undocumented desktop metadata** used for role lookup may change. The env and title fallbacks still work, and a failure logs `role=unknown`.
- **Beta rules regrow the pile, or game the checks.** Mitigations: compiler-enforced limits (additive only, no trigger overlap, cap of 5, 21-day expiry, a named target), a one-switch kill for all beta rules, and promotion that needs a 👍 until the agent's calls have proven calibrated.
- **The dashboard becomes a project of its own.** v0 is one table and v1 is a view over existing files. No new backend, no hosting, toggles reuse the Tweaks panel.
- **The system itself becomes a project.** The reassess gate after step 4, and the stated targets, keep it honest.

---

## 10. Decisions only Matt can make

1. The six in [PLAN-summary.md](PLAN-summary.md): details file, allow-rules + act-or-wait, one design flow, weekly learn loop, school `ask`, and **beta rules going live without his 👍**.
2. **The freeze's end condition** (proposed: "until Matt says the Tyler merge has started").
3. **The palette**, or an interim one. Until then, the colour rules can't be followed or enforced.
4. **With Tyler:** the circles, the digest cadence, the `core.md` header wording, and the active-project limit.

---

## Appendix A: draft always-loaded core (≈ 55 lines with Slub core)

Generated, never hand-edited. Wording to be polished in step 7; shown so the budget is concrete.

```markdown
# Matt's core rules (generated from rule files; edit those, not this)
Other rules arrive just in time, tagged [rule:id]. Follow them.

## When rules clash
Safety (secrets, data loss, school, other people's accounts) > Matt's latest explicit words > the project freeze > everything else.

## Who and where
- Read ~/projects/ai-os/docs/ABOUT_MATT.md first; school schedule is docs/SCHOOL.md.
- Search the Mac (that index, QMD, mdfind, threads.py) before asking Matt about himself.
- Shelved unless Matt asks: Antigravity/agy, Hermes, Perplexity, DeepSeek, the LiteLLM proxy.

## Act or wait
- Wait for Matt only for: (a) an idea he hasn't asked you to build; (b) anything irreversible or that reaches other people or the public (messages, posts, purchases, publishing to his website); (c) a real fork where his taste decides and the outcomes differ; (d) the visual direction of a new product.
- Everything else: do it, test it, commit and push, make it live, then report. Pushes are pre-approved, main included (not daily-mini-crossword main).
- Restate logic before building only when it is truly complex and you're unsure you understood.
- If a tool or agent can do a step (including clicking through a web app in Chrome), you do it. Hand Matt a step only when it needs his password, payment, device or hands.

## Replies to Matt
- Line 1 is the answer, or the one thing he must do.
- Aim for ≤ 50 words, up to ~100 when clarity needs it; more only when he asked for detail. Clarity beats brevity: plain full sentences, no shorthand like "You: rename 3 states".
- One idea per line, bold the point, a blank line between lines, at most 4 items.
- Anything he must do, decide or worry about is in the reply, one short line each. Overflow goes to the details file (~/projects/ai-os/docs/details/YYYY-MM-DD-<slug>.md), linked last.
- At most one question, in plain text. Offered actions go in one last line: **Actions:** <verb + object> → <sentence> · … (only things you will do; ` | ` between either/or choices).
- Link every thread, file, folder and service you mention. After changing a project, give its folder link and one command or link that runs it.
- Read-aloud reads the whole turn: never repeat what a progress note said.
- "Why did you do that?" gets the real cause first, plainly.

## Building
- Test or run after every change; report the result honestly, failures included.
- Fix root causes; never strip existing custom styling or architecture.
- Small steps. Each project names its next checkpoint; done = tested, pushed, live or installed, NOW.md updated. Flag polish past the checkpoint once; call out wheel-spinning.
- Project freeze until Matt says the Tyler merge has started: no new projects, prefer simplifying.
- Look for existing tools first. Systems over one-offs. Shared modules over copies. Save working methods where the next agent will find them.
- Ship-ready = self-contained, README, runs in one step. Settings and onboarding only for "for the world" builds.
- Ideas Matt states: log them in the project's IDEAS.md (Slub ideas in slub-hq) with a 1–2 line honest take; building waits for his 👍.
- Rules Matt gives: one rule file, then the build; say "saved for all your agents; offered to Tyler in his next digest".
- School: never write, fix or generate graded work (code, essays, answers). Explain, hint and critique only.
- Secrets never go in chat, pages, logs or commits; check keys with aios-env.

## Slub (shared with Tyler; changes need both)
@~/projects/slub-hq/setup/core.md
```
