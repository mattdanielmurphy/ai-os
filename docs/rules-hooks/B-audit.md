# B · Honest audit of Matt's rules (2026-10-29, second pass)

Angle B of 3 (A architecture, C failure evidence). This is analysis only: no rule was changed. This pass replaces the low-effort first pass. What changed is listed at the end.

## Summary in five lines

1. **Agents don't see the rule set Matt thinks they see.** The full ~12,200-word ai-os rule set only loads in sessions opened inside ai-os. Everywhere else agents get a hand-kept ~3,800-word summary that has drifted from it. Six topic rule files reach no Claude session at all.
2. **Because of that, the most important rule has a hole.** "Never write graded school work" is missing from every session outside ai-os. No course folder has a rule file.
3. **About a third of the text should go.** Some rules are dead (agent logs, project board, preflight, Antigravity files, Projects-thread routing), some are rituals almost nobody follows (a details file and a Readthrough on every reply), and some contradict each other (rm, the project freeze, undo, handoff limits, whether to wait or act).
4. **The rules that keep failing are the ones that fight Claude Code's own built-in instructions** (always push, pages instead of Artifacts, no menus), plus a muddle of "wait for Matt" and "just do it" rules. Hooks fix the first problem. One clear act-or-wait rule fixes the second.
5. **Missing rules:** a size limit and one home per rule, a scope tag on each rule matching Matt's "circles", a named checkpoint and definition of "done" per project, a limit on active projects, a cost note before fan-outs, and plain-English change notes for Tyler.

---

## 1. What I read and checked

- **Slub:** slub-hq `README.md`, `NOW.md`, `IDEAS.md`, `NAMES.md`, `TASKS.md`, `CLAUDE.md`, `setup/core.md`, `setup/INSTALL.md`, `setup/matt/CHANGES.md`, `setup/tyler/decisions.md` and `setup/hooks/slub-sync.sh`. There is no `VISION.md`. I also read today's call notes (`notes/calls/2026-10-29.md`), which are mostly about this exact topic.
- **Matt:** `docs/ABOUT_MATT.md`, every `.rules/*.md` file, the compiled `ai-os/CLAUDE.md`, `~/.claude/CLAUDE.md`, the ai-os memory index plus several memory files, and `~/.claude/settings.json` hooks.
- **Plumbing:** `scripts/build_rules.py`, `scripts/compile_dynamic_prompt.py`, the Codex hook setup (`~/.codex/hooks.json`, `scripts/codex_hooks/`), and `scripts/hooks/*`.
- **Checks run:** which files reach which sessions, whether each rule's tools and files still exist and when they were last used, and C's failure counts (`C-evidence.md`) wherever I cite how often a rule is broken.

## 2. What the rules are for

The slub-hq files and today's call give the yardstick:

- **Ship.** Drum ID 0.0.1, Glass TV by next weekend, Slub Utils for Tyler. Matt said today: "fighting the urge to keep improving will be a constant on every project."
- **Protect Matt's attention and his school standing.** He is behind in PHIL 120, and AI-written coursework could get him expelled.
- **Many agents on one Mac without collisions,** with no data loss and no leaked secrets.
- **Matt and Tyler working together.** One small shared core, and opt-in adoption of each other's habits. Today's decision: "Matt's own rules never apply to Tyler automatically."
- **Cost:** a weekly quota and Opus by default.

There is also a bigger reason the rules matter. On today's call Matt and Tyler named the core Slub product as a coordinator that gives each task only the rules it needs. **Matt's rule system is the first prototype of what Slub would sell.** Its design is product research, not just housekeeping.

## 3. Structural findings (the big ones)

### 3.1 What each session actually receives

