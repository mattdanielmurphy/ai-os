# B · Honest audit of Matt's rules (2026-10-29)

Angle B of 3 (A architecture, C failure evidence). Analysis only: no rule was changed.

Read: slub-hq `README.md`, `NOW.md`, `IDEAS.md`, `NAMES.md`, `setup/core.md` (there is no `VISION.md`), ai-os `docs/ABOUT_MATT.md`, every `.rules/*.md`, `~/.claude/CLAUDE.md`.

## The headline

**The rule set is about 15,000 words loaded into every session, and that size is itself the biggest failure cause.** `core_safety.md` alone is ~11,350 words; `~/.claude/CLAUDE.md` repeats ~3,800 words of the same content as a summary. Every rule is stated at least twice (often three times: `.rules/`, user CLAUDE.md, memory), with slightly different wording and dates. An agent reading this cannot hold it all, so it obeys whatever was nearest the top or most recent. Tyler and Matt already named the fix on the 2026-10-29 call (slub-hq IDEAS: "concierge gives the model only the rules each task needs"). That is right, and it matters more than any individual rule below.

**Most rules are good preferences written as incident reports.** A typical rule is one line of intent plus three lines of "Why: on Oct 21 an agent…" plus quoted Matt sentences plus dated amendments. The why is valuable for Matt's autopsies but costs every agent attention every turn. Keep the why in a changelog; ship the rule as one line.

**The goals the rules should serve** (from slub-hq + ABOUT_MATT): Matt and Tyler ship audio software and small utilities under Slub; Matt is a student with limited attention (ADHD-ish, behind in PHIL 120); they share one agent setup; usage quota is finite. So the rules should buy: shipping, Matt's focus, safe Mac automation, Matt+Tyler collaboration, and cost. Measured against that, roughly a third of the current text earns its place.

---

## 1. Rules that clearly serve the goals (keep, mostly as hooks)

| Rule | Why it earns its place | Best form |
|---|---|---|
| Secrets: never read `.env*`, use `aios-env`; commit secret gate | Real, irreversible harm; Tyler sync makes leaks worse | **Hard block** (PreToolUse on Read/Bash matching `.env`, keys) + existing `auto_commit.py` gate |
| `rm` → `~/.Trash` except scratch/caches | Irreversible harm | **Hard block** (Bash matcher, allowlist scratch/tmp/node_modules) |
| Take-control queue (claude-control ask before input) | Several agents on one Mac really do collide; Matt was burned | **Hard block** (`input_guard.py` exists; extend to `open`, `osascript`, computer-use, media) — fail closed |
| No command may hang a thread | Already a hook; proven | Keep hook (`bash_timeout_guard.py`, `browser_pane_guard.py`) |
| Thread size guard at 250k | Already a hook; cost | Keep hook |
| School work: never write graded work | Expulsion risk; the most consequential rule in the set | **Just-in-time reminder** when cwd/paths match course folders or Canvas; stays judgment otherwise |
| Always test after a change, report honestly | Core to shipping | **End-of-turn check** (Stop hook: files edited this turn but no test/run command → nudge) |
| Always commit and push (except crossword `main`) | Shipping + Tyler sync | **End-of-turn check** (dirty tree in touched repo → block stop once) + **hard block** on push to crossword `main` |
| `bun` not npm/pnpm/yarn | Cheap, mechanical | **Hard block** (rewrite hint in deny message) |
| New repos `--private` | Cheap, mechanical | **Hard block** on `gh repo create` without `--private` |
| No `/tmp`, use `./tmp` or scratchpad | Mechanical | **Hard block** (light) |
| Every Word Costs Matt (short, clear replies) | Directly serves Matt's attention, the scarcest resource | Judgment, but **shrink the rule to ~8 lines**; an end-of-turn word-count nudge (>150 words, no "detail" request) is cheap |
| Look for existing tools first | Saves build time | **Just-in-time** when a session starts a new project folder / `pages new` / `git init` |
| Model choice by usage pace | Cost | Judgment + `claude_pace.py`; a **session-start reminder** only when pace is hot |
| Light + dark, no Claude-default look, palette only | Brand quality for Slub | **Just-in-time** when editing CSS/HTML/Swift UI files; not in every session |
| Visible by default (slub-hq NOW.md line) | The one rule that makes collaboration work | **End-of-turn check** when a new repo/project folder was created this session |

