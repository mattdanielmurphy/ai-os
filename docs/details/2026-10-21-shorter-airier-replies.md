# Shorter, airier replies (details)

Thread: "Shorter, airier replies rule" in the Everything project. One section per reply, newest last.

## 16:55 The 50-word rule and the first write-up

Date: 2026-10-21. Thread: "Shorter, airier replies rule" in the Everything project.

### What changed

Every agent (Claude in Code and project threads, Gemini, the coordinator) now follows one reply style for anything Matt reads:

- 50 words by default, 100 as a hard cap unless he asks for detail or a full list.
- Line 1 is the answer, or the one thing he has to do.
- One idea per line (about 12 words), point in bold, a blank line between every line, at most 4 items.
- Things he must know (to-dos, decisions he might veto, risks, failures, untested parts) always get a short line in the reply. They never live only in a file.
- When the work had real decisions or detail, the agent first writes a full write-up like this one, then replies with a summary and a link to it. (Superseded at 16:58: every reply now links a details file.)

Saved in:

- `~/projects/ai-os/.rules/core_safety.md`, section "Every Word Costs Matt" (compiled into ai-os `CLAUDE.md`, `LEAF.md` for subagents and `~/.gemini/GEMINI.md` by `scripts/build_rules.py`).
- `~/.claude/CLAUDE.md` under "How Matt likes to work" (short version).
- The Everything project's instructions, "Talking to Matt" section (the coordinator pastes in the text I sent it, since only it can edit them).

### Why it's built this way

**The problem wasn't length alone, it was that nothing got read.** Matt's words: walls of text meant he skipped everything, "rather than the important things at least getting read". So the rule has two halves: cut hard, *and* guarantee that the important lines survive the cut.

**Why a number (50 / 100 words).** "Be concise" was already in the rules, and agents still sent ~150-word replies, because every agent thinks its own reply is concise. A word count is something an agent can check before sending. The old rule actually said "~150-200 words", which explains why replies were that long; that line now points to the new rule.

**Why blank lines between every line.** Matt asked for visual whitespace. In markdown, a blank line between bullets also makes them render with more space. A line on its own is far less scary than a block.

**Why bold the point.** Already a rule. It means he can read only the bold and still get the answer.

**Why a cut list.** I read recent replies in this project (dropped keys, Cmd-K guard, nightly restart). They weren't badly written; each bullet just carried 2-3 sentences of how-it-works, caveats, file paths and commit hashes. The cut list names exactly those things.

**Why two layers (reply + write-up).** Matt is happy for agents to make lots of decisions, but wants to be able to dig into why. Putting the full reasoning in a file keeps it findable without making him read it to get the gist. The file goes in `docs/writeups/` of whatever repo the work happened in, so it sits next to the code and is committed with it. Work with no repo uses `~/projects/ai-os/docs/writeups/`.

**Why "decisions he'd plausibly veto" go in the reply.** If an agent decides something he'd disagree with, he needs to see it without opening a file. Routine decisions stay in the write-up.

**Why honesty is protected.** The existing "report results honestly" rule could clash with a word budget. Failures and untested parts are explicitly exempt from cutting: one short line each.

### What I rejected

- **A hard character limit enforced by a hook, right away.** Possible (a check that bounces any thread reply over 100 words), but a hook would also block a long reply he asked for. I offered it as a follow-up instead of switching it on.
- **Folding detail into `<details>` blocks.** The old progressive-disclosure rule asked for this, but neither the Code tab nor project threads render HTML; it shows as raw text.
- **Keeping the 150-200 word guideline.** That's the length he called a wall.

### What's untested or uncertain

- Whether every agent actually follows it. Rules get ignored sometimes; the word-count guard would make it mechanical.
- Codex's rules file (`~/.codex/AGENTS.md`) is built without `core_safety.md`, so Codex doesn't get this rule. That was already true of the old reply-length rule.

### How to undo or change it

- Edit the "Every Word Costs Matt" section in `.rules/core_safety.md`, run `python3 scripts/build_rules.py`, commit and push.
- Edit the matching bullets in `~/.claude/CLAUDE.md`.
- Ask the coordinator to change the project instructions' "Talking to Matt" section.

## 16:58 Every reply links a details file

### What Matt asked

He edited his message to add: every reply should link a "more details" md file, the expanded version, so he can do an autopsy (why did the agent do this, what was it thinking, what did it do) or just dig into an exchange.

### What I did

- Replaced the "write-up only for big work" layer with: every reply has a details file behind it, and the reply's last line links it.
- Moved this file from `docs/writeups/2026-10-21-every-word-costs-matt.md` to `docs/details/2026-10-21-shorter-airier-replies.md` and gave it one section per reply. This section is the first one written in the new format.
- Updated `.rules/core_safety.md`, ran `build_rules.py`, updated `~/.claude/CLAUDE.md`, and sent the coordinator new "Talking to Matt" text.

### Decisions and why

- **One file per thread, one section per reply, not one file per reply.** A file per reply would mean dozens of tiny files a day, and an autopsy would mean opening many of them. One chronological file per thread reads like a lab notebook: the whole story of a thread in one place, and each reply links straight to its own section with a `#heading` anchor.
- **All details files in one folder (`~/projects/ai-os/docs/details/`), not in each repo.** Threads often touch several repos or none. One folder is one place to look and one place to search. The earlier version put write-ups in each repo's `docs/writeups/`; I dropped that so there's only one system.
- **Write the section before sending the reply.** The point of an autopsy is what the agent was thinking at the time. Written afterwards, it turns into a cleaned-up story.
- **Commit and push it.** So it survives and shows up on GitHub, and other agents can read it.
- **Only pure acknowledgements skip it.** Matt said every reply; a reaction or "on it" has nothing to expand.
- **Cloud sessions without his Mac write to `/mnt/project-files/details/`.** They can't reach ai-os on his Mac.

### Rejected

- **A file per reply** (too many files; see above).
- **Auto-generating the details from the transcript afterwards.** Possible later (QMD already exports Claude transcripts), but the transcript is long and noisy; a deliberate summary of the reasoning is what he asked for.

### Untested or uncertain

- Whether a `#section` anchor opens at the right spot for a Mac file path in the project UI. Anchors are documented for `/mnt/project-files` paths; for a file attached from the Mac it may just open the top.
- Cost: every reply now has an extra write. Small, but agents may skip it under pressure; a check (hook) could enforce it later.

### Undo

Edit the "Every reply has a details file behind it" bullet in `.rules/core_safety.md` (then `build_rules.py`) and the matching bullet in `~/.claude/CLAUDE.md`.
