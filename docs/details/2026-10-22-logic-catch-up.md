# Logic catch-up + lunch-then-study habit (2026-10-22)

## 09:40 What you missed, FOL flashcards, afternoon study habit

Matt asked (via coordinator): he's badly behind in PHIL 120 Symbolic Logic, missed the last two classes, wants accountability, a new afternoon "lunch then study" habit starting really small and ramping slowly, and today's block is logic only. Flashcards work for him because he answers before he can talk himself out of it.

---

### What you missed

From the syllabus schedule (`~/Documents/School/Symbolic Logic/PHIL120 F26 X1 Course syllabus.pdf`): Oct 14 and Oct 21 were both Unit 5, FOL language and syntax, forall x Part V, ch. 23–29 (building blocks, one quantifier, multiple generality, identity, sentences of FOL, definite descriptions, ambiguity). So the missed classes are the whole of Unit 5. Homework due Oct 21 was ch. 25 sets A–E. No graded work missed (grade = 2 midterms + final). Midterm 2 is Wed Nov 4, 18:00 (30%), 13 days away. Unit 6 (FOL semantics) starts Oct 28.

Existing plan from Oct 20: `~/Documents/School/Symbolic Logic/Unit 5/catch-up.md` (quiz-first, ~3–4 h total). Still valid; it's the source for today's quiz.

Canvas wasn't checked: the built-in browser pane is signed out of Canvas now. The syllabus was enough to know what was covered.

---

### FOL flashcards added

The morning check-in's logic deck stopped at ch. 15, so it couldn't drill anything he missed. Added 16 multiple-choice cards for ch. 23–29 (`services/assistant/spaced_repetition/decks/forallx_intro_formal_logic_ch23-29.json`), imported into the FSRS deck (`~/.hermes/assistant.db`) as new cards, due now. They'll start showing up in tomorrow's morning page (mixed with CMPUT and World Music by exam urgency; logic's Nov 4 exam gets more slots from Oct 28).

Content is standard forall x conventions (all → →, some → ∧, quantifier order, identity for "at least two" / "exactly one" / "except", free vs bound variables, Russell's descriptions, scope ambiguity). Written by me, not copied from the book; checked against the chapter titles. Not cross-checked line by line against the textbook's notation.

Undo: `sqlite3 ~/.hermes/assistant.db "delete from fsrs_cards where card_id between 'forallx_ch23' and 'forallx_ch29_zz'"` and remove the JSON.

---

### Lunch-then-study habit

Reused the morning check-in habit ladder (`services/checkin/ladder.py` + `ladder.json`), same as the SUB thread proposed for SUB study, instead of a new tracker or calendar events.

- New habit `study`, label "Lunch, then study", minutes: 15 → 20 → 25 → 30 → 40 → 50 → 60. Starts at 15 today.
- Weekdays only (`days: [0..4]`). Weekends never count for or against it.
- Grows on its own weekly clock (`own_track`): one step after a week of hitting the dose every scheduled day. So +5 min a week at best: 30 min by mid-November, 60 by late December. Without its own clock it would have waited ~10 weeks behind breaths/gratitude/etc. for the shared one-change-per-week slot.
- Pull back: two school days in a row under the dose steps it down one level; a missed morning check-in undoes its last step (existing ladder rules).
- It's not on the morning page (`when: afternoon`). Instead the morning talk thread gets a line: today's dose, and asks once how yesterday's block went (minutes) and records it. If it's already recorded (e.g. from a thread), it just mentions it.
- Today: one Apple Reminder at 14:15 (after CMPUT lab ends 13:50) for the first block. One-off, not recurring, so it isn't a nagging habit reminder.

Shared pieces the SUB thread can use: `days` and `own_track` are generic ladder options now. Whether SUB study should be the same habit as this one is Matt's call (asked in the reply).

Rejected: calendar blocks (his rule: habits off the calendar), a recurring reminder (nagging), a bigger first dose (he said start really small; the catch-up hours come from the flashcards plus optional extra time).

Tests: `test_ladder` + `test_daily` pass (18), with new tests for weekday-only scheduling, own-track growth and easing after two skipped days. Smoke-tested tomorrow's plan on a copy of the live data.

Undo: revert the commit; the `study` entries in `data/state.json` and `history.jsonl` are harmless if left.

---

### Today's block

After lab and lunch, ~14:15: read forall x ch. 23 (p. 190) for 15 minutes, then say "done" in this thread for a 4-question tap quiz (ch. 23–25 basics from catch-up.md). CMPUT Quiz 2 still closes at 20:00.