| Session opened in | What loads | Size |
|---|---|---|
| `~/projects/ai-os` (the Coordinator and most side sessions) | compiled `ai-os/CLAUDE.md` (core_safety + git + agent_logs + claude_only), `~/.claude/CLAUDE.md`, `core.md`, ai-os memory index | ~17,000 words, ~103 KB |
| Any other project (glass-tv, slub-hq, school…) | `~/.claude/CLAUDE.md` + `core.md` (+ that project's CLAUDE.md, which only 6 of ~95 projects have) | ~4,100 words |
| No Claude session at all | `ui_web.md`, `web_design.md`, `hammerspoon.md`, `mac_env.md`, `audio.md`, `ios.md` | — |

Why the last row happens: `build_rules.py` compiles `CLAUDE.md` once, with ai-os as the workspace and an empty prompt. The keyword step that would add topic files never matches anything. `web_design.md` isn't even in the keyword list.

What this means in practice:

- **The school rule is missing where it's needed.** "Never write graded work" is not in `~/.claude/CLAUDE.md`, and no course folder has a CLAUDE.md (`~/Documents/School/*`, `~/projects/school`). A session opened on a lab sees nothing.
- **The project freeze (2026-10-27) only exists in ai-os.** Outside ai-os, `~/.claude/CLAUDE.md` still says "new projects are welcome… the flag is lifted."
- **A rule written yesterday reached no one.** "Never run `hs -c 'hs.reload()'`" was added after two ~50-minute hangs on Oct 28. It lives only in `hammerspoon.md`, which no Claude session loads, and no hook blocks the command.
- Model-by-pace, obvious-wants, drive-the-web-app-yourself, curated exemplars and icons-not-text are also ai-os-only.
- `ai-os/CLAUDE.md` is ~79 KB, about twice the size Claude Code itself warns hurts performance.

### 3.2 Two hand-kept copies, a third in memory, and a rule that requires copying

`.rules/` is the source, but `~/.claude/CLAUDE.md` is written by hand (last edited today at 19:32). The rule "Proactive System Directive" tells agents to save each new rule in three places: `.rules/`, `~/.claude/CLAUDE.md`, and the project's instructions. That rule is what manufactures the drift. Confirmed drift:

- **rm.** `.rules` says "NEVER use rm (except node_modules)". `~/.claude` (2026-10-23) says rm is fine in scratch, tmp, cache and old worktrees, and to clear them without asking.
- **Freeze vs welcome** (see 3.1).
- **Undo.** The memory file `make-it-live-by-default` says "then tell him… want me to undo it?". The rules say never ask that.
- **Approvals.** The memory file `emoji-quick-replies` says to ask "Reply 👍 to…". In the Code tab, reactions stopped working on 10-27 and the Action bar replaced them.

### 3.3 Churn and noise for Tyler

- About 100 commits touched `.rules/` in 10 days (24 on Oct 21 alone).
- `setup/matt/CHANGES.md` collected 10 entries for Tyler in two days. That includes the same rule twice (1r), titled by a grab-bag section name ("Anti-Scope-Creep…") that says nothing about the rule.
- Matt-only rules (his lights, his Hammerspoon, his school) go into Tyler's Yes/No queue. Tyler's `decisions.md` is still empty.
- Today they agreed on "every few days", with Matt's "circles" (shared core → Slub core → Matt's recommended defaults → everything else). The pipeline doesn't know those circles exist yet.

### 3.4 Codex already has the system Matt wants; Claude doesn't

- **Codex** gets a short generated prompt plus topic packs injected per prompt (`config/codex_policies/policy_*.md` via `codex_hooks/on_user_prompt.py`). It also has a tested `tool_guard.py` that blocks `rm`, `.env` reads, npm/yarn/pnpm and `/tmp`, with a shadow mode, rollback and an audit log. The log shows real blocks as recently as 10-27.
- **Claude's** PreToolUse hooks cover input clearance, long commands, the browser pane and thread size. **Nothing blocks rm, secrets, npm or `/tmp` for Claude.** The secret gate exists only at commit time, inside `auto_commit.py`.
- Porting the Codex guard and pack loader to Claude is mostly an adapter job (angle A covers how).

### 3.5 Rules that fight Claude Code's own instructions lose

Claude Code's built-in system prompt, which agents read on every turn, says:

- commit or push only when the user asks
- confirm before actions that reach outside the session
- publish pages as Artifacts
- ask with menus and session cards

Matt's rules say:

- always push
- make it live without asking
- pages on Vercel, not Artifacts
- plain-text questions only

With two instruction sets in tension, the model hedges. That fits C's top failure: 134 turn-ends asking "want me to / should I / reply 👍". **These are the rules that most need hooks**, because text alone keeps losing to the system prompt.

### 3.6 Six "wait" rules and four "just do it" rules with fuzzy edges

- **Wait:** ideas wait for 👍 (1f); show 3–4 UI options first (1o); think alone first (1j); start from curated exemplars (1r); restate complex logic first; ask Matt to test menu bar items.
- **Act:** always push; make it live; obvious wants, just do it (1g); no API? drive the web app yourself (1n).
- Each rule is reasonable. Together they leave the agent unsure on every turn, so it asks.
- This is a design flaw, not an obedience problem. Fix it with **one rule**: wait only for (a) an idea Matt hasn't asked to build, (b) something irreversible or that reaches outside the Mac, (c) a real fork where the outcomes differ, or (d) the visual direction of a new product. Otherwise do it, then report.

### 3.7 Rituals with low compliance

From C's counts and my own checks:

