# Rules → hooks: architecture (angle A)

Design only, 2026-10-29. Nothing here is built yet. Siblings: B (rules audit vs Slub mission), C (failure evidence). The merge thread reconciles all three.

## 1. The problem in one paragraph

~480 lines of rules (`.rules/*.md` → CLAUDE.md, plus `code-coordinator.md`) are read once at session start, then compete with a growing transcript. By 150k tokens a rule from line 200 of `core_safety.md` is effectively gone. The failures today (no size check before a hand-off, waiting for OKs, lost bot hand-offs) were all *moment* failures: the rule existed, but nothing put it in front of the agent at the moment it mattered. `thread_size_guard.py` worked because it fires at that moment and can't be forgotten. The design goal is to do that for every rule where a moment exists, and to make CLAUDE.md small enough that the rest actually get read.

## 2. Four kinds of rule

Every rule gets exactly one primary `kind`:

| kind | mechanism | example | share (est.) |
|---|---|---|---|
| `block` | PreToolUse `deny` (or `ask`) with a reason telling the agent what to do instead | `rm` outside scratch; send into 250k+ thread; push to crossword `main`; reading `.env` | ~15% |
| `nudge` | just-in-time `additionalContext` on a matched trigger, 1–3 lines | editing a `.css`/UI file → "light+dark, palette roles, no orange, no orphans"; `start_session` → "Opus/Sonnet per pace, brief self-contained" | ~45% |
| `check` | Stop hook (or PostToolUse) that inspects what happened and blocks the stop once with a reason | reply >100 words with no Details line; uncommitted changes in a repo touched this turn; `Actions:` line missing when the reply offers choices | ~15% |
| `judgment` | stays as text in a slim CLAUDE.md; no deterministic trigger exists | "clarity beats brevity", "be candid on ideas", "think alone first on open design" | ~25% |

A rule can also carry a secondary kind (e.g. `nudge` on Edit of a UI file + `check` at Stop that a dark-mode check ran). Judgment rules are the honest remainder: hooks don't make taste reliable, and pretending they do adds noise.

## 3. Registry format

One file per rule area, YAML, in ai-os `rules/registry/` (keeps `.rules/` as the human-readable source during migration; later the `.md` files are *generated* from the registry, not the other way round).

```yaml
- id: no-rm-outside-scratch
  kind: block
  scope: [all]                 # roles: coordinator | project-coordinator | worker | all
  who: [matt, tyler]           # Slub-shared rules list both; Matt-only rules list matt
  on:
    event: PreToolUse
    tool: Bash
    match: { command_re: '(^|[;&|]\s*)rm\s' }
    unless: { command_re: '\brm\b.*(/tmp/|tmp/|node_modules|cache)' }
  say: "Don't rm here. Move it to ~/.Trash/ (rm is only for tmp/, caches, node_modules)."
  since: 2026-10-23
  source: "Matt, 2026-10-23"
  text: core_safety.md#safety-and-tooling   # where the full rule lives, for humans

- id: ui-light-dark
  kind: nudge
  scope: [worker]
  on:
    event: PreToolUse
    tool: Edit|Write
    match: { path_re: '\.(css|scss|html|tsx|jsx|swift|lua)$' }
  once_per: session            # fire the first time only
  say: "UI file: design light+dark, colours only from palette roles, no orange/terracotta, headings text-wrap:balance."

- id: details-line
  kind: check
  scope: [worker, coordinator]
  on: { event: Stop }
  test: details_line           # named Python check in rules/checks.py
  say: "Your reply has no Details: line. Append the details section and add the line."
  max_blocks: 1                # never block the same stop twice
```

Fields that matter:
- `say` is capped at 200 chars by the compiler (lint fails above). It is the only text injected.
- `once_per: session | turn | file | never` (default `turn` for nudges) is the main anti-noise lever.
- `scope` is matched against the session's role (§5).
- `test` names a function, so checks stay real code with tests, not regex soup in YAML.

## 4. One dispatcher, not fifty hooks

`settings.json` gets **one entry per event** pointing at `scripts/hooks/dispatch.py <event>` (matcher `*` for tool events, or a union matcher compiled from the registry to skip Python startup for tools no rule cares about). The dispatcher:

1. Reads stdin (session_id, transcript_path, cwd, tool_name, tool_input, prompt).
2. Loads a **compiled** registry (`rules/compiled.json`, written by `build_rules.py`; no YAML parsing at runtime).
3. Resolves role (§5), filters rules by event + tool + scope, evaluates matchers.
4. Applies `once_per` via a tiny state file `~/.claude/rule-state/<session_id>.json`.
5. Emits one combined output: any `deny` wins (reasons joined); otherwise all nudge `say` lines joined into one `additionalContext`, hard cap ~600 chars per call (lowest-priority dropped).
6. Logs one line per firing to `~/.claude/rule-state/fired.jsonl` (rule id, session, decision). This log is the evidence base for tuning (§8) and feeds angle C-style audits for free.

