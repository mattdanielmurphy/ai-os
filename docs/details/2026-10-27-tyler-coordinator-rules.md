# Coordinator rules for Tyler

---

## 17:35 Rebuilt the shareable coordinator block

**Asked:** the coordinator's summary for Tyler's coordinator (built from project memory only) missed the handoff rules. Rebuild it from the real sources, list what it missed, keep it generic, under 16,000 characters, published as a page. Matt then said scripts can be shared, so script-dependent rules are included and marked **[needs: X]**.

**Sources read:** `/mnt/project-files/coordinator/routing-rules.md`, `.rules/core_safety.md` (compiled CLAUDE.md), the project instructions, the `_handoff` skill, `scripts/` (cold_handoff.py, handoff_capture.py, auto_commit.py, readthrough_comments.py), `mods/context-alert`, and the two coordinator posts (main block + handoff addendum).

---

### What the summary missed

- **"Ideas stay ideas until the user says 'build it'"** contradicts rule 1f: offer "👍 = make it", never ask him to type a phrase.
- Cold-thread cost reasoning (warm < fresh < cold), the full warm/cold/long decision table, "warm but long: a one-line tweak can still go there".
- Things that never justify a cold wake (folder prompt, "owns the code", the coordinator's own promise).
- Batching small asks into one fresh thread; held follow-ups (deliver when warm, else fresh thread).
- Brief contents for a fresh thread (what the old one touched); cold_handoff.py for full reasoning.
- The context-alert mod's automatic cold-thread hold (the "auto handoff" Matt described to Tyler on the call).
- _handoff chain links and the verbatim copy of the user's handoff message.
- Routing rules 6-9: start threads on a message that is the task, mirror check, "why did you do that?" = real cause, when unsure new thread.
- /coord, /learn, cautious option until a rule thread answers.
- Thread cleanup without asking, parking ideas in Linear.
- Project instructions stay pointer-only (16k).
- Important things in the reply, never only in a file; "try this" comes with a command; restate tricky logic before building.
- 👍 on any offer = go, never reconfirm; at most one question.
- Make-live: no "want me to undo?" question; always test.
- Details files, Readthroughs, reels, claude-control queue (Esc vs Stop), secret handling.
- No command may hang a thread; model naming/verification; look for existing tools; systems over one-offs; shared modules.

---

### Decisions

- **Model choice section dropped.** "Opus while usage is on pace, Sonnet when over" isn't in any rule file or Mac memory I searched; flagged at the bottom of the page instead of copied.
- **"Never resolve a thread the user hasn't looked at"** replaced with the real rule: close superseded/answer-only threads without asking; only results he must try go in front of him.
- **Left out:** school, health, music, Hue, reminders, colour palette (needs his palette), voice-task reports (needs his voice bridge), puma-dev, VPS database.
- **Public page:** mattmurphy.ca/coordinator-instructions (unlisted). It names Matt's script paths but has no secrets or private life details.
- Paste block is 11,723 characters, under the 16,000 limit.

**Untested:** Tyler hasn't pasted it yet. Scripts still have Matt's hard-coded paths.

**Undo:** delete `docs/shared/coordinator-instructions.md` and the page in `~/projects/pages`.