- **Details file on every reply:** missing on 69% of replies over 40 words. New details files fell from 57 on Oct 22 to 1 a day on Oct 28–29.
- **Readthrough publish on every reply:** rarely done.
- **Quiz menus must be multi-select:** 59% weren't.
- **Replies over 150 words:** 28% of turn-ends.
- **`preflight.py`** last ran Oct 27. Its main check is `ag-quota`, an Antigravity tool, and Antigravity is shelved.
- **`DEVELOPMENT_JOURNAL.md`** was last written Oct 21, and `agent-logs/` Oct 20 (around the switch to Claude).
- **`wiki-engine`** is not installed.
- **`PROJECT_BOARD.md`** was last touched Oct 21. The rules themselves now call Linear "where Matt actually looks."

A rule followed less than half the time is worse than no rule. It costs attention on every turn and buys nothing. Each one should be automated, enforced or deleted.

### 3.8 How the rules are written

- **Two styles are mixed.** Gemini-era rules shout: "Zero-Tolerance", "Invariant", "MUST NEVER", ALL CAPS. Newer rules are plain sentences with a reason, which current Claude models follow better. Shouting tends to make models over-apply a rule in the wrong places.
- **Firm wording still matters.** Tyler's Drum ID lesson: a rule worded "it would be great if…" got ignored. Write "do X", calmly, with one clause of why.
- **Incident stories crowd the rules.** About 40% of the text is "Why: on Oct 21 an agent…" plus quoted Matt sentences and dated amendments. That history is useful for an autopsy, but it should live in a changelog. Every working agent pays for it on every turn.
- **Rules sit under the wrong headings.** "Link every file" is under *Music*. Half of the "Anti-Scope-Creep" section adds scope: settings screens, onboarding, live tweaks for every app, 3–4 separately made design options. "Restate complex logic" is under *Voice Tasks*. Two rules are both numbered 1g, and the secrets list has two item 5s.

---

## 4. Rule-by-rule verdicts

**Form** = what each rule should become:

- **BLOCK:** a PreToolUse hook denies the action, with a message saying what to do instead.
- **INJECT:** the rule loads only when a trigger fires (prompt words, folder, file type, a tool being used).
- **CHECK:** an end-of-turn (Stop) hook checks the reply or the repo, and blocks once with a fix-it message.
- **AUTO:** a hook or tool just does it, so the text can go.
- **CORE:** judgment; a short line in the always-loaded core.
- **ROLE:** loads only for one kind of session (coordinator, cloud).
- **DELETE / SHELF:** remove it, or park it in `shelf/` with Antigravity.

### 4.1 core_safety.md: setup and environment

| Rule | Verdict | Why (blunt) | Form |
|---|---|---|---|
| Project-root definition, `git rev-parse` advice | Delete | Claude Code and git already handle this; it's script-writing advice | DELETE (scripts README) |
| No git repo in `~` | Keep | Cheap and mechanical | BLOCK `git init` when cwd is `~` |
| `AG_CONTEXT.md`: read first, create if missing | Keep | One of the few rituals still alive (54 projects, updated yesterday) | AUTO: SessionStart prints it, or a one-line project CLAUDE.md with `@AG_CONTEXT.md` |
| rm → `~/.Trash` | Keep, fix | Irreversible harm. `.rules` and `~/.claude` disagree; use the newer allowlist (scratch, tmp, caches, node_modules, old worktrees) | BLOCK (port Codex `tool_guard`) |
| bun, never npm/pnpm/yarn | Keep, cut a clause | "Migrate any npm project to bun before your main task" forces a migration into every task. That's scope creep against the marginal-change rule. Keep the ban, drop the forced migration | BLOCK npm/pnpm/yarn/npx (suggest `bunx`) |
| New repos `--private` | Keep | Cheap and mechanical | BLOCK `gh repo create` without `--private` |
| No system `/tmp` | Keep | Real (C: 14 hits). The harness scratchpad is under `/private/tmp/claude-*`, so a naive block would break it | BLOCK, allowlist the scratchpad |
| Don't litter generic folders; Antigravity scratch fallback | Shrink | Keep "new projects go in `~/projects/<name>`"; the Antigravity clause is dead | CORE (1 line) |
| VPS database first | Keep | Cost and ownership; pairs with the "ask before heavy VPS work" memory | INJECT on database or hosting words |
| Always test after a change | Keep | The heart of shipping | CORE + CHECK (code edited and nothing run since → remind once) |
| puma-dev `.test` domains | Keep, small | Nice, low stakes | INJECT when starting a dev server or editing `launch.json` |
| Menu bar: ask Matt to test | Keep | A real Bartender fact | INJECT on `NSStatusItem` / `hs.menubar` edits |
| Path migration `matthewmurphy` → `matt` | Delete | Finished; only old Antigravity scripts and the guard itself still contain the path | DELETE |

