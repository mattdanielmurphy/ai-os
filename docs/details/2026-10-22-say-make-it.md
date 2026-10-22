# Why agents said "say 'make it'"

## 09:55 Cause and fix

**Asked:** why agents write "say 'make it'" instead of "👍 = make it".

---

### Cause coordinator wording

A coordinator brief for an idea thread said "don't build until Matt says 'make it'". The agent copied that phrase to Matt. The same wording sat in IDEAS.md statuses and several details files, so agents kept seeing it. No written rule said "make it" had to be typed; it was a brief convention.

---

### Fix rule text

- Commit b066f944 (from the habit-reward thread) already changed the emoji rule to "Ask for approval as 'Reply 👍 to <action>', never 'say <phrase>'" and fixed IDEAS.md. It was pushed to origin/main but the main checkout on the Mac was behind; fast-forwarded it (kept the uncommitted policy_reminders.md edit by re-applying it).
- Added rule 1f "Ideas Wait for a 👍" to `.rules/core_safety.md` (rebuilt CLAUDE.md): record ideas, build nothing, offer "👍 = make it", never write "until he says 'make it'" in briefs.
- Added the same sentence to the "Record Matt's ideas" line in `~/.claude/CLAUDE.md`.
- Left old details/handoff files as history (not loaded as rules).

---

### Threads load it

Project threads on the Mac load `~/.claude/CLAUDE.md` plus the repo's CLAUDE.md; this thread's own context showed the new "Reply 👍" line, so it loads. Coordinator added it to project instructions too.

**Undo:** revert this commit; remove the added sentence from ~/.claude/CLAUDE.md.
