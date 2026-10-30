# C · Evidence: which rules actually break (2026-10-29)

Angle C of the rules→hooks study. Analysis only; no rule was changed.

## Method
- 521 Claude Code transcripts modified in the last 10 days (`~/.claude/projects/*/*.jsonl`), 2,149 turn-ends (an assistant text followed by a real user message). Scripts: counters over tool calls and reply text (regex, so counts are approximate; precision noted per row).
- Matt's corrections: user messages under 1,500 chars matching again / rule / never / always / should have / why did you / you didn't (129 hits, ~60 real corrections after removing pasted agent messages).
- Incident "Why:" lines in `.rules/` (each one is a past break that produced a rule), plus today's coordinator incidents named in the brief.
- Not covered: Claude Projects (Everything) threads that ran in the cloud, voice calls, and anything that never reached a transcript on this Mac.

## Ranked by cost to Matt

Cost = how often × how much of Matt's attention or trust each one burns (a wall of text he skips costs less per hit than a lost handoff he only discovers hours later).

| # | Rule broken | Count (10 days) | Trigger moment | Role | Hook that catches it then |
|---|---|---|---|---|---|
| 1 | **Don't wait for OKs you don't need** (Always push / Make it live / Obvious wants: just do it) | 134 turn-ends ask "want me to / should I / reply 👍" (~half are legitimate forks); Matt's explicit complaints: 3+ ("Why wait for my OK? … START", 10-30 02:32; "Why did you stop?", 10-30 00:42; the Google Docs userscript reply "reply 👍 and I'll commit and push") | End of turn, after work is done and tested; worst on commit/push and "build the obvious next step" | Workers mostly; coordinators when forwarding | **Stop hook**: scan the final reply for permission phrases + check `git status` dirty / unpushed commits; block the stop with "commit and push, or name the real fork" |
| 2 | **Thread hand-offs and messages that get lost or overload a thread** (thread-size, routing, bot fallback) | 322 SendMessage calls, 110 start_session; zero size checks before 10-29 (hook added today). Incidents: Slub Bot didn't answer when the Mac was offline (10-30 00:28); coordinator assumed a memory note = global rule (10-29 04:23); 30-thread cap retried 7× (10-27) | SendMessage / start_session from a coordinator; agent-to-agent hand-back | Coordinator, project coordinators | **PreToolUse on SendMessage/start_session** (now live: `thread_size_guard.py`); add: deny a "rule saved" claim unless `.rules/` changed (PostToolUse on Write to memory dir → remind) |
| 3 | **Every word costs Matt** (≤ 100 words, line 1 = answer) | 604 of 2,149 turn-ends are over 150 words (28%) — includes worker→coordinator reports, so maybe ~15% reach Matt | Final reply after a long build or investigation | All, worst in workers reporting results | **Stop hook**: word-count the last reply; over 150 → block once with "trim to ≤100 words, move the rest to the details file" |
| 4 | **Action bar labels must be clear verb + object, only agent actions** | 195 replies had Actions lines; Matt's complaint 10-30 01:31 ("buttons… just a pattern it found") | Final reply that offers choices | All | **Stop hook**: parse `Actions:` line; reject labels < 2 words, bare numbers, or labels with "you/Matt" steps |
| 5 | **Details file + link on every reply** | 1,484 of 2,149 turn-ends (69%) over 40 words had no `Details:` line | Final reply | All (rule is near-universally ignored) | **Stop hook**: require `Details:` line when reply > 40 words; or drop the rule (B-audit's call) — the evidence says it's not happening |
| 6 | **Screen/input clearance (claude-control)** | 187 `open`/`osascript` commands with no clearance in the same call (upper bound; many are read-only `osascript` queries or `open -g` background launches); 31 computer-use / Chrome input calls. Past incidents: Finder reveal without banner; test script moved the mouse after "unreachable" | Testing own builds (launching .app, revealing files), VS Code `.env` opens | Workers | **PreToolUse on Bash** matching `^open\b|osascript .*(activate|keystroke|click)` and on computer-use tools: deny unless a granted ticket exists for this session |
| 7 | **Quiz menus multiSelect: true** | 84 of 142 quiz questions (59%) single-select | AskUserQuestion during study | Workers (school threads) | **PreToolUse on AskUserQuestion**: deny if any question has multiSelect false |
| 8 | **Never rm outside tmp/cache** | 34 rm commands outside obvious tmp paths (most are test-output files and VPS cleanup; no data loss found) | Cleanup after tests | Workers | **PreToolUse on Bash**: deny `rm` unless the path matches tmp/cache/node_modules/scratch/worktrees |
| 9 | **Secrets: never touch .env directly** | 96 commands mention `.env` (nearly all are writing code that loads env vars or `open -a VS Code .env`, which is allowed); no raw reads found | Writing server code | Workers | Existing preflight secret gate is enough; **PreToolUse** deny only `cat/head/grep` on `.env*` |
| 10 | **System /tmp, npm instead of bun** | 14 and 7 | Ad-hoc test scripts | Workers | **PreToolUse on Bash**: deny `/tmp/` (not `/private/tmp/claude`), `npm|npx|pnpm|yarn` |

## Repeat failures from Matt's corrections (not countable by regex)
- **No link given / can't open the thing** (10-17 "you never gave me a clickable link", 10-17 landing pages, 10-24 missing details file + run command). Trigger: final reply naming a file/service. Hook: Stop hook flags file paths or service names not inside a markdown link.
- **Restating / repeating already-said text in voice mode, giant UI text, missing loading states** — product feedback, not rule breaks; skip.
- **Agent stops mid-task** ("Why did you stop?") — same family as #1; Stop hook with a "work still pending?" check (open todos, dirty tree).
- **Project coordinators don't know how global rules work** (10-29 04:23) — onboarding gap; SessionStart hook for coordinator sessions that injects the "rules go in `.rules/` + build_rules.py" line.

## What this says for the merge
- The highest-cost breaks (#1, #2, #3, #4, #5) all happen at **one moment: the end of a turn**. One Stop hook that checks the final reply (permission phrases, word count, Actions labels, Details line, unlinked paths) and the repo state (dirty/unpushed) covers most of the pain.
- The second cluster is **PreToolUse guards on Bash/SendMessage/AskUserQuestion** — cheap, deterministic, low false-positive if the regexes are tight.
- Rules nobody follows at all (Details on every reply: 69% miss) should be either enforced by hook or deleted; keeping them as text only adds weight.

## Caveats
- Counts are regex-based; "asks permission" and "open without clearance" are upper bounds. Word counts include agent-to-agent reports Matt never reads.
- The 10-day window starts 10-19; rules added mid-window (Actions bar 10-27, clear labels 10-29) are judged only from their start date in spirit, not in the counts.