### 4.2 core_safety.md: life and personal workflow

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Apple Reminders right away; create, then offer to delete | Keep | Serves his life directly; works on his phone | INJECT on to-do and follow-up wording |
| No sleep reminders; habits stay off the calendar | Keep | Tiny, real | Rides with the reminders pack |
| Music links via the resolver, no AI music | Keep | Clear taste rule with a deterministic tool | INJECT on music asks |
| Zero placeholders; identity file only when needed | Keep | Cheap and embarrassing when missed | CHECK (regex `\[Your [A-Z]` in replies or written files) + INJECT on forms and email |
| QMD recall | Shrink | Already automatic (two hooks) | CORE (2 lines) |
| Obsidian vault path and schema | Keep | Stops agents inventing `~/wiki` | INJECT on note and wiki words |
| School: never write graded work | **Keep, top priority** | Expulsion risk. **Currently absent outside ai-os** | INJECT by folder (`~/Documents/School`, `~/projects/school`), by course names or Canvas; PreToolUse `ask` on writes under school folders |
| Studying logic: start at symbols, tiny steps | Keep | Specific and kind; it works | INJECT with PHIL 120 / logic / quiz |
| Quizzes: AskUserQuestion, multi-select, 4 per round | Keep | 59% broken, so it needs a hook | BLOCK AskUserQuestion unless every question is multi-select (this also mostly enforces "no menus outside quizzes") |
| Voice tasks: report back via `voice_reply.py` | Keep | Exact trigger exists (the "🎙️ Voice task" marker) | INJECT on the marker |

### 4.3 core_safety.md: how agents talk to Matt

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Every Word Costs Matt (budget, line 1 is the answer, one idea per line, max 4 items, cut list) | Keep the heart, cut 80% | The most valuable rule in the set, written as a ~1,600-word wall about brevity. Keep ~8 lines plus the one before/after example; examples teach better than lists | CORE + CHECK (over ~150 words with no "detail" ask → trim once) |
| Clarity beats brevity | Keep | Fixed a real overcorrection | CORE (1 line) |
| Important things in the reply, never only in a file | Keep | Key safety valve for his attention | CORE |
| Details file before every reply | **Change** | 69% ignored, now ~1 a day. The autopsy goal is already covered: transcripts are exported and indexed in QMD automatically. Keep a details file only where a reply overflows its budget | CORE ("overflow goes to the details file") or AUTO (a cheap-model summary at session end) |
| Readthrough publish on every reply | Delete as default | A public deploy per reply, mostly skipped. Offer it on request | DELETE → on request |
| Heading link per bullet, `---` spacing, 2-word bold-label quirk | Move | Formatting notes for the details file, not rules | details-file doc |
| Reels for big replies | Delete as default | The most expensive habit in the set (TTS + render + deploy, with hang hazards), and it produces more content to consume. Keep for when he asks | DELETE → on request |
| Read aloud means no repeats | Keep | He listens now; real | CORE (1 line) |
| "Try this" comes with a command | Merge | "Until action buttons exist" is stale (they exist). Merge with "hand over the project: folder link + run command" | CORE (1 line) + CHECK |
| Always link threads | Keep | Cheap | CORE |
| Link every file/folder (do.test + `/mnt/project-files` + SendUserFile layers); link every service | Shrink | C: missing links are a repeat complaint. The three-layer scheme was built for Projects threads, which Matt and Tyler dropped today. In the Code tab, plain markdown links already open in the file pane. Re-test whether do.test is still needed there | CORE ("link files, folders and services") + CHECK for bare paths |
| Universal progressive disclosure (`<details>`, `<br>`, span max-width) | Delete | Contradicts "the Code tab shows raw HTML." Keep the idea as a Slub product pattern (Tyler liked it today) | DELETE |
| Span-only styling invariant | Delete | A Gemini-era artifact-renderer patch; wrong for every surface now (also copied into `ui_web.md` and the Codex frontend pack) | DELETE |
| Ask in plain text, never menus (quizzes excepted) | Keep | Real: menus block dictation | CORE + the quiz BLOCK above |
| Action bar (labels are a verb plus its object, agent actions only, `|` for either/or) | Keep | Replaced emoji in the Code tab; C: 195 uses, label complaints | CORE + CHECK (labels ≥2 words, no bare numbers, nothing only Matt can do) |
| Emoji quick replies, "Reply 👍 to…" | Delete for the Code tab | Reactions don't work there since 10-27; still taught in three places plus memory | DELETE (keep only if some surface still supports reactions) |
| Restate truly complex logic first | Keep | Softened correctly on 10-28 | CORE (1 line, under the act-or-wait rule) |

