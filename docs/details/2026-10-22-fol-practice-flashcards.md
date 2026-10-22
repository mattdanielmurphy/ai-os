# FOL practice page → flashcards (2026-10-22)

## 14:10 Practice page now uses the check-in flashcards

Matt's screenshot: the habit gate's "FOL Five" page was a plain "show answer" list, not the tap-to-pick flashcards from the morning check-in.

---

### Root cause found

`services/checkin/habit_gate.py` (`held_context`) told the agent to *hand-write* an artifact with "each answer hidden until he taps to reveal it". Nothing pointed it at the check-in's card UI, so each agent improvised a page.

---

### Practice mode added

- `template.html` (the check-in page) gained a practice mode (`DATA.mode == "practice"`): steps are just Practice → Done, title from data, optional symbol `key` under the prompt, one "Next" button instead of the FSRS Again/Hard/Good/Easy ratings (practice cards aren't in his deck), taps saved to db `practice/<date>` instead of `checkins/<date>`. The Done screen tells him to reply 👍 in the thread.
- New `services/checkin/practice.py CARDS.json` builds the page from that template. Same options/correct_index shape as the deck cards; options are shuffled on the page.
- The gate's instruction now says: write the questions as JSON to `data/practice/<date>.json`, run practice.py, publish with `{"db": {}}`, never hand-write the page.
- Also fixed in passing: `go()` now hides every `section.step`, and the template declares `<meta charset="utf-8">` (local previews showed mojibake).
- Rejected: copying the card JS into a second template (two copies would drift); AskUserQuestion menus (don't work as a page).

---

### Today's page regenerated

Same five questions, now multiple choice with 3 plausible wrong options each, republished to the same link: https://claude.ai/artifact/KbgoxmBsydpVAAgcQaery4

Tested locally: practice page answers, reveals, Next, Done summary; morning check-in still starts on Breathe with all four steps. Unit tests (habit_gate, daily, ladder) pass. Not tested: db saving on the published page (no taps yet).

Undo: `git revert` the commit; the old static page is version 1 of the artifact.
