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

## 14:25 Symbol key one item per line

Matt (in another thread): write the key `UD: animals · Dx: … · Bx: …` with newlines instead of "·" separators.

---

### Key on separate lines

`practice.py` now splits every key on "·", ";" or newlines (or takes a list) and shows one item per line; the template already uses `white-space: pre-line`. Done in the builder, not left to the agent, so every future gate page gets it. The gate's instruction now asks for the key as a list. Today's page is republished (same link); question 2's key also got its missing meanings (Sx: x is a student, Px: x is a professor). Tests pass.

---

### Saving check

The coordinator saw no `practice` rows while Matt was mid-quiz; I confirmed the collection is empty. The same save code works on the morning check-in (rows for Oct 17–21), so the code path is fine; the likely cause is taps made before the page's db connection arrived (save() silently skipped them), or a view of version 1 (static, no db). Fix in `template.html`: when the db connects and there's no saved doc yet, it saves the taps already made; in practice mode, a view with no db now says "Answers aren't being saved in this view." I couldn't open the live page myself (the built-in browser isn't signed in to claude.ai), so this is untested live. Not republished yet, so Matt's quiz isn't interrupted mid-way; it applies to every gate page built from now on.

---

## 14:45 A better way than "reply 👍"

Matt asked if there's a better way than going back to the thread to reply 👍.

---

### Done button wakes thread

Yes. The review page (`services/review`) already does this: its Done button links to the Mac connector's `/act/<token>/review-done` route (`services/mac-connector/server.ts`), which queues a note the coordinator routes to the thread. The practice page's Done screen could use the same route with a `practice-done` action that runs `habit_gate.py done` on the Mac and wakes the thread, so the held message carries on without him typing. Not built yet; offered as "👍 = make it". Rejected: having the agent poll the artifact db on his next message (still needs him to send something).