### 4.4 core_safety.md: building and design

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Architectural preservation (fix the root cause, don't strip custom work) | Keep | A general good rule | CORE (1 line) |
| New utilities welcome / from-scratch flag lifted | Suspend | Superseded by the freeze, yet it's what most sessions see | Remove from `~/.claude` while the freeze lasts |
| Project freeze until the Tyler merge | Keep, add an end | Right for now; needs a stated end ("until Matt says the merge has started") or it will rot | CORE |
| Look for existing tools first | Keep | Saves whole builds | INJECT when a project is created (`mkdir ~/projects/x`, `pages new`, `git init`, new repo) |
| Systems over one-offs | Keep | It's who Matt is | CORE (1 line) |
| Shared modules | Keep | Reuse across the suite | INJECT on Hammerspoon / hud-kit / pages work |
| Live tweaks for every app | Narrow | Great for HUD and feel work; overkill for scripts | INJECT on HUD/UI feel work; `tweaks scan` does the rest |
| Ship-ready by default (settings, onboarding, README) | Narrow | Settings and onboarding on every build is the complexity the freeze forbids. Keep "self-contained, README, runs in one step" for everything; settings and onboarding only for "for the world" builds. Today's Drum ID 0.0.1 decision is the model | CORE (narrowed) |
| Discoverable by design; icons not text alone; every press shows it landed | Keep | Good UX principles, but only matter in UI work | INJECT (UI pack) |
| Think alone first + curated exemplars + 3–4 separately made options + UI Mixer | **Merge** | Stacked, these are four gates before any code, each costing Matt a decision and several agents. One flow: exemplar links → he picks → build → side-by-side compare. Separate-agent options only for Slub-branded "for the world" products | INJECT (UI pack, one flow) |
| Obvious wants: just do it / ideas wait for 👍 | Merge | Into the one act-or-wait rule (3.6) | CORE |
| Ideas go in VISION/IDEAS with an honest take | Keep, narrow | Valuable, but "every idea however small, even mid-call" turns chats into paperwork. Ideas he states as ideas get logged; passing remarks don't | CORE (merge with Slub core rule 4) |
| Proactive behaviour over skills | Move | A principle for whoever writes rules (it's why this migration exists), not for working agents | rule-authoring guide |
| Save working methods | Keep | Makes repeat tasks faster | CORE (1 line) |
| No API? drive the web app yourself | Keep | Good | CORE (1 line) |
| Same experience in Code and project threads | Delete | Projects mode was dropped today | SHELF |
| Sustainable marginal change; call out wheel-spinning | Keep, strengthen | The only real anti-scope rules in the anti-scope section. Make it concrete with checkpoints (§6) | CORE |
| Skills: `_` prefix, action-first name | Keep | Cheap | INJECT on writes under `skills/` |
| Skills: workflow parity with `~/.gemini/global_workflows`; auto-sync | Delete parity; automate sync | Antigravity is shelved; the sync is mechanical | AUTO (PostToolUse on `skills/` writes runs `sync_skills.py`) |
| Secrets: never read `.env*`/keys, `aios-env`, open-don't-hunt, commit gate | Keep | Real harm, and the Tyler export makes leaks worse | BLOCK (port Codex guard) + existing AUTO gate in `auto_commit.py` |
| Secrets: vendor-ingestion scan | Keep, niche | Rare | INJECT on fork/vendor work |
| Model family naming (no version numbers) | Delete | Cosmetic, and it clashes with the exact IDs the harness itself provides | DELETE |
| Verify model IDs before hardcoding | Keep | Prevents real bugs | INJECT when code contains `claude-` / `gpt-` / `gemini-` strings |
| Model choice by usage pace | Keep | The main cost lever; ai-os-only today | INJECT at Coordinator SessionStart and before `start_session`/Agent (one line from `claude_pace.py`) |
| Pages on Vercel, not Artifacts; shareable markdown → `pages md` | Keep | Fights the harness's Artifact push every session | INJECT on the Artifact tool (PreToolUse reminder) |
| Hand over the project: folder link + run command | Keep | C: repeat complaint | CORE + CHECK (merge with "try this") |

### 4.5 core_safety.md: Mac automation, colour, HUDs

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Take-control queue (`claude-control ask`, `done`, tiers, Esc vs Stop, shows, fullscreen, deterministic automations) | Keep, shrink text | Essential with many agents on one Mac. ~700 words is mostly tool documentation; it belongs in `claude-control --help` and the deny message. **Contradiction:** the rule says fail closed, but `input_guard.py` says it fails open when Hammerspoon is unreachable. The hook covers Bash only; C counted 31 computer-use/Chrome input calls without clearance | BLOCK (extend `input_guard` to computer-use and Chrome input tools; decide fail-open vs fail-closed) + INJECT on Hammerspoon/KM automation code |
| Never terracotta / no orange | Merge | Four copies plus memory; it follows automatically from "palette only" | DELETE once the palette lint exists |
| Never invent a colour; palette by role | **Blocked on a decision** | `ARCHITECTURE.md` says "No colours are picked yet" (since Oct 22). For a week, "add no new hard-coded colours" has been impossible to follow; every UI since either broke it or used no colour. Matt has to pick the palette (or name an interim one) | then BLOCK-lite: PostToolUse lint on CSS/Swift writes (colour not in the palette → flag) |
| No Claude-default look (fonts, cream, card grids) | Keep | Real brand value for Slub | INJECT (UI pack) + lint for banned fonts |
| No orphans | Keep | Taste, with a checker | AUTO (`orphans.cjs` inside `pages deploy`) + INJECT |
| Check against EXEMPLARS.md; light and dark always | Keep | UI quality | INJECT (UI pack) + lint for `prefers-color-scheme` |
| HUD slots; HUDs move, resize, snap | Keep | Real collisions happened | INJECT on HUD code + AUTO (run `hud_layout_test.lua` after `hud_slots.json` edits) |

### 4.6 core_safety.md: coordinators, cloud, Projects

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Split asks before routing; meta stays with the coordinator; size check; "why did you do that" is a real question; no analysis in the coordinator; thread cleanup; show 5 at a time | Keep, move | Only coordinators need these. "Why did you do that? Give the real cause first" is good for every agent | ROLE (`code-coordinator.md`) + one CORE line |
| Projects-era routing (`cmsg_`, warm-thread 45 min, 30-thread cap, `/coord`, pointer-only project instructions) | Delete | Projects mode was dropped today | SHELF |
| Cold threads under 250k resume; size hook | Keep | Hook is live | AUTO (`thread_size_guard.py`) |
| Long threads: write HANDOFF.md after compaction or ~40 messages | Delete | Clashes with "~200k → /_handoff" (`~/.claude`), with the 250k hook, and with Matt's point today that early handoffs lose detail. Pick one threshold, the hook's | DELETE |
| Cloud threads: blocked sites go through the Mac | Keep | Only for cloud sessions | ROLE (cloud) |

### 4.7 git_protocol.md, agent_logs.md, claude_only.md

| Rule | Verdict | Why | Form |
|---|---|---|---|
| Run `preflight.py` before any work | Delete | Last run Oct 27; it mainly checks Antigravity quota. Keep only the useful bit (pull) | AUTO (SessionStart `git pull --ff-only` if clean, like `slub-sync.sh`) |
| Auto-commit and push; always push, never ask | Keep | C's #1 failure. Text loses to the harness's "commit only when asked" | CHECK (dirty or unpushed repo touched this session → commit/push or name the real fork) |
| Crossword: `working` branch only, never `main` | Keep | Public production | BLOCK (commit or push to `main` in that repo) |
| Make it live by default | Keep | Part of the act-or-wait rule | CORE |
| Ubiquitous git tracking; notify about untracked files | Narrow | "Notify Matt every time" is noise and makes repos for scratch. Track `~/projects/*` and config folders, mention it in one line | CORE (narrowed) |
| Read FEATURES / DEVELOPMENT_JOURNAL / agent-logs; write logs and a journal at session end | Delete | Dead since about Oct 20 | DELETE |
| Mandatory wiki recording via `wiki-engine` | Delete | The tool doesn't exist | DELETE |
| Master project board protocol | Delete | Linear replaced it | DELETE |
| No command may hang a thread | Keep | Hooks already enforce it; the text can be one line | AUTO (existing) + CORE (1 line) |

### 4.8 Topic files no Claude session loads

| File | Verdict | Notes |
|---|---|---|
| `ui_web.md`, `web_design.md` | Turn into the UI pack | Unique good rules exist only here: modals close on Esc and click-outside, spatial continuity, Mantine over hand-rolled widgets, no Tailwind unless asked, surface archetypes. Light mode, span-only and HUD slots are duplicated elsewhere; drop span-only |
| `hammerspoon.md` | Turn into a Hammerspoon pack + hooks | `hs.reload` → BLOCK. The qwerty-midi reload → AUTO (PostToolUse on edits there). AX-liveness tips → that project's AG_CONTEXT |
| `mac_env.md` | Mostly delete | The screen-capture text names Antigravity's tools. The TCC reset tip → saved methods |
| `audio.md` | Move | AbletonMCP is a real routing rule (INJECT on Ableton); the Web Audio tips belong in the synth repos' AG_CONTEXT |
| `ios.md` | Delete | Two content-free lines |
| `gemini_only.md`, `subagent_leaf.md`, `LEAF.md` | Shelf | Antigravity is shelved |
| `codex_only.md` | Delete | Not even used for Codex: the minimal Codex prompt returns before reading it. It duplicates the YouTube transcript skill |

### 4.9 `~/.claude/CLAUDE.md`-only items

| Rule | Verdict | Form |
|---|---|---|
| Start with ABOUT_MATT; refresh SCHOOL.md when stale; search the Mac before asking about himself | Keep | CORE (short) |
| Old AI threads (`threads.py` recipe, ~250 words) | Keep, move | INJECT on "Gemini / Antigravity / that earlier conversation" |
| Shelved tools list | Keep | CORE (2 lines; stops dead tools being used) |
| Everything else | It's the condensed copy of core_safety | Regenerate from the single source |

### 4.10 Slub `core.md` (8 rules) and slub-hq `CLAUDE.md`

| Rule | Verdict | Why | Form |
|---|---|---|---|
| 1 Visible by default (NOW.md line) | Keep | The rule that makes collaboration work | CORE + CHECK (new repo or project folder this session, no NOW.md line → remind) |
| 2 Check before building | Keep | Prevents double builds | AUTO pull (exists) + INJECT at project creation (same trigger as existing-tools-first) |
| 3 Look for connections | Rewrite | Tyler is right that it's vague. Give it a trigger: "when your work touches a repo, file or idea named in NOW/IDEAS/notes, say so in one line" | CORE |
| 4 Ideas in files | Keep | Merge with Matt's ideas rule | CORE |
| 5 Tasks per person; 6 inbox | Keep | `slub-sync.sh` surfaces the inbox but **not TASKS.md**; add it | AUTO |
| 7 Model-neutral, Slub-only | Keep | Matters for the "Slub sauce" goal | INJECT when editing slub-hq |
| 8 Never act as someone else | Keep | Bright line | CORE |
| Header ("forever") | Reword | Already a pending task; Tyler misread it today | — |
| slub-hq `CLAUDE.md` repeats rules 1–7 with different numbering next to `@setup/core.md` | Merge | Two copies in the same repo; agents there read both | keep CALLS/notes specifics + the import |

### 4.11 Memory (ai-os project, 55 files, 30 "feedback")

- **Memory only loads in ai-os sessions, yet many memory files restate rules,** and at least two now contradict them (undo, emoji).
- **Memory should hold facts** (who, where, how a tool behaves, gotchas). A preference that's really a rule moves to `.rules/`, and the memory file is deleted.
- **CHECK:** a reply that says "saved as a global rule" when only memory changed gets blocked. C logged a coordinator treating a memory note as a global rule.

---

## 5. Contradictions, in one place

1. **rm:** never (`.rules`) vs fine in scratch/tmp/cache (`~/.claude`, 10-23).
2. **New projects:** welcome (`~/.claude`) vs freeze (`.rules`, 10-27).
3. **Make it live:** "then offer undo" (memory) vs "never ask about undo" (rules).
4. **Approvals:** "Reply 👍" (rules, `~/.claude`, memory) vs the Action bar (10-27).
5. **Handoff threshold:** ~40 messages / ~200k / 250k.
6. **Take-control:** fail closed (rule) vs fail open (`input_guard.py`).
7. **Tyler:** "it syncs to Tyler" (rule, said on every saved rule) vs "never applies to Tyler automatically" (today's decision).
8. **Act vs wait:** six wait rules vs four act rules (3.6). This is the root of C's #1 failure.
9. **Ship-ready + tweaks + shared modules + 3–4 design options** vs freeze and marginal change.
10. **HTML disclosure and span wrappers** vs "the Code tab shows raw HTML."
11. **Matt's rules vs Claude Code's built-in instructions:** push, Artifacts, menus (3.5).
12. **Max 4 items per reply** vs coordinator "show 5 at a time."
13. **Bun "migrate first"** vs marginal change.

## 6. Missing rules (the ones that would help Slub ship)

1. **Rules about rules (for whoever writes them, not loaded into working agents):**
   - One source; every other copy is generated, never hand-edited.
   - Each rule carries a **scope tag** matching Matt's circles: `shared-core` / `slub` / `matt-recommended` / `matt-only`. Only `slub` and `matt-recommended` reach Tyler's queue, batched weekly.
   - Each rule carries an **enforcement tag** (block / inject + trigger / check / core).
   - A **budget for the always-loaded core** (~60 lines); a new core rule means an old one moves out.
   - **Incident stories go in a changelog,** not the rule.
   - A **review date** on incident patches: no repeat and no hook after 30 days → archive.
   - **Firm, calm wording:** "do X" with one clause of why; no "it would be great if", no ALL-CAPS invariants.
2. **One act-or-wait rule** (3.6), replacing six.
3. **A named checkpoint per project and a definition of "done".**
   - Each active project names its next checkpoint, in the 0.0.1 style: self-contained, and someone else can open it.
   - "Done" means tested, pushed, live or installed, NOW.md updated, and the other brother told if it touches him.
   - Work past the checkpoint gets flagged once ("this is polish past 0.0.1, keep going?"). This turns "call out wheel-spinning" from a mood into a check.
4. **A limit on active projects:** at most 3 NOW.md lines per person. A 4th means one gets parked. Cheap to CHECK; it matches the freeze's spirit permanently.
5. **A cost note before fan-outs.** Any step that starts 3+ agents, renders media, uses TTS or deploys says its rough cost in one line first. Mechanical sub-work runs on Sonnet and judgments on Opus (Tyler's existing habit, worth adopting).
6. **Plain-English notes for Tyler** (his "psychotic levels of clarity").
   - Any change to how slub-hq works (where notes, tasks or transcripts land; how changes reach him) comes with a short note in `inbox/tyler.md`.
   - His agent decides how to present it. Matt-only rules never reach his queue.
7. **Be honest about saved rules.** Never say a rule is saved or global unless `.rules/` changed and the build ran (CHECK).
8. **Exports must work without Matt's Mac.** `export_setup.py` flags Matt-only paths (`do.test`, `~/.hammerspoon`, `claude-control`) in anything offered to Tyler.
9. **A conflict order:**
   1. safety (secrets, data loss, school, other people's accounts)
   2. Matt's latest explicit words
   3. the freeze
   4. everything else
10. **Optional, weaker:** on Coordinator SessionStart only, one line with the next 48 hours of due dates from SCHOOL.md. It might protect school focus, but it's a nag risk, and the habit gate already covers logic practice. Try it only if Matt wants it.

## 7. What the always-loaded core could hold (~40 lines)

These are titles only; the wording is for the merge thread (D). Everything else becomes a hook, a pack or a role file.

- **Who and where:** ABOUT_MATT first; search the Mac before asking; shelved tools.
- **Conflict order** (§6.9).
- **Act or wait** (one rule): make it live, always push, obvious wants, restate only truly complex logic.
- **Replies:** line 1 is the answer; ≤ ~100 words, clarity first; one idea per line with blank lines; max 4 items; important things in the reply; overflow goes to the details file; one plain-text question at most; Action bar for approvals; link threads, files and services; folder link + run command after changes; no repeats for read-aloud. Plus one before/after example.
- **Building:** test after changes; fix root causes without stripping custom work; marginal change, checkpoints, call out wheel-spinning; systems over one-offs; save working methods; drive the web app yourself; existing tools first (backed by a hook); ship-ready = self-contained + README.
- **Freeze** (with an end condition).
- **Slub core 8** (header reworded, rule 3 rewritten).
- **"Why did you do that?"** gets the real cause first.

## 8. Decisions only Matt (with Tyler where noted) can make

1. **Pick the palette,** or bless an interim one. Without it, the colour rules can't be followed or enforced.
2. **Details files:** overflow-only, or auto-generated at session end? Readthroughs and reels: on request only?
3. **The freeze's end condition.**
4. **Take-control when Hammerspoon is down:** fail open (current hook) or fail closed (current rule)?
5. **Whether do.test is still needed** in the Code tab now that Projects threads are dropped (one quick test).
6. **With Tyler:** the scope tags (the circles) and how often the rule digest arrives.

## 9. What changed from the low-effort pass

- **Corrected:** the first pass said ~15,000 words load into every session. Only ai-os sessions get that; everywhere else gets ~4,100 words of a hand-kept summary. That shifts the main problem from "too much text everywhere" to "the wrong text in most places, and too much in ai-os."
- **New:** six topic rule files reach no Claude session (the build's keyword step never fires), including yesterday's `hs.reload` hang rule.
- **New, most important:** the school ghostwriting rule is missing outside ai-os, and no course folder has a rule file.
- **New:** the freeze is missing outside ai-os, and `~/.claude` says the opposite.
- **New:** Codex already has the pack loader and a tested guard for rm, secrets, npm and `/tmp` (with shadow mode and rollback); Claude has none of these guards. Recommendation: port it, don't rebuild it.
- **New:** rules that fight Claude Code's built-in instructions are the ones that fail. The act-vs-wait muddle explains C's top failure.
- **New contradictions:** `input_guard` fail-open vs the fail-closed rule; "syncs to Tyler" vs today's opt-in decision; the handoff threshold appearing three ways; the memory files contradicting the rules (undo, emoji); the "migrate to bun first" clause.
- **New facts:** the palette isn't picked, so the colour rule is stuck; preflight last ran Oct 27 and checks an Antigravity quota; details files fell from 57 to 1 a day; `codex_only.md` is unused even by Codex; `slub-sync.sh` doesn't surface TASKS.md; Tyler's change queue has duplicates and Matt-only rules; slub-hq `CLAUDE.md` duplicates `core.md`.
- **Kept, now with evidence:** the stale list (agent logs, project board, Antigravity files, progressive disclosure, span-only), the redundancy list, and the hard-block list.
- **Dropped or softened:** the claim that AG_CONTEXT belongs with the dead rituals (it's alive; automate loading it). The flat "make reels and Readthroughs end-of-session" became "on request". Rule-by-rule hook forms now cover every rule, not just a sample.