Existing guards (`bash_timeout_guard`, `browser_pane_guard`, `input_guard`, `thread_size_guard`) become `test:` functions called by the dispatcher, keeping their code and tests. Migrate them last; they work.

**Latency/cost**: Python cold start ~40–60 ms per call. Bash runs dozens of times per turn, so: compiled JSON, no imports beyond `json/re/os`, matcher union in settings so Read/Grep never spawn the dispatcher. Budget: p95 < 80 ms, checked by a test. Command hooks cost zero tokens; only `say` text costs tokens, and only when fired.

**Fail open**: every path is wrapped; any exception → exit 0, no output, and a line in `fired.jsonl` with `error`. One exception: `block` rules marked `fail: closed` (only `claude-control` input and secret reads) deny on error, matching the existing "fail closed" input rule.

## 5. Knowing the session's role

Hooks get `session_id` and `cwd`, not a role. Resolution order:
1. `coordinator/threads.json` registry lookup by session id → `central` / `project-coordinator` / worker.
2. Session title from the desktop metadata (`… · Coordinator`) — same lookup `thread_size_guard.title()` already does.
3. Default `worker`.

Cache the result in the session state file so it's one lookup per session. Tyler's machine: same code, his registry path from an env var (`AIOS_REGISTRY`), default worker if absent.

This is what makes coordinator-only rules ("no analysis here", "split before routing", "say nothing after starting a thread") stop polluting workers, and vice versa: the coordinator's CLAUDE.md load shrinks to its own rules.

## 6. Which event carries what

- **SessionStart**: role-specific digest (≤ 15 lines): the 10 judgment rules that matter for this role + "rules arrive just-in-time; obey `say` lines". Also re-runs after `/compact` (source `compact`), which fixes "rules forgotten after compaction" outright.
- **UserPromptSubmit**: keyword nudges on Matt's own words. "idea", "what if", "could we" → log-the-idea-with-honest-take. "remember/from now on/always" → save as global rule + say it syncs to Tyler. "quiz me" → quiz skill. "call/remind me/Monday" → Apple Reminders. Plus the existing qmd recall. Keep matchers conservative; false positives here are the noisiest of all.
- **PreToolUse**: blocks and tool-shaped nudges (Bash, Edit/Write by path, `start_session`, `SendMessage`, `AskUserQuestion` → "plain-text questions only, except quizzes", computer-use/Chrome tools → claude-control clearance check).
- **PostToolUse**: facts the agent just learned that trigger a rule: `git commit` succeeded but not pushed → "push now"; `start_session` returned → coordinator: "register it in threads.json, say nothing".
- **Stop**: deterministic checks on the final reply (from `transcript_path`): Details line present, word budget (> 150 words without a reel/details → block once), `Actions:` line format, uncommitted changes in a repo whose files this session edited, links on mentioned `local_` threads. `stop_hook_active` true → never block again (no loops). `max_blocks: 1` per turn.
- **PreCompact**: write a "rules that fired this session" digest so SessionStart(compact) can re-inject the ones that were relevant, not all of them.

## 7. Prompt-type and agent hooks: where, and where not