## 2. Redundant (merge or delete the duplicates)

- **Everything in `~/.claude/CLAUDE.md` duplicates `.rules/`.** Delete the user-level copy down to ~15 lines of pointers and hard essentials; let hooks and the per-task loader carry the rest. Today the two drift (e.g. "make it live, then offer undo" in memory vs "don't ask want me to undo it" in rules).
- **Hammerspoon reload** appears in `hammerspoon.md`, `mac_env.md` and `gemini_only.md`. Make it one PostToolUse hook on edits under `qwerty-midi-hammerspoon/` and delete all three texts.
- **HUD slots** appears in `core_safety.md`, `ui_web.md`, user CLAUDE.md. One copy, as a just-in-time reminder when editing HUD code.
- **Terracotta/orange** appears four times (core_safety, web_design, ui_web, user CLAUDE.md) plus memory. Fold into "colours come only from the palette": if palette-only is enforced (lint for hex literals not in the palette), the terracotta rule is automatically true and can be deleted.
- **Light mode default** in three files. Same merge.
- **Architectural preservation** in core_safety and ui_web.
- **Apple Reminders** in core_safety, ios.md, user CLAUDE.md, plus "no sleep reminders" and "habits off calendar" each three times.
- **"Rules are global / say it's global / synced to Tyler"** is stated in four places. It's a property of the system, not something each agent must remember. `build_rules.py` can print the confirmation line; delete the prose.
- **Emoji quick replies vs Action bar**: emoji reactions "no longer work" in the Code tab (2026-10-27) yet the emoji rule is still stated in full, twice, with "Reply 👍 to…" instructions. Keep only where they still work (project threads, if any remain), else delete.
- **Two rules numbered 1g** in the anti-scope-creep section (Live Tweaks and Obvious wants).

## 3. Contradictory

- **Project freeze (1p, 2026-10-27) vs "new utilities are welcome" (1, 2026-10-22) vs "ship-ready by default, polish by potential" (1h).** An agent gets three directions at once. Pick one current state: the freeze, with an end condition ("until the Tyler merge starts"). Archive the other two until then.
- **"Ship-ready: settings, onboarding, README for every build" vs the freeze's "don't make life more complicated" vs "flag features for imagined users."** Settings screens and onboarding for a one-person Hammerspoon module is the complexity the freeze forbids. Narrow ship-ready to builds the agent marks "for the world".
- **Show 3–4 separately-made UI options before any code (1o) + start from curated exemplars (1r) + think alone first (1j) + UI Mixer after one round (1m).** That is four sequential gates before a UI exists. Each is reasonable alone; stacked, they guarantee nothing ships and burn quota (4 agents per option round). Merge into one design flow with one gate: "new UI → show 3 exemplar links or quick renders, Matt picks, build". Mixer only if he asks.
- **Details file + Readthrough + reel for every reply vs "every word costs Matt" and cost.** Every non-trivial reply must append a details section, publish a Readthrough (a deploy), link each bullet to a `###` subsection, attach via SendUserFile, and add do.test links; big replies also need a narrated video. That's often more tokens than the work. The intent (autopsy-ability) is good; the mechanism is too heavy. Make the details file an end-of-session artifact (or generated by a cheap model from the transcript by a Stop hook), not a per-reply ritual.
- **"Ask questions in plain text, never menus" vs quizzes requiring menus** — fine, already excepted, but it's stated three times.
- **Action bar "buttons only for agent actions" vs "Reply 👍 to <action>".** Old and new approval mechanisms both live in the rules.
- **"Universal progressive disclosure: use `<details>` and `<br>`, wrap in span max-width"** directly contradicts "Code tab shows raw HTML; plain markdown only". The disclosure section applies to no surface Matt uses now. Delete it.
- **"Span-only styling, never `<div>` or `<p>`"** contradicts basic web work and the pages/Vite stack; it was a patch for one old artifact renderer. Delete.

## 4. Stale (delete or move to the shelf)

