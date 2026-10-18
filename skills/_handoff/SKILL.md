---
name: _handoff
description: Write a lean, chain-linked handoff so work can continue in a fresh thread. Use when Matt types /handoff or /_handoff, says the thread is getting long, or asks to start fresh, save progress or hand off. Links every earlier thread in the chain, summarizes the whole chain, states the current task and what to keep in mind, then gives a one-line paste prompt.
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

## 4. Check, then report

- Read the file back. Every section filled (write "none" if truly empty); next step 1 is concrete;
  parent file exists (`ls`); session ids are real, not guessed.
- Commit only the handoff file and this thread's own work, using the repo's normal commit flow
  (in ai-os: `python3 ~/projects/ai-os/scripts/auto_commit.py -m "<message>" --paths <files>`). List unrelated dirty files instead of committing them.
- Reply in a few bullets: file path and line count, chain seq, and the paste prompt in its own
  code block:

  ```
  Read <absolute path> and continue.
  ```

Then keep working in this thread unless Matt says he's switching.
