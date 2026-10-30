# C · Evidence: which rules actually break, when, and what would have caught them

Angle C of the rules→hooks study (redo at xhigh, 2026-10-29). Analysis only: no rule was changed.

## Headline

1. **The costliest breaks happen at two moments: when a coordinator sends work to another thread, and at the end of a turn.** One PreToolUse guard on sends (now live) and one Stop check on the final reply would have caught most of what hurt Matt.
2. **Hooks already work here.** The hang guard blocked 77 risky commands and the input guard blocked 46 unapproved screen grabs. In both cases the forgetting kept happening, but the hook caught it before it reached Matt.
3. **Text rules fail most where they conflict or depend on judgement.** Examples are "ask before building" against "just do it", and coordinators that were supposed to remember to check thread size.
4. **Many rules are followed fine and don't need hooks.** Commit and push, bun, secrets and quiz menus (since their rule) all fall in this group.
5. **Some "rule breaks" are really the auto-mode safety check or bugs in the system.** About 16 of the replies asking Matt for an OK were forced by the classifier (13 separate blocks). Permission allow-rules would fix those, not hooks.

## Sources and method

- **Transcripts:** 535 Claude Code transcripts changed 10-19 → 10-30 (`~/.claude/projects/*/*.jsonl`; subagent side-chains excluded), parsed into 50,900 events. Timestamps below are UTC (Matt's evening = next day UTC).
- **Matt's own messages:** 1,551, after removing agent hand-backs, relays, system events, voice tasks and pasted text. Project-thread wake envelopes were unwrapped.
- **Replies Matt saw:** 1,125 visible replies to Matt's own messages: the last assistant text in the Code tab, or the `reply`/`post_message` text in project threads.
- **Roles:** the app's session titles (`claude-code-sessions/*/local_*.json`). Coordinator means `Coordinator…`, project coordinator means `… Coordinator` (Glass TV, Slub), and everything else is a worker.
- **Corrections:** I read 377 messages from Matt that look like corrections, deduped, alongside the agent turn that came before each one. I then reread about 60 rule-relevant ones in full context.
- **Thread size at send time:** for every SendMessage to a `local_` thread, I took the target's context size from its last API usage record before the send.
- **Also used:** `.rules/` "Why:" incident lines, `docs/details/` incident sections, a QMD `claude-threads` cross-check and the guard-denial messages in tool results.
- **Not covered:** cloud-only sessions, voice calls, Claude Projects (Everything) threads before 10-28 that ran off this Mac, and replies to agent-triggered turns. The Slub Coordinator's "Delete / Admin first" buttons were one of those.
- Scripts are in `docs/rules-hooks/c-scripts/` so the merge thread can rerun them.

## Ranked by cost to Matt

Cost = how often it happens × how much it costs him (tokens, time spent diagnosing, trust, real-world stakes).

| # | Rule broken | Evidence (10 days) | Trigger moment | Role | Hook that catches it then |
|---|---|---|---|---|---|
| 1 | **Thread size: never send work into a thread at 250k+** | 32 coordinator sends went into 7 threads already at 250k–399k (10-28 08:11 → 10-30 02:25). Coordinators made at most ~20 size lookups in 163 sends. Matt blew up twice (10-29 02:40, 10-30 02:29). | `SendMessage` to a `local_` thread, usually a quick follow-up into a busy worker | Project coordinator (Glass TV: 20), coordinator (12) | **PreToolUse on SendMessage**: `thread_size_guard.py`, **live since 10-30 02:33 UTC**. It denied a 274k send during its own test. |
| 2 | **Don't wait for OKs you don't need** (Always push · Make it live · Obvious wants · Close threads without asking) | 165 visible replies (15%) end by asking for a go-ahead. 21 asked to commit, merge or go live, 15 of them before the 10-20 rules. Coordinators: 42 of 197 replies end in a choice, and about 7 were plain wants (fix a bug Matt just reported, start the hooks thread). Matt objected **6 times**: 10-19, 10-20 (×2 → rules), 10-22 ("👍 again"), 10-22 ("when I OBVIOUSLY want something"), 10-26 ("don't ask me"), 10-30 ("Why wait for my OK?"). | End of turn, after the work is done or the bug is diagnosed | All; coordinators on "start a thread to fix X" | **Stop hook**: when the reply's last lines ask for an OK, block once if the ask is about commit, push, merge, go-live, closing a thread, or starting a thread for a bug Matt reported. Make it say "do it, or name the real fork". Pair it with **permission allow-rules** for push and merge to main (see "Not rule breaks"). |
| 3 | **School work: never write graded work** | 1 incident (10-23 20:46). Asked to "clean up comments, then copy to c2", the agent removed a helper, filled in a docstring, restored `input()` and **added a missing `print(keystream)`** in `CMPUT 174/labs/lab_4…/cipher1.py`. Matt: "if AI is used in the writing of the code I can get fucking expelled". | `Write`/`python3 -` edit to a file under `~/Documents/School/` | Worker | **PreToolUse on Edit/Write/Bash** whose path is under `~/Documents/School/` (or a course name): inject the school rule. **PostToolUse**: diff code tokens (AST/strip comments) and block if anything besides comments, whitespace or line order changed. Rare, but the worst outcome of anything here. |
| 4 | **Handoffs and rules that depend on someone remembering to read them** | 10-30: a Slub Bot task **never arrived**. The bot filed it under "Done" in an inbox the Coordinator read only at session start, and the pointer named an old coordinator. 10-29: the Glass TV Coordinator saved "no messages to cold threads" to **its own project memory**, which contradicts the global 250k rule. Matt had to untangle it ("I don't understand why you would make such a recommendation"). Of 22 sessions that saved feedback memories, 10 never touched `.rules/` (mostly project-specific, so fine; 1–2 were global). | Inbox file written by a bot; `Write` to `…/memory/*.md` | Project coordinator; bot | **Deterministic delivery**: a watcher that forwards inbox lines straight to the live coordinator (built 10-30, untested end to end). **PostToolUse on Write to `*/memory/*.md`** with `type: feedback` and always/never wording outside ai-os: add context "if this isn't project-only, send it to the Coordinator for `.rules/`". |
| 5 | **Every word costs Matt** (length and clarity) | Code-tab worker replies: median 139 words, **47% over 150**. Project-thread workers: median 85, 20% over 150. Coordinators: median 67, **4% over 150** (the rule works there). From 10-22 to 10-25, 23 replies used the "**You:** …" shorthand, which Matt called confusing on 10-25 (rule changed). About 7 times Matt said he didn't understand a reply (10-22, 10-23, 10-24, 10-29 ×2). | Final reply after a long build or investigation | Workers in the Code tab | **Stop hook**: over 150 words → block once with "trim to ≤100, put the rest in the details file". Flag `^**You:` / `^You:` prefixes. Clarity itself stays judgement. |
| 6 | **Action-bar buttons: verb + object, only things the agent does** (rule 10-27, tightened 10-30) | 66 buttons in 38 replies since 10-27. **8 one-word labels** (Here, Later ×2, Skip, Sent, Restart, Works, Wait). **About 7 buttons were steps only Matt can do** ("When you're at the Mac, type 'start it'", "I'll turn on apps-only mode", "I'll @mention the bot", "I've messaged the bot", "I'll restart it myself", "I'll send Tyler the prompt"). Matt complained on 10-30 01:31 about "Delete / Admin first". | Final reply that offers choices | Project coordinators mostly | **Stop hook** (fully mechanical): parse `**Actions:**`, block labels under 2 words, and block sentences that start with "I'll / I've / I " (Matt's own step) unless they ask the agent to help. |
| 7 | **Do it yourself instead of handing Matt steps** ("No API? Drive the web app yourself", 10-25) | 4 complaints: 10-22 Apple Music ("is there NO way for you to add them"), 10-25 Linear states (→ rule), 10-27 Warp settings ("Are you sure you can't add that for me"), 10-29 adb install ("Can you just try to do it for me?"). | Final reply that tells Matt to run or click something | Workers, project coordinator | Only a soft **Stop check**: if the reply gives Matt a terminal command or click path and no tool error explains why, nudge "can you do this yourself?". A judgement call: some steps really need his password or device. |
| 8 | **Link every file, folder, thread and service** | Complaints 10-17 ×2, 10-22 (threads), 10-22 (`open https://…` command instead of a link), 10-23 (→ file-link rule), 10-24 (nonexistent details file, no folder link or run command). **None since 10-24.** 110 visible replies still contain a bare `~/…` or `/Users/matt/…` path. | Final reply | All | **Stop hook** (regex): bare home paths outside links or code blocks, `open https?://`, and linked `.md` files that don't exist on disk. |

## Hooks that already exist, and what they show

| Guard | Live since | Denials in transcripts | What it proves |
|---|---|---|---|
| `bash_timeout_guard.py` (hang guard) | 10-23 | **77** (encodes, playback, foreground `timeout` > 5 min, `sleep` ≥ 60s) | Agents forget this rule constantly. The hook catches it at no cost to Matt, and he hasn't raised hangs again. |
| `input_guard.py` (take-control) | 10-21 | **46** (`open`, `osascript activate`, `hs` focus/eventtap) | The same: frequent forgetting, every case caught. One slip got through on 10-23: a script carried on after its ticket had already ended (see `2026-10-22-generative-ambient.md` "Take-control slip"). The guard only checks a ticket when the command looks like input, so long scripts also need `claude-control state` between steps. |
| `browser_pane_guard.py` | 10-23 | 5 (local and media pages in the pane) | The same pattern. |
| `thread_size_guard.py` | 10-30 02:33 UTC | 1 (its own test, 274k) | Too new to judge. Every oversize send in the table came before it. |

My first pass counted 187 "`open` without clearance". That was wrong: those commands ran because the session already held a ticket or the guard let them through. The 46 denials are the real number of attempts.

## Rules that are mostly followed (low priority for new hooks)

- **Commit and push:** only 3 of 185 sessions that edited repo files never committed. Most "uncommitted" mentions are agents correctly leaving other sessions' files alone.
- **bun not npm:** no real npm/npx/yarn/pnpm runs; all matches were text inside heredocs.
- **Secrets:** no raw `.env` value was printed. About 10 commands piped a value through without printing it (`sed -n 's/^KEY=//p' .env | ssh …`). The riskiest copied a token-bearing URL to the clipboard on 10-21.
- **`/tmp`:** about 10 real uses on the Mac; the rest are `./tmp` or the VPS.
- **`rm` only in scratch:** 41 commands outside obvious scratch paths (build output, VPS test files). No data loss found.
- **Quiz menus:** every quiz question before the 10-21 rule was single-select (36/36). After it, 12/59. The "Option A" descriptions stopped.
- **Public repos:** the one `--public` repo (10-22, mac-utilities) was approved by Matt in his own words.

## Rules that died silently

- **Details line on every reply.** In project threads (10-22 → 10-27) it was followed 60–85% of the time. In the Code tab after the 10-28 migration it dropped to 4 of 138 coordinator replies, and Matt hasn't complained once. Either a hook should write and link it automatically, or the rule should go (B's call).

## Not rule breaks (fix somewhere other than hooks)

- **Asks forced by the auto-mode safety check (about 16 replies, 13 separate blocks).** The classifier blocked push or merge to main (10-23, 10-24), a public repo or open ports (×4, 10-21 → 10-22), starting or reading a test thread (10-18 ×2), giving a bot Mac access, a mouse blocker, editing its own permissions, Telegram deletes, and the 10-28 "go" mod. To Matt these look like "waiting for my OK". Fix: permission allow-rules (`Bash(git push origin main)` etc.) and fewer protected actions, not a Stop hook.
- **Oversized coordinators:** 19 worker reports landed in coordinators at 287k–432k. The cause was the context-alert mod failing to recognise coordinators (fixed 10-29), not an agent choice.
- **Notification spam** (10-28 18:23, 10-29 21:13): product bugs in the call transcriber and context band.
- **Following Matt's own earlier instructions inside a thread** ("You forgot how we do the … two links" 10-19; "Remember when I said … dialogue only" 10-29; "I said I want it UNPINNED" 10-30): memory and recall, not a rule. Already partly served by the QMD recall hook.

## What this means for the merge

- **One Stop hook carries most of the rest:** permission asks, Actions-line lint, word count, bare paths, `open https://`. Each check is cheap and deterministic. Block once per turn, then let the agent stop, so Matt never gets stuck.
- **PreToolUse guards keep working best for tool-shaped rules:** sends (live), school paths (missing), input (live), hangs (live).
- **Fix the conflicts before hooking them.** "Ideas wait for a 👍" and "restate complex logic first" collide with "obvious wants: just do it" and "make it live". A hook can only enforce one side, so the merge needs a single rule for what counts as a real fork.
- **Delivery between agents must not depend on someone reading a file at session start.** Every lost handoff in the data had that shape.
- **Check permissions before blaming agents:** the classifier causes a share of the "why are you asking me" moments.

## What changed from the low-effort pass

- **Corpus.** Before: all 2,149 turn-ends, including agent-to-agent reports. Now: 1,125 replies Matt actually saw, 1,551 of his own messages, and roles from app titles.
- **Thread size.** Before: "322 sends, zero checks". Now: each target's size at send time. 32 coordinator sends went into threads at 250k+, there were at most ~20 size lookups in 163 sends, and the new hook postdates them all. Duplicate sends from compacted transcripts were removed (322 → 196 unique).
- **Screen input.** Before: 187 `open`/`osascript` "without clearance". Wrong: `input_guard.py` has existed since 10-21 and denied 46. Hooks are now shown as working evidence, not breaks.
- **Waiting for OKs.** Before: 134 asks. Now: 165 visible asks, split into commit/live asks (mostly before the 10-20 rule), coordinator plain-want asks, and ~16 forced by the classifier, with Matt's 6 dated complaints.
- **Details line.** Before: "69% missing". Now: followed in project threads, died with the Code-tab migration, zero complaints.
- **Quiz menus.** Before: 59% single-select overall. Now: 100% before the rule, 20% after.
- **Downgraded.** rm (no harm found), secrets (no prints), npm and public repo (false positives or approved).
- **New.** School-work incident (#3), lost Slub handoff and memory-only rule (#4), Actions-button breakdown (#6), do-it-yourself complaints (#7), reply lengths by role, and the "not rule breaks" section.