- **Agent logs protocol** (`agent-logs/`, `DEVELOPMENT_JOURNAL.md`, "mandatory wiki recording" in `wiki-engine`): `wiki-engine` doesn't exist on PATH; the newest agent-logs found are from July. Nobody follows it, and every agent reads it. Replace with the details file (already the real practice) or delete.
- **Master Project Board** (`PROJECT_BOARD.md`, last touched 2026-10-21): Linear (team MAT) replaced it. Delete the protocol.
- **`gemini_only.md`** (Antigravity tools, `manage_subagents`, `WaitMsBeforeAsync`): Antigravity is shelved. Move to `shelf/`.
- **`subagent_leaf.md`** (`view_file`, `read_lines`, "no quoted heredocs"): Antigravity tool names; wrong for Claude. Shelf.
- **`codex_only.md`** YouTube rule duplicates the `_fetch-youtube-transcript` skill. Keep the skill.
- **`mac_env.md` screen capture** says "Antigravity has Screen Recording permissions… use `view_file`". Stale tool names.
- **Coordinator routing for Claude Projects threads** (`cmsg_`, `/mnt/project-files/`, 30-thread cap, cold-thread 45-min rule): self-labelled "legacy" since the Code-tab coordinator. Move to the coordinator's own doc; it shouldn't load in worker sessions at all.
- **Path migration `matthewmurphy` → `matt`**: probably done; a one-time grep can confirm and retire it.
- **"Thread.md deprecation"**: a rule about a thing that no longer exists.
- **Cloud threads: blocked sites go through the Mac** and the `/mnt/project-files` link conventions: only relevant in cloud/project threads; load only there.
- **`ios.md`** has two generic lines with no content. Delete.
- **`audio.md` Web Audio rules** are code tips, not rules (fine to keep as project notes in the synth repo, not global).

## 5. Over-specific patches of a single incident

These read as "never again X" after one bad day. Each should become either a general principle or a hook, not a paragraph.

- "Two rules: bold link labels need 2+ words" (a renderer quirk). Fine as a hook-free tip in the details-file doc, not global.
- "Hand the coordinator chat off before 30 threads" — a server limit of one product; belongs only in the coordinator doc.
- "Never run `hs -c 'hs.reload()'`" — good, but make it a **hard block** (Bash matcher) and delete the text.
- "Agent told Matt to say 'make it'" — a paragraph about a phrase. The general rule is "never ask Matt to type a phrase; use the Action bar". One line.
- "No API? drive the web app yourself (Linear rename states)" — good principle, keep one line.
- "Amazon.ca via `scripts/amazon_ca.py`" — a saved method, belongs in a methods index, not rules.
- "No orphans" with a per-width checker — real taste, but applies only when building pages. Just-in-time (pages/CSS edits) + run `orphans.cjs` as part of `pages deploy`, i.e. enforced by the tool, not by memory.
- "Icons, never text alone" and "Every press shows it landed" — good UX principles; load with UI work only.
- "Glass TV ignored the hairline style" — generalized fine into "match a named style"; keep the one-line principle, drop the story.

## 6. Cost more attention than they save

- **Per-reply details file + Readthrough publish + bullet anchors + SendUserFile + do.test + reel.** The single most expensive rule cluster, both in tokens and agent focus. See §3.
- **"Every reply that finishes a project gives a folder link + run command" + "link every file and folder" + "link every service" + "link every thread".** Each alone is nice; together, replies become link soup, which fights "every word costs Matt". Keep: link threads and the one file he must open. Tooling (`file_link.py`) could be called by a hook that rewrites bare paths.
- **Live Tweaks for every app** (declare default/min/max/step/note for every feel number). Great for the HUD suite; overkill for a script. Scope it to UI modules.
- **Restate complex logic before building** — already softened twice; fine as judgment, one line.
- **Record every idea with an honest take in VISION/IDEAS and commit** — useful, but "every idea, however small, even mid-call" turns a chat into paperwork. Keep for ideas he states as ideas; skip asides.
- **Ubiquitous git tracking: notify Matt about any untracked file you touch and assume he wants a repo.** That creates repos for scratch. Narrow to config/tool folders.

## 7. Missing rules that would help Slub ship

