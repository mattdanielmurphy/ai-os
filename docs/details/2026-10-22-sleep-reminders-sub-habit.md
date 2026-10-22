# Sleep reminders + SUB habit (2026-10-22)

## 09:15 Stopped bed/wake reminders, SUB habit plan, calendar answer

Matt asked: stop the "go to bed" / "wake up" reminders; set up the SUB study + piano habit patiently, off the calendar; should the calendar hold want-to items too?

---

### Where they came from

`scripts/hue.py retime --reminders` (run 2026-10-20 to ease bedtime 00:30 → 23:00 over 4 nights) added "Bed by …" / "Wake up …" items to Apple Reminders. `hue.py shift` also added them by default.

---

### What I changed

- Marked the 6 open ones done (`apple-reminders complete`), not deleted: they stay in Completed, so it's reversible.
- `hue.py shift` now adds reminders only with `--reminders` (was on by default). `retime` was already opt-in. The lights' gradual shift is unchanged.
- Rule saved in `.rules/core_safety.md` (compiled to CLAUDE.md/GEMINI.md), `~/.claude/CLAUDE.md`, and Claude memory `no-sleep-reminders.md`. Project instructions can only be changed in the app (coordinator).
- Undo: `git revert` this commit; untick the reminders in Reminders > Completed.

---

### SUB habit proposal

Existing system: the morning check-in habit ladder (`services/checkin/ladder.py` + `ladder.json`) already does exactly Matt's habit rules (grow one step per 7 kept days, a missed day undoes the last growth, 2+ missed drop to the floor). Reuse it rather than building a new tracker.

Proposed logic (not built yet; waiting for his 👍 because it's multi-state logic he might read differently):
1. New ladder habit "SUB study", minutes, levels 5 → 10 → 15 → 20 → 30. Starts at 5 min.
2. Campus days only (Mon–Fri per SCHOOL.md). Weekends neither count nor break it. Needs a small `days` option in ladder.py.
3. Piano is a bonus, never required, so a busy piano never counts as a miss.
4. The morning check-in asks one line: "SUB yesterday? minutes" and records it.
5. Not added straight away as active? Option: put it first in `unlock_order` so it unlocks after the existing 14-day streak rule. Rejected as default: he wants to start this one now, just small.

Rejected: Calendar events (he said no), Apple Reminders (nagging, and against the new rule), a separate habit app (the ladder already exists).

---

### Calendar answer

Recommendation: the main calendar holds only fixed commitments (time + place you've committed to: classes, appointments, shifts, ticketed shows). Want-to events with a real time (a concert, a jam) go on a separate "Maybe" calendar he can hide. Habits and flexible intentions never go on a calendar; they live in the ladder. Why: if the calendar mixes must and maybe, he stops trusting it and misses the musts.

## 09:45 SUB habit built (merged into lunch-then-study)

Matt 👍'd the SUB plan. Meanwhile the "Logic catch-up and study block" thread had added a weekday "Lunch, then study" ladder habit (15 min start). Two study habits at once would break "very patient", so I merged them (default; that thread's merge question was unanswered).

---

### Merged into one habit

- Label is now "Lunch, then study in SUB" (`services/checkin/ladder.json`).
- Levels now 5 → 10 → 15 → 20 → 25 → 30 min (was 15 → 60), matching the approved 5-min start and his 30-min goal. Tomorrow's dose: 5 min. Today's 15-min logic block from the other thread is unchanged.
- Growth/pull-back reuse that thread's weekday + own-track logic: +1 step per full kept week, eases after skips.
- Morning check-in line (`daily.py study_line`) now says "in SUB" and that the public piano after is a bonus, never required.
- Tests updated for the new label/start dose; all 18 pass.
- Undo: separate them by reverting this commit and adding a new `sub` habit with `days` + `own_track`.
