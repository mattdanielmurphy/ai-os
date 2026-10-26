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

## 02:55 Speed reel 2 is live (truth tables, chapters 9–15)

Speed 2 · Truth Tables: https://claude.ai/artifact/J17qDAd1PejdMqhhjnZRaN. Reel 1's end now links to it.

---

### What reel 2 covers

Two warm-up throwbacks from reel 1, then: the five characteristic tables in one table, truth-functionality ("because" and "necessarily" aren't), symbolizing vs translating, row counts (2 to the n), filling a table inside out, tautology/contradiction/contingent, equivalence, joint satisfiability, entailment and bad rows, the double turnstile as metalanguage (and its link to the arrow), limits of TFL, shortcuts, and which claims need one row, two rows or the complete table. 19 questions (5 throwbacks) and 5 comeback slots.

---

### School rule check for reel 2

The Part III exercises are mostly "make a truth table for this sentence" or "is this argument valid" on specific A/B/C sentences. None of those sentences or arguments are used; every quiz sentence uses my own letters and shapes, and the one row-evaluation question uses a sentence not in any exercise list. The book's K-questions ("suppose C is a tautology, what about A, B ⊨ C?") are not asked.

---

### Kit change

Small truth tables (`table.tt`) now have a style in the player, tightened on phones so seven columns fit at 360 px (checked with a screenshot, no sideways scroll).

## 03:35 Speed reel 3 is live (natural deduction, chapters 16–22)

Speed 3 · Natural Deduction: https://claude.ai/artifact/8KFVUwnGYh5JQkyAGAVyY2. Reel 2's end now links to it.

---

### What reel 3 covers

This is the part most likely to carry Midterm 2 marks. It covers what a proof is (PR, AS, citing lines), every basic rule with its shape (R, ∧I/∧E, →I/→E, ↔I/↔E, ∨I/∨E, ¬E, ¬I, IP, X), which lines you may cite once a subproof closes, proof strategy (work backwards from the goal's main connective, forwards from what you have, indirect proof when stuck), the five extra rules (DS, MT, DNE, LEM, DeM), the single turnstile, theorems, interderivable and inconsistent, derived rules, and soundness vs completeness. 20 questions (5 throwbacks), 7 comeback slots. Proofs are drawn Fitch-style with the book's vertical lines and underlined assumptions.

The questions are mostly "which rule justifies this line", "which lines can be cited" and "what's the first move", because that's the decision-making that proof questions test, and it can be quizzed without writing whole proofs.

---

### School rule check for reel 3

All mini-proofs use my own sentences (K, W, H, R, S, T). I checked them against every chapter 17–20 exercise list; none match. The reel never gives a full proof of any exercise, and Ask for this reel has an extra line: never write or finish a proof of a textbook exercise, coach with hints and different examples instead.

---

### Kit change

Fitch-style proof tables (`table.pf`) in the player: line numbers, one vertical bar per open subproof, underlined assumptions, muted justifications. Checked on a 360 px phone in light and dark.

---

### Next

Reel 4: a quiz-heavy recap of Part V (first-order logic syntax, chapters 23–29; the four earlier catch-up reels already teach it). Reel 5: Part VI (interpretations and truth in FOL, chapters 30–35), which class reaches on Oct 28 and Midterm 2 likely includes.

## 04:15 Reels 4 and 5 are live; the series is done

---

### Speed 4 · First-Order Logic Recap

https://claude.ai/artifact/7U8hAAFHjT6DteYnPv1xD2. A quiz-first lap of chapters 23–29, since the four catch-up reels already teach them: one reminder, one question, repeated. It covers two-place gap order, the all-arrow and some-and patterns and their traps, negated quantifiers, empty predicates, quantifier order and the shift fallacy, identity ("other than", "only", why counting needs ¬x = y), free vs bound variables and bracket scope, Russell's descriptions with inner vs outer negation, and scope ambiguity. 20 questions. The book's own exercises (apples, Pavel, Hofthor, "glitters") are avoided; counting and "only" are asked conceptually ("what does this part do?") rather than as symbolize-this items, because those exercise answers would be the same shape.

---

### Speed 5 · Interpretations

https://claude.ai/artifact/DrGK2z9wDXSHzbbDyZbf3w. A first look at chapters 30–35, which class starts on Oct 28: extensions and extensionality, ordered pairs, fixed identity, the four parts of an interpretation, truth for atomic, connective and quantified sentences (worked on one small interpretation of my own: Ana, Bo, Cy), validity and the other semantic concepts, satisfaction and expressing relations, counter-interpretations, the one-vs-all table, and reflexive/symmetric/transitive/anti-symmetric relations. 17 questions. The interpretation and the counter-model question are my own, not the chapter 31 or 33 exercise interpretations or arguments; Ask is told not to build interpretations for textbook exercises.

---

### Order and links

Each reel's end links to the next: Speed 1 → 2 → 3 → 4 → 5. Speed 3 (natural deduction) and Speed 5 (interpretations) are the most likely Midterm 2 material.

---

### Untested

Same as before: the real claude.ai viewer on his phone (voice from Artifact files, Ask consent) hasn't been tried. Everything else passed headless tests on every reel.