1. **A rule budget.** "Global rules stay under N lines (say 60); anything else loads per task." Without it the set grows by ~10 rules a week (it has, Oct 20 → 29). New rule in → old rule out or moved to a topic file.
2. **One rule, one place, one owner.** A rule exists in `.rules/` only; CLAUDE.md, memory and slub-hq setup are generated from it. Memory may not restate a rule. (Today memory and rules disagree.)
3. **Every rule says how it's enforced:** `hook:<name>` / `jit:<trigger>` / `judgment`. If neither hook nor trigger, it must be short enough to be remembered. This also makes the hooks migration measurable.
4. **Rules expire.** Each incident patch gets a review date (e.g. 30 days); if no repeat incident and no hook, it's deleted or archived. Stops patch accretion.
5. **Definition of done for shipping.** There's no rule that says what "shipped" means for Slub (version tag? Tyler can install it? one real user?). Many rules govern how to reply about work; almost none push work out the door. Suggest: "done = tested, pushed, installed/live, NOW.md updated, one-line note to Tyler's inbox if it touches him."
6. **Weekly focus cap.** A Slub-level rule like "each person has at most 3 active lines in NOW.md; a 4th means one gets parked." The rabbit-hole guard exists only as prose ("call out wheel-spinning"); a hard WIP limit is enforceable (end-of-turn check on NOW.md).
7. **Cost guard per task.** Fan-outs (4 design agents, reels, Readthroughs) have no budget. "Any step that spawns ≥3 agents or renders media states its rough cost first" — cheap PreToolUse reminder on Agent/Workflow.
8. **Tyler parity check.** Rules exported to Tyler aren't tested on Tyler's machine (hard-coded `~/.hammerspoon`, `do.test`, Matt's scripts). A rule: "anything in setup/core.md or exported must work without Matt's Mac", verified by `export_setup.py` (grep for Matt-only paths).
9. **Plain conflict resolution order.** When rules clash: safety > Matt's latest explicit words > freeze > everything else. One line saves many wrong guesses.

## 8. Hook suitability, rule by rule (compact)

- **Hard block (PreToolUse deny):** secrets read; `rm` outside scratch; synthetic input without a grant; `hs.reload` via hs; npm/pnpm/yarn; `gh repo create` without `--private`; push to crossword `main`; `/tmp` writes; git init in `~`; browser pane on local media without `?mute` (exists); long foreground commands (exists); thread send at 250k (exists).
- **Just-in-time reminder (inject the topic file when a trigger fires):** UI/design pack (palette, light+dark, no stock look, orphans, icons, press feedback, show options) on UI file edits or `pages new`; school-integrity on course paths/Canvas; HUD slots + tweaks on Hammerspoon/hud-kit edits; music/Apple Music on music asks; reminders/habits when to-do language appears; Slub check-before-building on new project folders; existing-tools-first on new project creation; coordinator routing only in the coordinator session; cloud/project-thread rules only in those surfaces.
- **End-of-turn check (Stop hook):** uncommitted changes in touched repos; edits without a test run; new project without a NOW.md line; reply over ~150 words with no detail request; approvals offered without an `Actions:` line; Hammerspoon edited without reload; details file (if kept) generated here rather than by hand.
- **Stays judgment (keep short, always loaded):** every-word-costs-Matt (shrunk), clarity over brevity, restate truly complex logic, obvious wants just do it, ideas with honest take, ask questions in plain text, make it live by default, systems over one-offs, look for existing tools, model by pace, shared modules, never act as someone else.

## 9. Concrete proposal (for the merge thread)

1. Always-loaded core ≤ 60 lines: the judgment list above + the 8 Slub core rules + conflict order.
2. Topic packs loaded just-in-time: `ui`, `mac-automation`, `school`, `music`, `coordinator`, `cloud-threads`, `personal-workflow`.
3. Hard blocks and Stop checks as listed in §8; delete their prose once each hook is tested.
4. Delete/shelf: progressive disclosure, span-only, thread.md, agent logs, project board, gemini_only, subagent_leaf, ios.md, emoji rules (Code tab), legacy Projects routing (move to coordinator doc).
5. Replace the per-reply details/Readthrough ritual with an automatic end-of-session details file.
6. Add the missing rules 1–9 in §7, starting with the budget and the expiry date, since they stop the set from regrowing.
