---
name: _quiz-with-tap-menus
description: Quiz Matt with multiple-choice questions he answers by tapping, using the built-in question-menu tool (AskUserQuestion), so his answers come back to you. Use whenever Matt asks to be quizzed, to study, for practice questions or flashcards in chat, or says "quiz me".
argument-hint: [topic or course, optional]
---

# Quiz with tap menus

Matt studies best with short tap-to-answer rounds and instant feedback. This is the exact
format he settled on (World Music midterm, 2026-10-20). Reuse it as is.

## The menu
- **Use the built-in question-menu tool (`AskUserQuestion`)**, not a widget, artifact or
  HTML quiz. Widgets don't send his taps back to you; the menu does. (He corrected this.)
- **One call = one round of 4 questions** (the tool's max). Each question:
  - `question`: numbered, e.g. `"1. Who wrote The Anthropology of Music (1964)?"`
  - `header`: `"Q1"` … `"Q4"`
  - `multiSelect: true` (always), so he can pick his answer AND use Other in the same tap
    set. Other is his only way to talk to you while a menu is open.
  - 4 `options`, each `{"label": "<the answer, 1–5 words>", "description": ""}`.
- **`description` is always the empty string.** Never "Option A/B/C/D" or any other filler
  under a choice; he asked three times for it to go.
- **Put the right answer in a random position** each question. Don't let one round be mostly
  the same position.
- **Make wrong options plausible**: real terms from the same material, not jokes.
- **Never give the answer away in the menu.** No correction, hint, definition or memory hook
  in the question text, the header or the options of the question that tests it. Corrections
  live only in your chat reply. (Matt, 2026-10-21: "You're telling me the answer IN THE
  QUESTION and then asking me it?")

## Reading his answers (Other = how it felt, or a comment)
The result comes back as `"<question>"="<picks, comma-separated>"`. Tested 2026-10-21:
an empty Other shows up as `Something else`; typed Other text shows up as the text itself.
- **Answer only** → recall was in the sweet spot (FSRS Good if right).
- **Answer + empty Other (`Something else`)** → too easy (Easy if right).
- **Answer + `h`** → too hard (Hard if right).
- **Wrong answer** → Again, whatever else he picked.
- **Any other Other text** → a comment or request. Read it and act on it before the next
  round (it may be about the quiz itself, like "drop this kind of question").
- **Two answers ticked** → treat as a slip: count it wrong only if neither is right, and
  mention it in one line.
There is no separate confidence step; he finds it twice as slow (Matt, 2026-10-21).

## Each round
1. Build questions from his actual course files first (`~/Documents/School/<course>/`,
   see `~/projects/ai-os/docs/ABOUT_MATT.md`). If a unit has no files, say once that those
   questions come from the readings or general knowledge, not his slides.
2. Open the menu. Don't ask setup questions first; start right away.
3. When answers come back, **check the thread for typed messages that arrived while the menu
   was open** (in a project thread: `fetch_thread` newest first) and deal with them first.
   His messages sent during an open menu were missed once, and he had to ask three times.
4. Reply with the score and only what he needs:
   - `**Round N: 3/4.**`
   - one bullet per miss: `**2 ✗ It's <right answer>:**` + one line on why, plus a memory
     hook if two things keep getting mixed up (e.g. **H**ood = **H**ands-on, **M**erriam = **M**ind).
   - right answers as one line: `1 ✓ 3 ✓ 4 ✓`.
5. Next round right away. Bring each miss back reworded, at least one round after its
   correction, with no giveaway. If he says he
   only got one right from a hint, count it as a miss.
6. If he says a question isn't the kind his class would ask, drop that style of question.

## Spaced repetition
His morning check-in already reviews FSRS flashcards (`services/checkin`, deck in
`~/.hermes/assistant.db`, table `fsrs_cards`, ids prefixed by course, e.g. `music102_`).
Quiz misses aren't fed into it yet; don't build that unless Matt asks.