Claude Code supports `type: "prompt"` hooks (a small model judges the input and returns allow/block with a reason). Use them only in **Stop**, only for a handful of high-value judgment checks that regex can't do, and only on one role:
- Coordinator Stop: "Did this reply do analysis instead of routing?" / "Did it ask Matt for an OK it didn't need?" (today's failure).
- Worker Stop on replies > 80 words: "Is line 1 the answer or the one thing Matt must do?"

Cost: one Haiku call per stop (~1–2k tokens, ~1 s). Fine on the coordinator (low volume, high stakes); too slow and too noisy for every worker turn. Gate with a cheap deterministic precheck first (e.g. only run the "unneeded OK" judge if the reply contains `?` or "want me to"). Never use prompt hooks on PreToolUse: latency on every tool call is unacceptable.

## 8. Noise control (the thing that kills hook systems)

Nudges that fire constantly become wallpaper exactly like CLAUDE.md did. Guards:
- `once_per` defaults; global cap of 600 chars injected per call.
- Weekly report from `fired.jsonl`: rules that fired > 50×/week with no measurable effect → demote to `once_per: session` or delete; rules that never fired in a month → check the matcher or move to judgment.
- A rule's `say` must tell the agent what to do, not restate the principle ("Move it to ~/.Trash/" not "Safety first").
- Blocks only where a wrong action is costly or irreversible. A deny an agent learns to route around (e.g. `rm` → `find -delete`) is worse than a nudge; the C evidence should tell us where that happens.

## 9. Testing

- `rules/tests/cases.yaml`: per rule, ≥ 1 should-fire and ≥ 1 should-not-fire input (tool_input JSON or a reply text). `build_rules.py` refuses to compile if any rule lacks cases or a case fails.
- Replay test: run the dispatcher over the last week's real transcripts (C already reads them) in dry-run, report firing counts per rule. Shows noise *before* turning a rule on.
- Latency test in the same suite (p95 < 80 ms over 200 synthetic calls).
- Each rule ships with `mode: shadow` first: it logs to `fired.jsonl` but injects nothing. Flip to `live` after a day of sane counts.

## 10. Rollout, in small steps

1. **Skeleton**: dispatcher + compiled registry + state + log + tests; port nothing; one trivial shadow rule. (half a day)
2. **Port the 4 existing guards** behind the dispatcher; settings.json shrinks to one line per event. Old scripts stay as `test:` functions.
3. **Blocks** from B's audit (expect ~10), shadow 1 day, then live.
4. **Stop checks** (Details line, uncommitted/unpushed, Actions format), shadow, then live with `max_blocks: 1`.
5. **Nudges** in batches of ~10 by area (UI, git, coordinator routing, Mac input), shadow first each time.
6. **Shrink CLAUDE.md**: once a rule is live as a hook, its full text leaves the compiled CLAUDE.md (stays in `.rules/` docs for humans). Target: compiled CLAUDE.md under 120 lines, judgment rules only. This is the real win; do it rule by rule, never in one sweep.
7. **Prompt-type Stop judges** on the coordinator only, after C confirms which judgment failures recur.

Each step is independently revertible (one settings line, or `mode: off` on a rule).

## 11. Sync to Tyler

- Registry entries carry `who:`. `export_setup.py` already exports sanitized rules to slub-hq `setup/matt/`; extend it to export `who: [matt, tyler]` rules + the dispatcher into `setup/hooks/` (Slub-shared, model-neutral data in YAML, code in Python stdlib only).
- `setup/core.md` Slub rules become registry entries too (`who: [all]`), so "check NOW.md before building" can be a real UserPromptSubmit nudge on "let's build / new app", not a line Tyler's agent forgets.
- INSTALL.md step 3 gains "add the dispatcher hook lines"; paths via env (`AIOS_HOME`, `AIOS_REGISTRY`), Mac-only rules (`claude-control`, do.test, pages) tagged `who: [matt]` so they never reach him.
- Tyler's own rules go in `setup/tyler/registry/`; the dispatcher loads core + own. Same Yes/No/Later flow in `CHANGES.md` for new shared rules.

## 12. Matt's idea: a third layer of watcher agents that inject hooks

Honest take: **good instinct, wrong shape as an always-on layer; right shape as an offline tuner.**

- As a live layer (agents watching threads and injecting corrections mid-turn) it is expensive (a model call per watched turn across 15+ threads), slow (it reacts after the mistake, while a PreToolUse hook prevents it), racy (two agents writing into one thread), and itself a set of text rules that can be forgotten. It recreates the problem one level up.
- What it does well is what deterministic hooks can't: notice *new* failure patterns. So make it a **daily (or on-demand) rule tuner**: an agent reads `fired.jsonl` + recent transcripts, finds (a) mistakes no rule caught, (b) rules that fire uselessly, and proposes registry diffs (new rule with cases, matcher fix, demotion) as a PR or an `IDEAS.md` entry for Matt's 👍. The deterministic dispatcher stays the enforcer; the agent only writes code that gets tested.
- Live judgment is covered narrowly by §7's prompt-type Stop hooks on the coordinator, which is the cheap version of a watcher for the one place it pays.

## 13. Risks

- **Hook bugs block everything**: fail-open + tests + shadow mode; a kill switch env `AIOS_RULES=off`.
- **Over-blocking teaches workarounds**: keep `block` small; watch for agents rephrasing commands around denials (C).
- **Stop loops**: `stop_hook_active` + `max_blocks: 1`, enforced in the dispatcher, not per rule.
- **Role misdetection**: default to worker (the least restrictive set of coordinator-only rules).
- **Two sources of truth during migration**: registry generates `.rules/` text, never hand-edit both; lint flags a rule present in both live hook and CLAUDE.md after step 6.
