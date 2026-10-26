# Slub call transcripts and tasks (2026-10-26)

## 16:50 Calls saved to slub-hq, action items become tasks

Matt asked for Slub call transcripts to be saved into the slub-hq repo, and for each brother's Claude to act on what the other asked of him.

---

### Saved when the call ends

`call-transcript stop` (ai-os `scripts/call-transcript`, installed copy in `~/.local/share/call-transcript/`) now runs `slub-hq/calls/save.sh` in the background for any transcript named `*-tyler.md`. That script copies the transcript to `slub-hq/calls/`, commits and pushes. The FaceTime watcher already calls `stop` when a call ends, so nothing in Hammerspoon changed (avoids clashing with the FaceTime recording prompt thread). Log: `~/calls/.slub-save.log`.

---

### Tasks per brother

After saving, `save.sh` runs Claude Code headless (Sonnet, edits limited to the repo plus git) with "follow CALLS.md". `CALLS.md` is the model-neutral recipe: read lines newer than the notes file's `extracted-through:` marker, put each action item under `## Matt` or `## Tyler` in `TASKS.md` (who has to do it, who asked, time, source), write a short Slub-only summary in `calls/YYYY-MM-DD-notes.md`, commit and push. Re-running is safe; only new lines are read.

---

### Works for Tyler from the repo alone

Rules 7 and 8 in `AGENTS.md` / `CLAUDE.md`: every agent reads its own human's section of `TASKS.md` at session start, offers to do the open ones and ticks them off; and if a transcript in `calls/` hasn't been processed, it does the extraction itself. So Tyler's Claude needs only `git pull`, no install.

---

### Privacy decision

The raw transcript is committed as-is: both brothers were on the call and the repo is private to them. Notes and tasks are Slub-only (no health, relationships, outside money or other people's business). Rejected: filtering the raw transcript with an LLM (loses fidelity). If Matt wants raw transcripts kept off the repo, `save.sh` can commit only the notes.

---

### Tested

Ran on today's live call: 10 tasks (5 Matt, 5 Tyler) and a notes file were pushed. Not yet tested end to end through a real call hang-up. Known gap: a task done during the call (the Slub work calendar events) can still be listed; a later pass won't untick it.

Undo: remove the `slub` block from `call-transcript` stop; delete rules 7-8.
