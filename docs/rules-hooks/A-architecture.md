# Rules → hooks: architecture (angle A, second pass)

Design only, 2026-10-29. No rule, hook or setting was changed. Siblings: [B-audit.md](B-audit.md) (which rules deserve to live) and [C-evidence.md](C-evidence.md) (which rules break, and when). This file answers *how*: the registry, the triggers, the runtime, the rollout, and the sync to Tyler. Where B or C already decided something, this builds on it instead of repeating it.

## 0. In short

- **Five delivery channels, cheapest first:** native `permissions.deny` → path-scoped rule files (`~/.claude/rules/*.md` with `paths:`) → one command-hook dispatcher → a few gated model-judge hooks → a small always-loaded core. Every rule says which channel enforces it.
- **One rule = one Markdown file with frontmatter** (trigger, kind, roles, who, one-line `say`, tests). The body is the human text. The compiler generates everything else: the slim CLAUDE.md, the path packs, the dispatcher's index and Tyler's export. It's plain Markdown, so it fits Slub core rule 7.
- **The runtime knows who is reading.** It knows the session's role (central coordinator, project coordinator, worker or subagent) and who sent the prompt (Matt, a coordinator relay, a peer, a schedule). Reply-style checks fire only when Matt is the reader, which removes most of the noise C measured.
- **The end of the turn is where most pain is caught** (C: #1, #3, #4, #5). A Stop dispatcher runs deterministic checks on `last_assistant_message` plus the state of the repos this session touched. It nudges once through `additionalContext`, never loops, and only judges when the reader is Matt.
- **Matt's watcher idea is right as a tuner, wrong as a live layer.** A live watcher is costly and reacts after the fact. The workable form is an async model judge on the coordinator's Stop (wakes it only on a violation), plus the self-audit-and-learn loop (§13). The loop captures corrections and rule breaks every turn for free, reviews them in batches, and sends Matt at most 3 tested rule changes a week to approve. Hermes's version wrote directly with no approval, and its cleanup bot looped unnoticed for 25 days.

---

## 1. What exists today (re-read, not remembered)

**Always-loaded text.** The compiled `ai-os/CLAUDE.md` is 299 lines and about 12,200 words. `~/.claude/CLAUDE.md` adds 114 lines and about 3,800 words, mostly restating the first. Anthropic's own guidance is "target under 200 lines per CLAUDE.md… longer files reduce adherence" (memory docs). We are at roughly 400 lines before memory, so the size alone predicts the failures C counted.

**Claude Code hooks in `~/.claude/settings.json`:**

| Event | Hooks | Notes |
|---|---|---|
| UserPromptSubmit | `live_call.py`, `qmd_recall.py`, `habit_gate.py hook`, `coordinator_id.py` | Context injectors. `habit_gate` already classifies the prompt's sender (`NOT_MATT = <relay, <cross-session-message, <side-sessions-event, <task-notification, <scheduled …`); reuse that. |
| PreToolUse `Bash` | `input_guard.py`, `bash_timeout_guard.py` | Each about 20–25 ms (measured: 10 runs ≈ 0.21–0.25 s). `input_guard` shells out to `claude-control held` (≤ 6 s) only when a command matches. |
| PreToolUse browser pane | `browser_pane_guard.py` | Deny without `?mute`. |
| PreToolUse `SendMessage\|…send_message` | `thread_size_guard.py` | Deny at 250k; otherwise injects the target's title (an "inject the fact" nudge, the best pattern we have). |
| Stop | `qmd_refresh.sh` | Detached side effect, no feedback. |
| SessionStart | `rex …`, `slub-sync.sh` | `slub-sync` pulls slub-hq and injects Tyler-facing rule offers and the inbox. It's already a small rule-delivery system with Yes/No/Later answers. |
| Project (ai-os) | WorktreeCreate/Remove | Unrelated. |

**Desktop mods** (`context-alert`, `action-bar`, `read-aloud`) are a second hook layer: TypeScript modules registered with `on('prompt.submit' | 'tool.call' | 'turn.complete' | 'ui.render')`. They can hold prompts and draw UI, but they run only in the desktop app, from a cached plugin copy (version bump + update + restart). Use them for *showing* rule activity to Matt, never for enforcing rules: command hooks also run in the CLI, over Remote Control and on Tyler's Mac.

**Prior art Matt already built: the Codex hook engine** (`scripts/codex_hooks/`, Oct 3, still live in `~/.codex/hooks.json`). It has a PreToolUse `tool_guard.py` (rm, `.env`, npm/pnpm/yarn, `git init ~`, `/tmp`), a UserPromptSubmit classifier that slices "policy packs" from `.rules/` by cwd and keywords, `shadow`/`enforce`/`disabled` modes, `rollback.py` and a 30-case test suite. Its audit log has 238 events. Two lessons from it:
1. **Guards drift from rules.** It still blocks `rm -rf ./tmp/test.txt`, but the rm rule was relaxed on Oct 23 to allow tmp/caches. A guard that isn't generated from the same entry as the rule goes stale silently.
2. **Agents route around denials.** It had to add `find … -delete` and `find … -exec rm` patterns (18 hits). Every hard block needs its known workarounds in its test cases.

**Prior art for watchers: `transcript_evaluator.py`** (Hermes, Sep–Oct 12). It checked every 10 turns and wrote 249-byte "no severe rule drift" reports to `.rules/proposals/` that nobody read. What it checked was span-only HTML, a rule B now calls stale. It died unnoticed. That's direct evidence for §11.

---

## 2. What the platform gives us (checked against the docs today)

| Mechanism | What it can do | Use for |
|---|---|---|
| `permissions.deny` in settings | Native hard block by permission-rule pattern, zero code, works in auto mode | Secret reads (`Read(**/.env*)`, `Read(**/*credentials*)`, private keys) |
| `~/.claude/rules/*.md` with `paths:` frontmatter | Loads the file **only when Claude Reads, Edits or Writes a matching file** (or `cat`s it). Reloads on demand after compaction. User-level globs are relative to the session's primary working directory. | Topic packs tied to files: UI/web, Hammerspoon/HUD, Swift/hud-kit, school folders, crossword repo |
| PreToolUse command hook | `permissionDecision` allow/deny/ask/defer + reason; `updatedInput` (rewrite the call); `additionalContext`; matcher regex on tool name; `if` (one permission-rule filter, e.g. `Bash(git push*)`) | Blocks, tool-shaped nudges, injecting a live fact (pace, thread size) |
| PostToolUse / PostToolBatch | `additionalContext`; PostToolBatch injects **once** before the next model call | Recording what this session touched; one combined nudge per batch instead of one per tool call |
| UserPromptSubmit | `additionalContext` (cap 10,000 chars per field) | Nudges keyed on Matt's own words; existing recall |
| SessionStart | command only; `source` = startup/resume/clear/compact/fork; `additionalContext`, `sessionTitle`, `initialUserMessage` | Role digest; re-injection after compaction |
| SubagentStart | `additionalContext` (only added if missing, which keeps the cache intact) | A 5-line leaf digest for subagents |
| Stop | input has `last_assistant_message`, `stop_hook_active`, `background_tasks`; `decision:block` or `additionalContext` (shown as "Stop hook feedback") continues the turn; built-in cap of 8 consecutive continuations | End-of-turn checks |
| `type: "prompt"` / `"agent"` | Model judge returns `{ok, reason, impossible}`; supported on PreToolUse, PostToolUse, UserPromptSubmit, Stop and more; **not** SessionStart; default timeout 30 s / 60 s; runs on every match (it can't be gated by a cheap precheck) | Rare; see §8 |
| `async` / `asyncRewake` | Background command hook; its output arrives next turn; `asyncRewake` exiting 2 **wakes an idle session** | The gated judge: no latency for Matt, cost only when it fires |
| InstructionsLoaded | Observability only (`load_reason` = path_glob_match, compact…) | Measuring which path packs actually load |
| Plugin `hooks/hooks.json` | Same hooks, shipped with `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` | Distributing the dispatcher to Tyler (§11) |
| `onFailure: "block"` | Turns a hook crash or timeout into a block | Only on the two fail-closed rules, never on the dispatcher |

**Consequence: pick the cheapest channel that works.** A rule that a `permissions.deny` line can express needs no Python. A rule that matters only when certain files are touched should be a path pack, not a keyword guess. Only what needs logic goes through the dispatcher. Only what needs judgment *and* is worth money gets a model.

---

## 3. Rule kinds

Each rule has exactly one `kind`, which names how it is enforced. This is B's §7.3 "every rule says how it's enforced", made machine-checkable.

| kind | channel | contract | rough share after B's cuts |
|---|---|---|---|
| `deny` | permissions.deny or PreToolUse | Wrong action is costly or irreversible; the reason says what to do instead | ~12 rules |
| `pack` | path-scoped rule file, or a dispatcher-injected pack | A topic's rules, loaded when the work touches that topic | ~8 packs holding ~40% of today's text |
| `nudge` | PreToolUse/PostToolUse/UserPromptSubmit `additionalContext` | One line at the moment it matters; preferably **a fact, not a rule** ("Pace: 61% of week used at 48% of week, Opus OK", not "check the pace") | ~20 rules |
| `check` | Stop dispatcher | Inspects the reply plus repo state; nudges once | ~8 rules |
| `core` | always-loaded slim CLAUDE.md | Pure judgment, no trigger exists; must fit the ≤ 60-line budget B proposed | ~15 one-liners |
| `signal` | dispatcher, silent | Records evidence (corrections, ignored checks, workarounds) for the learn loop (§13); never injects text | ~6 |

A rule may add a secondary `check` to a primary `nudge` (for example: UI pack loads on edit, Stop checks that a dark-mode check ran). A rule that can't name a kind doesn't get in. That gate is what stops the pile regrowing.

### First assignment (from B §8 + C's ranking, refined)

**deny**
- Secret reads: native `permissions.deny` for Read; dispatcher for `cat|head|grep|less … .env*` in Bash. *Fail closed.*
- `rm`/`rmdir` outside tmp, scratchpad, caches, `node_modules`, stale worktrees, **including `find -delete` and `find -exec rm`** (Codex evidence). The reason text says `mv … ~/.Trash/`.
- Synthetic input without a `claude-control` ticket: existing `input_guard`, extended to `mcp__computer-use__*` and `mcp__claude-in-chrome__computer|form_input` (C #6: 31 unguarded calls). *Fail closed* (today it warns when Hammerspoon is unreachable; the written rule says fail closed; the merge must pick one).
- `hs -c 'hs.reload()'` → `scripts/hs_reload.sh`.
- `npm|npx|pnpm|yarn` → bun (reason includes the bun equivalent).
- `gh repo create` without `--private`; `git init` in `~`.
- `git push` to `main` in `daily-mini-crossword` (check `git -C <cwd> rev-parse --abbrev-ref HEAD` and the push refspec).
- Writes to system `/tmp` (allow `/private/tmp/claude-*`, the scratchpad).
- **AskUserQuestion with any `multiSelect: false`.** One deterministic rule covers both "plain-text questions, menus only for quizzes" and C #7 (59% of quiz questions single-select). Reason: "Ask in plain text; quizzes need multiSelect: true."
- Existing: hang guard, browser-pane guard, thread size at 250k.

**pack** (path-scoped where possible)
- `ui`: `**/*.{css,scss,html,tsx,jsx,vue,svelte}`, `pages/**`. Palette roles only, light and dark, no stock look, no orphans, icons, press feedback, the one merged design gate (B §3).
- `swift-hud`: `**/*.swift`, `hud-kit/**`. HUD slots, Tweaks, light and dark.
- `hammerspoon`: `~/.hammerspoon/**`, `qwerty-midi-hammerspoon/**`. Reload method, HUD slots, `withInput` queue for automations. Outside the cwd, so it's dispatcher-injected (see §5); path globs can't reach it from `~/projects`.
- `school`: course folders from `SCHOOL.md` and Canvas URLs. No ghostwriting, the allowed list, the PHIL 120 ramp. One line also stays in core because of the stakes.
- `coordinator`: `code-coordinator.md`, injected at SessionStart **only** for coordinator roles; workers never load it.
- `cloud-threads`: only when `cwd` is under `/mnt/` or the session has no Mac.
- `music`, `reminders`: dispatcher-injected on UserPromptSubmit keywords from Matt (no files to match).

**nudge**
- `start_session` (coordinators): inject the *current* pace verdict (cached `claude_pace.py`, 10 min), "brief is the task, self-contained", "say nothing after starting".
- `SendMessage`: existing size + title.
- Write/Edit in `.rules/` or the rule registry: "run `build_rules.py`; tell Matt it's global and syncs to Tyler".
- Write in any `memory/` dir with always/never/from-now-on language: "memory only affects this project; global rules go to `.rules/`" (C: the 10-29 04:23 incident).
- New project signals (`git init`, `pages new`, `mkdir ~/projects/<new>`): existing-tools-first, project freeze, slub-hq NOW.md/IDEAS.md check (Slub core 1–2).
- UserPromptSubmit, **sender = Matt only**: to-do/remind/call language → Apple Reminders now; "from now on / always / never" → save as global rule; idea language → IDEAS.md + honest take; "quiz me / study" → quiz skill; earlier-assistant-thread language → `threads.py`; "redesign / new UI" → design gate.

**check** (Stop, §7)
1. Permission-asking with no real fork, plus dirty or unpushed repos this session touched (C #1).
2. Word budget, only when Matt is the reader (C #3).
3. `Actions:` line lint: ≥ 2-word verb+object labels, no bare numbers, no Matt-only steps (C #4).
4. Details line, pending the B-vs-C decision on keeping the ritual (C #5).
5. Unlinked `local_…` ids and bare absolute paths in a reply to Matt.
6. Source edited since the last test or run command.
7. Voice task (prompt began "🎙️ Voice task") ended without a `voice_reply.py` call. Fully deterministic, so it's a free win.
8. Hammerspoon files edited this turn without a reload.

**core** (always loaded, ≤ 60 lines): reply shape (line 1 = answer, clarity over brevity, blank lines), obvious wants → just do it, make it live, honest takes on ideas, restate only truly complex logic, systems over one-offs, look for existing tools first, never act as someone else, one school line, the Slub core rules, and B's conflict order (safety > Matt's latest words > freeze > rest).

---

## 4. Registry format: one Markdown file per rule

Slub core rule 7 says "plain Markdown, no tool-specific formats", and Claude Code's own path rules are Markdown with frontmatter. So every rule is a `.md` file. Frontmatter is the machine part; the body is the human text, kept for autopsies, Tyler and generated docs.

```markdown
---
id: rm-outside-scratch
kind: deny
pack: core-safety
roles: [all]                     # central | project-coordinator | worker | subagent | all
who: [slub]                      # slub = shared with Tyler; matt = Matt's Mac only
on:
  event: PreToolUse
  tool: Bash
  command: '(^|[;&|(]\s*)(sudo\s+)?(rm|rmdir)\s|\bfind\b.*\s-(delete|exec\s+rm)\b'
unless:
  command: '\s(\./)?(tmp|\.cache|node_modules)/|/private/tmp/claude-|/\.claude/worktrees/'
say: "Don't delete here: mv <path> ~/.Trash/ (rm is only for tmp/, caches, node_modules, scratch)."
mode: live                       # off | shadow | live
fail: open                       # closed only for input + secrets
since: 2026-10-23
review: 2026-12-01               # B §7.4: patches expire unless renewed
tests:
  fire: ["rm -rf src", "find . -name '*.log' -delete", "cd x && rm a"]
  pass: ["rm -rf tmp/out", "mv a ~/.Trash/", "git rm --cached x"]
---
Never `rm` outside scratch… (full rule text, the why, Matt's quote, history)
```

```markdown
---
id: pace-on-start-session
kind: nudge
roles: [central, project-coordinator]
who: [slub]
on: { event: PreToolUse, tool: mcp__ccd_session__start_session }
fact: pace                        # named provider in facts.py; output is cached
say: "{pace}. Opus unless over pace; Sonnet only for really small tasks."
once: never                       # fires every time: the fact changes
---
```

```markdown
---
id: thread-size-limit
kind: deny
who: [slub]
params: { limit_k: 250 }          # Tyler can override: setup/tyler/overrides.md
on: { event: PreToolUse, tool: 'SendMessage|mcp__ccd_session_mgmt__send_message' }
test_fn: thread_size              # named Python check: logic lives in code, not regex
---
```

Field notes:
- `say` ≤ 200 characters (the compiler fails above that) and must tell the agent what to do. Every injected line is prefixed `[rule:<id>]`, so a transcript reader (Matt, Tyler, the learn loop) can trace any behaviour to its file.
- `once`: `turn` (the default for nudges), `session`, `file` (per edited file), or `never`. This is the main noise lever.
- `test_fn` names a function in `rules/checks.py`. Regex is for triggers; anything with logic is real code with unit tests (the four existing guards become `test_fn`s unchanged).
- `params` are the per-person knobs. Tyler's call worry ("I set my handoffs to 50% … I'd think it's broken") is answered by overriding a number, not forking a rule.
- `fact` names a provider (pace, thread size, git state, NOW.md lines) whose output goes into the text. Injecting facts beats injecting principles. The thread-size guard proved it.

**Layout**
- `slub-hq/setup/rules/<pack>/<id>.md`: shared rules (`who: [slub]`). Both edit, both agree (core.md's rule).
- `ai-os/rules/<pack>/<id>.md`: Matt-only rules. This replaces `.rules/*.md` gradually; during migration, `.rules/` text and rule files coexist, and the compiler warns when a rule exists in both.
- `slub-hq/setup/<who>/overrides.md`: per-person `mode` and `params` overrides.

**The compiler** (`build_rules.py` grows a step) emits:
1. `~/.claude/rules-index.json`: what the dispatcher reads (no YAML or Markdown parsing at runtime).
2. `~/.claude/rules/<pack>.md`: path packs with `paths:` frontmatter (generated, read-only).
3. Slim `CLAUDE.md`: the `core` rules only, with a header line saying "other rules arrive just in time, tagged [rule:id]; follow them".
4. The settings fragment (one entry per event; see §5).
5. Tyler's export: `who: [slub]` only, run through `export_setup.py`'s sanitizer plus a lint for Matt-only paths (B §7.8).
6. It **refuses to compile** when a rule lacks tests, a test fails, `say` is over budget, or `kind` is missing.

---

## 5. Runtime: one dispatcher, plus the guards that must stay separate

`settings.json` (or the plugin's `hooks.json`, §11) gets one entry per event:

```json
"PreToolUse":  [{"matcher": "<union of tools any rule names>", "hooks": [{"type": "command", "command": "python3 -I -S ~/…/rulehook.py PreToolUse", "timeout": 10}]}],
"PostToolUse": [{"matcher": "Edit|Write|Bash|mcp__ccd_session__start_session", "hooks": [{"…": "rulehook.py PostToolUse", "async": false}]}],
"PostToolBatch": [{"hooks": [{"…": "rulehook.py PostToolBatch"}]}],
"UserPromptSubmit": [{"hooks": [{"…": "rulehook.py UserPromptSubmit"}]}],
"SessionStart": [{"hooks": [{"…": "rulehook.py SessionStart"}]}],
"SubagentStart": [{"hooks": [{"…": "rulehook.py SubagentStart"}]}],
"Stop": [{"hooks": [{"…": "rulehook.py Stop"}]}]
```

The dispatcher's steps:
1. Read stdin; check the kill switch (`AIOS_RULES=off` env or a `~/.claude/rules.off` file → exit 0).
2. Load `rules-index.json`; resolve role and sender (§6) from the per-session state file `~/.claude/rule-state/<session_id>.json`.
3. Filter rules by event, tool, role and `who`; evaluate triggers and `test_fn`s; apply `once`.
4. Merge the outputs. Any `deny` wins (reasons joined, each tagged). Otherwise the nudges are joined into one `additionalContext`, **≤ 600 characters per call**, lowest priority dropped first. PostToolUse nudges are held in state and emitted once by PostToolBatch, so a 10-call batch gets one reminder, not ten.
5. Append to `~/.claude/rule-state/fired.jsonl`: `{ts, session, role, sender, rule, decision, mode}`. In `shadow` mode a rule logs but emits nothing.
6. Any exception → exit 0 with no output, plus an `error` line in the log. **Fail open.**

**Fail-closed exceptions.** The input guard and Bash secret reads stay as **separate handlers** with `onFailure: "block"`, so a dispatcher crash can't disable them and a crash in them can't take the dispatcher down. Native `permissions.deny` covers secret `Read`s with no code at all.

**Latency.** Python cold start is about 11 ms with `-I -S` and about 18 ms plain (measured). Merging today's two Bash guards into one process makes Bash calls *faster* than now. Budget: p95 ≤ 30 ms for pure-regex paths (a test enforces it), and external calls (`claude-control held`, `thread_size.py`, `git status`) only after a cheap trigger has matched, each under its own timeout. Read, Grep and Glob are never in the matcher, so they never spawn Python.

**Prompt cache.** SessionStart output becomes part of the cached prefix, so it must be stable per role (no timestamps, no live facts). Live facts go in mid-conversation injections, which append and don't invalidate the cache.

---

## 6. Who is running, and who is reading

**Session role.** Hook input has `session_id` (the CLI UUID) and `cwd`, but no role. Resolution, cached in the state file:
1. Desktop metadata: `~/Library/Application Support/Claude/claude-code-sessions/*/*/local_*.json` contains `cliSessionId` → `local_` id → `coordinator/threads.json` entry → `role` (`central` / `project-coordinator`; anything else is a worker). One glob per session, about 50 ms, done once at SessionStart.
2. The title from the same metadata (`… · Coordinator`), if the registry hasn't caught up yet.
3. `AIOS_ROLE` env (the CLI, Tyler without the desktop app, scripts).
4. Default `worker`.

Subagents are identified by `agent_id`/`agent_type` in the input and get role `subagent`. SubagentStart injects a 5-line leaf digest: safety denies still apply, report to the parent, no Matt-facing reply rules.

**Sender (who wrote this turn's prompt).** UserPromptSubmit classifies the prompt with habit_gate's list: `matt` (plain text, a `<wake>` from Matt's thread, a voice task), `relay` (`<relay`, `<coordinator-relay`), `peer` (`<cross-session-message`), `event` (`<side-sessions-event`, `<task-notification`, `<ci-monitor-event`), or `schedule`. It stores the sender under `prompt_id` in the state file.

**Reader (who reads the final reply).** This is what fixes C's main caveat. Matt reads a turn's reply when the sender was `matt`, or when the session is a coordinator (the central one or a project coordinator) and the sender wasn't a peer. A worker answering a coordinator's relay is writing to an agent, not to Matt, and its report gets relayed and trimmed. Reply-style checks (word budget, Actions lint, Details, links) run **only when the reader is Matt**. Repo checks (dirty or unpushed, untested edits) run for every role.

**What each tier gets:**

| | Central Coordinator | Project coordinator | Worker | Subagent |
|---|---|---|---|---|
| SessionStart | core + coordinator pack + routing facts (registry path, own id) | core + coordinator pack + project-coordinator delta + project name | core only | — (SubagentStart leaf digest) |
| Denies | all | all | all | all |
| Nudges | start_session, SendMessage, rules-save, memory-save | same | new-project, rules-save, memory-save, packs | none |
| Stop checks | reply checks + model judge (§8) | reply checks | repo checks always; reply checks when the reader is Matt | none |

This also enforces two coordinator rules that are now text-only. "No analysis in the coordinator" becomes a coordinator-only nudge when a coordinator does a long Read/Grep run (e.g. more than 8 non-registry reads in a turn → "route this to a thread"). "Project coordinators forward global rules to the central one" becomes a memory-save nudge that fires only in project-coordinator sessions.

---

## 7. The Stop dispatcher in detail

Input: `last_assistant_message` (from the docs: "use this field rather than reading `transcript_path`"), `stop_hook_active`, and the state file (touched repos, sender, checks already fired this turn).

- **Touched repos.** PostToolUse records the git root of every Edit/Write path and of every Bash `cwd` that ran a git or build command. At Stop, only those roots get `git status --porcelain` and `git rev-list @{u}..HEAD --count` (about 10–30 ms each).
- **Check #1, unneeded OK** (C's top cost). It fires when the reply matches permission phrases (`want me to|should I|shall I|reply 👍|let me know if|if you'd like`) **and** a touched repo is dirty or ahead of upstream. The nudge says "commit and push now (auto_commit.py), or name the real fork in one line". A permission phrase with a clean tree is left to the coordinator's model judge (§8), because only a model can tell a real fork from a lazy one.
- **Delivery.** It uses `hookSpecificOutput.additionalContext`, not `decision: block`: it shows as "Stop hook feedback", not an error, and it still continues the turn under the same loop protections. If `stop_hook_active` is true, nothing fires. Each check fires at most once per turn, recorded in state, which sits under the platform's 8-continuation cap.
- **Ordering.** All failing checks are folded into one feedback message (≤ 600 chars), so a bad reply costs one extra model turn, not five.
- **Escape hatch.** A reply containing `<!-- rules: skip <id> because … -->` (the action-bar mod would need to hide it from display) suppresses one check and logs the reason. Legitimate exceptions then become data for the learn loop instead of fights.

---

## 8. Model judges (prompt hooks), and where they're worth it

`type: "prompt"` hooks run on every matching event with no cheap precheck and take up to 30 s, which is too slow and too costly for worker Stops (C: about 215 turn-ends a day). So:

- **Use `async` + `asyncRewake`, not inline prompt hooks.** A command hook on the coordinator's Stop runs deterministic gates first (the reply has a question or permission phrase, or a long Read/Grep run happened). Only then does it start a background judge (`claude -p --model haiku` with a 1–2k-token prompt: the reply, the triggering prompt, the rule lines). If the judge says "violation", the hook exits 2 and the session wakes with the reason. Matt waits for nothing, and a clean turn costs one regex pass.
- **Judges that pay for themselves** (all coordinator-only, all C-evidenced): asked for an OK it didn't need; did analysis instead of routing; relayed a project coordinator's update (Matt: "the project coordinator should be the one keeping me up to date"); told Matt to do something an agent could do (rule 1n).
- **Cost.** About 20 gated judgements a day × about 2k Haiku tokens ≈ nothing next to one Opus turn. The real cost is a false wake, so each judge starts in shadow mode (logs its verdicts; nothing wakes) until a week of verdicts reads right.
- **The model must be verified, not guessed.** Use the `haiku` alias, never a hard-coded ID (Matt's model-verification rule).

---

## 9. Noise, cost and measurement

Hook systems die the way CLAUDE.md is dying: too many lines, all ignored. The guards:
- `once` defaults; ≤ 600 chars per call; ≤ about 1,500 chars of nudges per turn (the dispatcher keeps a per-turn counter and drops by priority).
- Facts over principles; a `say` that restates a principle fails lint ("must contain a verb telling the agent what to do").
- **Reader-aware checks** (§6) remove the agent-to-agent replies from reply checks. That's most of C's 604 "long replies".
- **Tokens.** About 50 tokens per nudge, a few per turn. Meanwhile the slim core replaces about 16,000 words (about 21k tokens) of always-loaded text with about 60 lines (about 1.2k tokens). Most of the gain is in the agent's attention rather than the token bill, but the bill drops too.
- **Measurement.** `fired.jsonl` + `InstructionsLoaded` log → `rulehook.py report` (per rule: fires/week, by role; how often the next action complied, e.g. a commit within 2 tool calls after the nudge; skips with reasons). Rules that fire more than 50×/week with low compliance get rewritten or demoted. Rules that never fire in 30 days get a look at their trigger, then expire at `review`.

---

## 10. Testing and rollout

**Tests** (in the build; nothing compiles without them):
- Inline `tests.fire` / `tests.pass` per rule, including known workarounds for every deny.
- A `test_fn` unit test for each named check; the four existing guards keep their behaviour, proven by replaying their past inputs.
- **Replay.** Run the dispatcher dry over the local transcripts C used (about 520 from the last 10 days): for every PreToolUse/Stop moment, record what would have fired. That gives firing rates and false positives *before* anything goes live. C's scripts already parse these transcripts.
- A latency test (p95 over 500 synthetic calls).
- A Stop-check golden set: 30 real final replies from C's sample, hand-labelled.

**Rollout.** Each step can be undone on its own; nothing is deleted until its replacement is live and measured.

| Step | What | Done when | Undo |
|---|---|---|---|
| 0 | Merge thread decides B's cuts. **Delete dead rules before hooking anything** (no hooks for stale rules; the Codex rm guard shows why) | B's delete list removed from `.rules/` | git revert |
| 1 | Registry format, compiler step, `rulehook.py` skeleton, state, log, kill switch, test runner. Port the 4 existing guards as `test_fn`s; settings points at the dispatcher | Replay shows identical decisions to today's guards | Restore the old 4 settings lines |
| 2 | Denies: native `permissions.deny` for secrets; port Codex `tool_guard` logic **from the rule files** (fixing its stale rm rule), shadow 2 days, then live | Shadow log is clean of false positives | `mode: shadow` per rule |
| 3 | Role and sender resolution; SessionStart digests; coordinator pack leaves workers' context | Coordinator and worker sessions see different digests | Env `AIOS_RULES_ROLES=off` |
| 4 | Path packs (`ui`, `swift-hud`, `school`) generated to `~/.claude/rules/`; dispatcher-injected `hammerspoon` pack | InstructionsLoaded log shows them loading on matching edits | Delete the generated pack files |
| 5 | Stop checks 1–8, shadow 3 days on replay + live, then live | Golden set ≥ 90% right, fewer than 1 false nudge/day | `mode: shadow` |
| 6 | UserPromptSubmit nudges (sender = Matt only) | Under 1 nudge per 5 of Matt's prompts | `mode: off` |
| 7 | Coordinator async judges, shadow one week, then live | Matt agrees with 9 of 10 sampled verdicts | `mode: shadow` |
| 8 | **Shrink CLAUDE.md**: a rule's text leaves the compiled core once its hook has been live a week; target ≤ 60 lines core + generated packs | Compiled core ≤ 60 lines; C's counts re-run and compared | Rebuild with `--full` |
| 9 | **Learn loop** (§13): signal capture ships with step 5; triage after 2 weeks of signals; first weekly proposal run after that | Matt keeps or kills it after the first report | `mode: off` on the signal rules; unload the launchd job |

Step 8 is the payoff and the riskiest step, so it goes rule by rule, never in one sweep (Matt's "sustainable marginal change" rule).

---

## 11. Sync to Tyler

**Distribution: a `slub-rules` plugin in the existing `slub-mods` marketplace** (`slub-hq/setup/matt/mods`, already used for the desktop mods; INSTALL.md step 8 already teaches it). `hooks/hooks.json` points at `${CLAUDE_PLUGIN_ROOT}/rulehook.py`. Why a plugin rather than settings edits:
- One `claude plugin install` instead of an agent hand-merging JSON into Tyler's settings (INSTALL step 3 today).
- **Code and data update differently.** Dispatcher code changes rarely and ships by plugin version bump. Rule *files* are read live from `~/projects/slub-hq/setup/rules/`, which `slub-sync.sh` pulls at every SessionStart, so a shared rule edit reaches Tyler on his next session without a plugin update. (Matt's memory note: plugin edits need a version bump, update and restart; this design keeps that to code changes.)
- Matt-only rules load from `ai-os/rules/` only if that folder exists, so they never reach Tyler.

**Tyler's concern from the 10-29 call** ("if I don't know explicitly what each thing is… I'd think it's broken") is handled four ways:
1. New shared rules arrive in **`shadow` on Tyler's machine** until he answers Yes in the existing CHANGES.md Yes/No/Later flow; `slub-answers.json` becomes the source of his per-rule modes.
2. Every injected line is tagged `[rule:id]`, and `rulehook.py why <id>` prints the rule file. Behaviour changes are traceable from the transcript.
3. `params` overrides in `setup/tyler/overrides.md` (e.g. his own handoff threshold) instead of forking.
4. A `rulehook.py conflicts` report lists Tyler's own CLAUDE.md lines that mention the same triggers as shared rules (same tool, same path, same keywords), for his agent to discuss with him. It's a crude lexical match, but it turns "rules I don't remember" into a short list.

**Codex and Gemini** read the same rule files: the Codex engine's `tool_guard`/`classifier` become a second adapter over `rules-index.json`, so the guard-vs-rule drift found in §1 can't recur.

---

## 12. Matt's idea: a third layer of watcher agents that inject hooks

Honest take: **the instinct is right (rules should be maintained by evidence, not memory), but an always-on watcher layer is the wrong shape.** Matt has already built one. `transcript_evaluator.py` ran every 10 turns, wrote reports nobody read, checked a rule that had gone stale, and died unnoticed in October.

Why a live watcher layer fails:
- **Timing.** It sees a mistake after the tool call. A PreToolUse deny prevents it; a Stop check catches it before Matt reads the reply. A watcher can only add a correction after the fact.
- **Cost.** A model call per watched turn across 15+ live threads, mostly saying "fine".
- **Races and authority.** Injecting into another thread mid-turn collides with the thread's own work and with the coordinator's messages. A watcher's injection is just more text, which is the thing that failed in the first place.
- **Recursion.** The watcher's own rules are text it must remember.

The two forms that do work, and that I recommend:
1. **A narrow live judge**, built into the hook system: §8's async judge on the coordinator's Stop, which wakes it only on a violation. That is a watcher scoped to the one place where judgment failures are costly and volume is low.
2. **The self-audit-and-learn loop** (§13): every turn records evidence cheaply, and a reviewer works in batches, writing tested rule-file diffs that Matt approves. This is "watchers that write hooks", done safely: the agent proposes code, the compiler and tests gate it, and Matt approves it. It also matches Tyler's suggestion on the call to audit both their Claude usage every month.

---

## 13. Self-audit-and-learn loop (Hermes-inspired)

Matt's ask: at Stop or PreCompact, an agent reviews the turn for rule breaks and corrections from Matt, then proposes rule or hook changes. Below: how Hermes did it, what went wrong there, and the design.

### 13.1 How Hermes did it (read from `~/.hermes/hermes-agent/agent/` and `~/.hermes/skills/`, read-only)

- **Background review fork** (`background_review.py`, `turn_finalizer.py`). Every 10 user turns (`memory.nudge_interval: 10`) and every 15 tool iterations (`skills.creation_nudge_interval: 15`), Hermes forked the agent in a background thread. The fork replayed the conversation on the same model (cheap prompt-cache reads) with a tool whitelist of only the memory and skill tools, and **wrote straight into the memory and skill stores. There was no approval step.**
- **The review prompt pushed for writing**: "Be ACTIVE — most sessions produce at least one skill update… A pass that does nothing is a missed learning opportunity." Corrections ("stop doing X", "too verbose") were "FIRST-CLASS" signals.
- **Good ideas worth stealing.** A "do NOT capture" list: environment failures, negative claims about tools ("X is broken" hardens into refusals for months), transient errors, one-off task narratives. A preference order: patch the skill that was in play before making a new one. And a **curator** (`curator.py`) that runs when the agent is idle, never deletes (only archives), honours pins, and keeps a ledger with before/after hashes.
- **What it produced for Matt.** 18 agent-created skills since July; 13 are now marked stale, most used 1–13 times. The curator's ledger shows **6,795 archive actions between Sep 26 and Oct 21**: the same 13 skills archived about every hour (`agy-20260926193621`, `agy-20260926203632`, …), apparently because another sync kept putting them back. Two automations fought over the same files for 25 days and nobody noticed.

**Lessons:** a learning loop that writes directly drifts. One told to "be active" produces volume, not value. And a loop nobody watches can run broken for weeks. Matt's own `transcript_evaluator.py` (§1) failed the same way, with unread reports.

### 13.2 Design: capture every turn, review in batches, approve by hand

**Stage 0: capture (deterministic, every turn, about free).** This runs in the existing dispatcher as a sixth rule kind, `signal`: it records evidence and never speaks. It writes to `~/.claude/rule-state/signals.jsonl`, which stays on this Mac, is never exported and is pruned after 60 days.

| Signal | Detected by | Moment |
|---|---|---|
| Correction from Matt | UserPromptSubmit, sender = Matt: C's correction patterns (again, why did you, I told you, never, always, stop, should have, you didn't, from now on), ❌/❓, a very short negative reply | Prompt submit |
| Explicit rule statement ("from now on…", "always…") | Same | Prompt submit |
| Unsaved explicit rule | Stop: Matt stated a rule this turn, but nothing was written to `.rules/` or the registry | Stop (the same check also nudges the session to save it **now**, which is the fast lane and covers C's 10-29 04:23 incident) |
| Check ignored | Stop: a check nudged last continuation and the condition still holds (still dirty, still over budget) | Stop |
| Deny workaround | PreToolUse: a deny followed within 3 calls by an allowed command with the same intent (e.g. `rm` denied, then `find -delete`) | PreToolUse |
| Skip with reason | Stop: a `rules: skip` comment | Stop |

Each record holds `{ts, session (local_ id), role, kind, rules fired in the previous turn, Matt's text ≤ 300 chars, previous reply excerpt ≤ 500 chars, transcript_path, prompt_id}`. **PreCompact and SessionEnd only flush** a session's pending records (SessionEnd has a 1.5 s budget, so no review can run there). The transcript stays on disk, so nothing is lost by not reviewing at compaction time.

**Why not review at every Stop or PreCompact, as asked:** one turn can't tell a pattern from an anecdote. A model call per turn across 15+ threads costs real usage to say "fine" about 95% of the time, and it would add latency or wake-ups to Matt's threads. Capture at Stop, review in batches.

**Stage 1: triage (daily, Haiku, about 40k tokens a day).** A nightly job (launchd, before the 04:30 restart; skipped when `claude_pace.py` says the week is over pace, with signals kept for later) reads new signals. For each one it pulls only a small window from the transcript (Matt's message, the previous reply and its tool calls). It classifies the signal as **agent-behaviour correction / product feedback about an app / task content / noise**. It names the rule that covers it (or none) and fingerprints it (normalised topic + rule id). Only agent-behaviour corrections go on; product feedback is out of scope (the project's IDEAS/Linear, not rules). Scale: C found 129 regex hits in 10 days, about 60 real, so about 13 a day × about 3k tokens.

**Stage 2: proposals (weekly, Sonnet, one medium worker session).** It groups the week's triaged signals by fingerprint and joins them with `fired.jsonl` stats and the replay report. It proposes only for groups that clear the evidence bar. It works in this order, borrowing Hermes's "patch what was in play first":

1. **Adherence fix** (a rule exists but was broken): move it up a channel (core text → nudge → check → deny) or fix its trigger. **This should be most proposals.** C's evidence says the problem is adherence, not missing rules.
2. **Trigger fix** for a rule that fired wrongly (false positive) or failed to fire (false negative), with the real transcript moment as a new test case.
3. **Merge, tighten or retire** a rule contradicted by Matt's correction, past `review` with zero fires, or noisy with low compliance.
4. **New rule**, only with **≥ 2 independent signals** (different sessions on different days), or one explicit statement from Matt that never got saved.

Each proposal is a **rule-file diff with tests built from the real moments**, evidence links (session links + one quoted line each), the replay's estimated firing rate, and the line count it adds to or removes from the always-loaded core. It must pass the compiler. New rules always start at `mode: shadow`. Hermes's "do NOT capture" list applies, plus: nothing private in shared rules (export sanitizer), and nothing Matt said as a joke.

### 13.3 How proposals reach Matt (nothing changes without a 👍)

- Stage 2 commits proposals to a branch (`learn/<date>`) in ai-os, or in slub-hq for `who: [slub]` rules, plus one summary file `docs/rules-hooks/proposals/<date>.md`. **No live rule changes.**
- It posts one line to the Coordinator through the existing coordinator inbox (`scripts/coordinator_inbox.py`, which the context-alert mod already polls every 30 s for voice tasks; reusing it for this needs a small test). On Matt's next turn, the Coordinator shows **at most 3 proposals**, one plain sentence each (what changes, how many times it happened, what it would have caught), with an Actions line, e.g. `Apply rule proposal 1 → Yes, apply proposal 1 · Apply all three → … · Skip this week → …`.
- **Apply** merges that rule file, runs `build_rules.py`, and puts the rule in shadow for 3 days. It goes live on its own only if shadow firing matches the estimate (within 2×); otherwise it comes back as a proposal. **Skip** records the fingerprint and suppresses the same proposal for 60 days unless the evidence doubles. **No answer in 14 days** → it expires quietly and is logged.
- **Shared rules** go to slub-hq: proposals touching `who: [slub]` rules also land in `inbox/tyler.md`, and core.md's "change it only when Matt and Tyler both agree" holds. Tyler's machine runs its own loop on his own signals; his signals never leave his Mac.

### 13.4 Keeping it from becoming noise

- **Silence by default.** A week with nothing over the evidence bar sends nothing at all (the opposite of Hermes's "be ACTIVE").
- **Cap of 3 proposals a week**, ranked by evidence count × cost to Matt (C's ranking method).
- **Rule budget.** While the core is over 60 lines, a new-rule proposal must come with a merge or removal of at least the same size (B §7.1).
- **The loop measures itself** in `docs/rules-hooks/learn-report.md`, regenerated weekly: proposals, acceptance rate, rules added vs removed, and the real success metric: **did that correction stop recurring** after its rule went live?
- **Kill date built in.** If acceptance stays under 30% for 4 weeks, or recurrence doesn't drop for accepted proposals within 6 weeks, the loop pauses itself and tells the Coordinator once.
- **Anti-churn guard (the Hermes curator lesson).** The same action on the same rule file more than 3 times in 30 days stops the loop and alerts. Every write goes to an append-only ledger (before/after hashes, like Hermes's curator).

### 13.5 Cost

| Stage | Model | Rough use |
|---|---|---|
| Capture | none | About 1 ms of regex per prompt/Stop inside the dispatcher |
| Triage | Haiku | About 40k tokens/day |
| Proposals | Sonnet | One medium session/week (about 100k input incl. tests and compile), skipped when over pace |
| Matt | — | ≤ 3 one-line proposals a week, one tap each |

For comparison, Hermes replayed the full conversation on the main model every 10 turns in every session.

### 13.6 Honest take

**Worth building, in this narrow form, and later than the hooks themselves.**
- **The strongest part is cheap and deterministic:** catching explicit rules Matt stated that never got saved, and noticing when a rule exists but keeps being broken. Both feed the hook migration directly ("this text rule keeps failing → make it a check"). That's where the value is: C's evidence is mostly broken rules, not missing ones.
- **The riskiest part is the one that sounds best:** "the agent writes its own rules". That is how the pile reached 15,000 words, and Hermes shows the end state: direct writes, a bias to write, stale output and a cleanup bot looping unnoticed for 25 days. Hence: approval-gated, silent by default, capped, budgeted, self-measuring, with a kill date.
- **Timing.** Capture can ship with rollout step 5 (it's a few signal rules in the dispatcher) and should run 2 weeks before any reviewer exists. Then the first Stage 2 run has real data, and Matt can judge from one report whether the loop is worth keeping. If the hooks work, there will be fewer corrections to learn from, which is the point.
- **One risk to watch:** proposals Matt approves without reading because the buttons are easy. Shadow-first promotion and the recurrence metric limit the damage, but the 3-a-week cap matters most.

---

## 14. Risks

- **A dispatcher bug breaks every session.** Mitigations: fail-open, the kill switch, shadow mode, replay tests, and the fail-closed rules living in separate handlers.
- **Over-blocking teaches workarounds** (Codex: `find -delete`). Keep `deny` small; every deny's tests include its workarounds; the learn loop records "denied, then a similar command allowed" as a signal (§13).
- **Stop feedback loops or nags.** Mitigations: one fold-together feedback per turn, `stop_hook_active`, the 8-continuation cap, reader-aware checks and the skip comment.
- **Role misdetection.** Default to worker. Worst case, a coordinator misses its pack for a session; it still has its brief.
- **Desktop-metadata dependency.** The role lookup reads an undocumented app file. If its shape changes, `AIOS_ROLE` and the title fallback still work, and the dispatcher logs `role=unknown`.
- **Path-pack globs are relative to the primary working directory.** Coordinators at `~/projects` cover projects, but files outside (`~/.hammerspoon`) need dispatcher injection. Untested: whether absolute globs work in user-level rules.
- **Plugin command hooks in the desktop app.** The current mods are TypeScript modules, not `hooks.json` command hooks. Before relying on the plugin (§11), test that a plugin command hook fires in a desktop Code-tab session and over Remote Control; if not, fall back to a settings merge.
- **Two sources of truth during migration.** The compiler warns on a rule present in both `.rules/` text and a rule file; step 8 removes the text.

## 15. Decisions for the merge thread

1. **Details ritual:** B says replace it with an automatic end-of-session file; C says enforce it or drop it (69% missed). Pick one before Stop check #4 exists.
2. **Input guard when Hammerspoon is unreachable:** fail closed (the written rule) or warn (today's code).
3. **Distribution:** a plugin (recommended) or settings merge; it depends on the plugin-hook test in §14.
4. **Registry home:** shared rules in slub-hq `setup/rules/` and Matt-only rules in `ai-os/rules/` (recommended), or everything in ai-os, exported.
5. **Whether the Codex adapter is in scope now** or after the Claude side is stable (recommended: after).
6. **Learn loop approval surface:** Coordinator inbox + Action bar (recommended), or a weekly Linear issue.

---

## 16. What changed from the low-effort pass

- **Re-read the sources and verified the platform against today's hooks docs** instead of memory. That added native `permissions.deny`, path-scoped `~/.claude/rules/` packs, PostToolBatch, SubagentStart, `asyncRewake`, `last_assistant_message`, the 8-continuation cap, prompt-hook limits (no SessionStart, no cheap gating) and `onFailure`.
- **Found Matt's existing prior art and built on it:** the Codex hook engine (shadow/enforce modes, tool_guard, policy packs, audit log) and the dead `transcript_evaluator` watcher. Both give concrete lessons: guards drift from rules, agents route around denials, watcher reports go unread.
- **Registry is now one Markdown file per rule** (Slub core rule 7, the same format as Claude Code's path rules) instead of YAML lists, with `params` for per-person overrides, `fact` providers and inline tests.
- **Added sender and reader awareness**, which C's caveat demanded: reply checks only when Matt reads the reply. The first pass had role scoping only.
- **Replaced inline prompt-hook judges with gated async `asyncRewake` judges** (no added latency; cost only on a likely violation).
- **Grounded latency in measurements** (11–20 ms per Python hook; merging guards makes Bash faster). The first pass guessed 40–60 ms.
- **Mapped C's top failures and B's keep-list to concrete rules**, with a first assignment of every rule to a kind and trigger. Added the AskUserQuestion deny, the voice-task check, the memory-save nudge and the coordinator-analysis nudge.
- **Tyler sync is now a plugin in the existing `slub-mods` marketplace**, with rule data read live from slub-hq, new rules in shadow until he says Yes, `[rule:id]` tags and a conflicts report. This answers his worry from the 10-29 call.
- **The watcher verdict is now evidence-based.**
- **Added the self-audit-and-learn loop (§13) at Matt's request**, based on reading Hermes's background review and curator code and outcomes. It has four parts: capture every turn, triage daily on Haiku, propose weekly on Sonnet (≤ 3, tested rule-file diffs), and approve by hand in the Coordinator.
- **Rollout has a step 0 (delete dead rules before hooking anything)**, done/undo criteria per step, and a list of decisions for the merge thread.
