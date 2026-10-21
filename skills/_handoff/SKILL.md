---
name: _handoff
description: Write a lean, chain-linked handoff so work can continue in a fresh thread. For a cold thread named from a new one, Haiku writes it from the transcript file. Use when Matt types /handoff or /_handoff, says the thread is getting long, or asks to start fresh, save progress or hand off. Links every earlier thread in the chain, summarizes the whole chain, states the current task and what to keep in mind, then gives a one-line paste prompt.
argument-hint: [optional focus, e.g. "just the mod spike"]
---

# Handoff

Adapted from REMvisual/claude-handoff (MIT, https://github.com/REMvisual/claude-handoff):
kept its chain links, "what we tried" and paste prompt; dropped beads, its 300–800 line
target and multi-pass mining. Matt wants a short brief, not a transcript.

**Guards**
- Only run when Matt asks for a handoff now. If he is only asking what a handoff is, answer instead.
- Never write a freeform handoff without this skill.
- Focus hint from Matt (soft; the conversation is ground truth): $ARGUMENTS

## 0. Another thread named? Check if it's cold

If Matt names a different thread to hand off (a session id, or words like "the qwerty thread"),
don't open or message that thread. A cold thread re-reads its whole context at full price.

1. Find its session id: an id he gave, else
   `grep -l "<distinctive words>" ~/.claude/projects/*/*.jsonl | xargs ls -t | head -5`. If several fit, ask.
2. `python3 ~/projects/ai-os/scripts/cold_handoff.py status <sid>` gives `lastAt` (ms) and `ttlSec`.
   It's cold when now minus `lastAt` is more than `ttlSec`.
3. **Cold:** `python3 ~/projects/ai-os/scripts/cold_handoff.py write <sid>`. Haiku reads the
   transcript file and writes the brief to `docs/handoffs/*-cold.md` in about 20 s. Read it back,
   commit it, and reply with the paste prompt the script printed. Skip steps 1–4 below.
4. **Warm:** tell Matt to run `/_handoff` in that thread now. It still has the whole context
   cached, so it writes a better brief for less.

If /_handoff runs inside the thread that's being handed off, that turn already re-read the
context, so the cache is warm again. Do the normal handoff below. If the gap since the previous
turn was more than an hour, add one line saying that next time he can run `/_handoff <thread>` from a
fresh thread so the old one is never reloaded.

## 1. Gather (one message, parallel Bash)

- `git branch --show-current`, `git status -s | head -30`, `git log --oneline -10` (skip if not a repo).
- `ls -t docs/handoffs/ | head -10` in the project root (`git rev-parse --show-toplevel`), else `~/projects/ai-os/docs/handoffs/`.
- This thread's session id: `echo "$CLAUDE_CODE_SESSION_ID"` (or the UUID in the scratchpad path).
  Don't use the newest `.jsonl`; parallel sessions make that the wrong thread.

## 2. Find the chain

The parent is, in order:
1. The handoff file Matt pasted or named at the start of this thread.
2. A handoff in `docs/handoffs/` from the last few days on clearly the same work. If unsure, ask
   in one plain sentence; default to a new chain.

With a parent: read it in full and carry its **Chain** list forward, adding the parent. No parent: seq 1.

## 3. Write the file

Path: `<project root>/docs/handoffs/YYYY-MM-DD_<2-4-word-slug>.md` (add `_2`, `_3` on collision).
Aim for 60–150 lines. Concrete beats complete: file paths, commands, numbers, exact errors.
Drop anything the next thread won't need; earlier detail lives in the linked threads.

```markdown
# Handoff: <what we're working on> (<YYYY-MM-DD>, seq <N>)

Paste into a new thread: "Read <absolute path to this file> and continue."

## Chain
- Seq <N> of `<chain-slug>`. Parent: `<parent file>` or "none (first in chain)".
- Threads so far (oldest first; reopen with `claude --resume <id>` or `threads.py show <id>`):
  - <date> · <session id> · <one-line topic> · handoff: `<file>`
  - <date> · <this session id> · <topic> · (this handoff)

## Chain summary
3–8 bullets for the WHOLE chain, not just this thread: what has been built or decided so far.
Carry the parent's bullets forward, merged and trimmed.

## This thread
- What got done (files, commits, results with numbers).
- What we tried that didn't work, and why. (Most expensive to rediscover; never skip.)

## Working on now
The current task in 2–4 sentences, and where exactly it stopped.

## Keep in mind
- Matt's corrections and preferences from this chain, in his words where possible.
- Gotchas, decisions and rejected options (with the reason).
- Uncommitted or unpushed work, things still untested.

## Next steps
1. <the single next action, concrete enough to start without asking>
2. ...

## Read first
- 2–5 key files or docs, with why.
```

## 3b. Copy Matt's /_handoff message verbatim (always)

Anything Matt sent with `/_handoff` (his own text, quotes, quote-with-comments, element picks,
images, attached files) must reach the next thread exactly. Never retype or summarise it; run:

```bash
python3 ~/projects/ai-os/scripts/handoff_capture.py --handoff <handoff file>
```

It reads this turn from the transcript (`$CLAUDE_CODE_SESSION_ID`), appends a
"Matt's message with this handoff (verbatim)" section, and saves images and `~/.claude/uploads`
files to `docs/handoffs/<file stem>/`. Commit that folder with the handoff. Still use the message
to shape Working on now / Next steps, but the verbatim section is the source of truth.

## 4. Check, then report

- Read the file back. Every section filled (write "none" if truly empty); next step 1 is concrete;
  parent file exists (`ls`); session ids are real, not guessed.
- The verbatim section is present and its image count matches what Matt attached.
- Commit only the handoff file (plus its `<file stem>/` folder) and this thread's own work, using the repo's normal commit flow
  (in ai-os: `python3 ~/projects/ai-os/scripts/auto_commit.py -m "<message>" --paths <files>`). List unrelated dirty files instead of committing them.
- Reply in a few bullets: file path and line count, chain seq, and the paste prompt in its own
  code block:

  ```
  Read <absolute path> and continue.
  ```

- Then offer the next thread as a linked session card, so Matt can pick the model and it nests
  under this thread: `mcp__ccd_session__start_session` with `initiation: "own_initiative"`,
  `context: "fresh"`, `title` = the handoff title, `prompt` = `Read <absolute path> and continue.`,
  `background` = 2–3 lines from Chain summary (≥80 chars). Don't set `model`; Matt picks it on the card.
  If that tool isn't available (other app, CLI), the paste prompt above is the fallback.

Then keep working in this thread unless Matt says he's switching.
