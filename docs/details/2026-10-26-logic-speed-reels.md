# Logic speed-review reels (2026-10-26)

## 02:20 Speed reel 1 is live (chapters 1–8)

**What Matt asked (via the coordinator):** a fast read-through of the textbook, starting with Parts I and II, as reels with lots of quizzing: retrieval practice, spaced re-checks of earlier ideas and quick feedback. He got 77 on Midterm 1 and wants to do much better on Midterm 2 (Wed Nov 4). Start him on the earliest material quickly instead of building everything first. School rule: explain, invent examples and practice questions, give hints; never answer assigned work or textbook exercises.

---

### Reel 1 covers Parts I and II

Speed 1 · Arguments and TFL Symbols: https://claude.ai/artifact/WVneBno1UzEMfzY5a1rnpA

It covers forall x: Calgary chapters 1–8 in twelve short sections: arguments and indicator words, validity and soundness, necessary/contingent/equivalent/jointly possible, atomic sentences, the five connectives (with the "but", "not both vs neither", "only if", necessary vs sufficient and "unless" traps), sentences of TFL and the main connective, ambiguity, and use and mention. It has 23 questions: 17 on the section just read and 6 "Throwback" questions on earlier sections, ending with a mixed round.

I read "Parts I and II" literally (chapters 1–8), because that's what the coordinator passed on and it's where the course starts. Midterm 2 most likely covers Units 4–6 (natural deduction, FOL syntax, FOL semantics), so the next reels go Part III (truth tables) → Part IV (natural deduction) → a quiz-heavy recap of Part V → Part VI.

---

### How the quizzing works

New in the reel player (`services/reels/scroll/kit/player.js`), reusable by every reel:

- **Score:** only the first pick on each question counts, shown in a small pill at the top left ("7 / 9 right first try"). After a wrong pick he can keep trying; the explanation shows either way.
- **Comebacks (spaced re-checks):** a question missed on the first pick goes into a queue. Later in the reel there are empty slots; when the reading reaches one, the oldest missed question from an earlier section comes back with its options reshuffled. Getting it right clears it. If nothing is queued, the slot is skipped.
- **Throwbacks:** questions written on purpose about earlier sections, mixed in between new material (interleaving).
- **End review:** the end shows the tally and every question still missed, ready to retry right there.

Why these: retrieval (answering before re-reading), spacing (coming back after a gap) and interleaving (mixing topics) are the three best-supported study methods, and immediate feedback stops a wrong idea from settling. Rejected: a separate flashcard app (more to remember, and he asked for reels), and cross-reel review (each Artifact has its own storage, so reels can't share his misses; each new reel instead opens with throwbacks to earlier ones).

---

### School rule

Every example and question is new. I checked them against the chapter 1–8 exercise lists so none of the book's exercise sentences appear. The Ask button keeps its school mode (explains and hints, never solves textbook or graded work).

---

### Tested and untested

Tested headless (muted Chrome): the reading pauses at each question, a missed question comes back at the next slot and only once, the score counts first picks only (22 of 23 when one was missed), the end review lists everything still missed and clears one when answered right, narration loads, Ask still works with the integrity rules, no sideways scroll on a phone in light and dark, no page errors.

Not tested: the real claude.ai viewer on his phone (as with the earlier reels, audio from Artifact files and the Ask consent prompt haven't been tried there).

---

### How to undo

Delete the artifact, and revert the commit that added quiz mode and `reels/speed-1`.
