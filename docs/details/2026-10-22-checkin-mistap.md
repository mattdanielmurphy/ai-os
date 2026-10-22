# Morning check-in: mistap button (2026-10-22)

## 08:50 Mistap button on the flashcards

Asked (via coordinator): a way to say "mistap" and discard that answer's result so it isn't recorded.

---

### Mistap button added

The flashcards live on the check-in page (`services/checkin/template.html`), not in `daily.py`, so the change is there.
After he taps an answer, under the Again/Hard/Good/Easy row there is now a small underlined link:
"Mistap · don't count this card". Tapping it:
- drops any review for that card from `state.reviews` and adds the card id to a new `state.skipped` list (saved to the page db);
- moves to the next card ("Not counted. Next card…").

---

### Nothing gets recorded

`daily.py` only reads `reviews` when ingesting, so a skipped card: no FSRS rating, not in the ladder's card count, not
in "X of Y correct". It stays due, so it comes back on a later day. A test covers that `skipped` doesn't count.

Decisions: skip the card rather than re-ask it (the answer was already revealed, so a re-ask would be a giveaway).
Rejected: an undo for a mistapped *rating* (ratings auto-advance after 0.9s); add later if he hits that.

---

### Live from tomorrow

The daily 7:45 job rebuilds the page from the template, so tomorrow's page has it. Today's already-published page
is unchanged. Tested: unit tests pass; browser test of the built page (mistap skips the card, nothing in reviews,
due tally drops). Undo: revert the commit.
