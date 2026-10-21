# Handoff: quiz menus, menu limits, emoji replies (2026-10-21)

Project thread in "Everything", started from Matt's message about reusing the World Music quiz pattern.

## Current state
- **Quiz skill is live:** `skills/_quiz-with-tap-menus/SKILL.md` (synced to `~/.claude/skills`, `~/.agents/skills`). Rule lines in `.rules/core_safety.md` ("Quizzes & Study Sessions"), `~/.claude/CLAUDE.md`, Claude memory `quiz-with-tap-menus.md`.
- **No menus outside quizzes is live:** `.rules/core_safety.md`, `~/.claude/CLAUDE.md` ("Ask questions in plain text…"), memory `menus-not-for-general-questions.md`.
- **Emoji reply set: proposed, waiting for Matt's 👍** on the proposal message. Not saved as a rule yet.

## Matt's rules from this thread
- Quizzes: AskUserQuestion, rounds of 4, `multiSelect: true` always, option `description: ""` (never "Option A"), right answer in a random position, score + one line per miss.
- Other is his channel while a menu is open: empty Other (returns `Something else`) = just guessing → counts as a miss even if right; `e` = too easy; any other text = a comment to act on before the next round. No separate confidence step (twice as slow).
- Never put the answer, a correction or a hint in the question/menu that tests it; corrections only in the chat reply; retest misses a round later, reworded.
- Check for typed messages after each menu (they wait while a menu is open).
- Outside quizzes: plain-text questions only, never menus.

## Tested facts
- AskUserQuestion: 1–4 questions, 2–4 options + automatic Other, short labels, 12-char header, optional multiSelect / preview / notes (preview and notes untested on his devices).
- A single-question single-select menu still needs Submit (Skip + Submit are app UI, not settable). No one-tap, no lone "Yes" button.
- While a menu is open, his normal replies and Claude dictation don't reach the agent; only Other does.
- A reaction on an agent's message in a project thread wakes that thread's session (`reason="reactions"`, emoji named) within ~30 s. Reactions on his own messages don't.
- The Mac right-click reaction row = his 6 most recently used emojis (not configurable).

## Open
1. **Emoji reply set** (awaiting his 👍): 👍 yes/do it · ❌ no · ❓ didn't get it, explain simpler · ⏩ next/keep going · ✋ wait, I'm typing more · ✅ done, wrap up. On approval: save to `.rules/core_safety.md` + `scripts/build_rules.py`, `~/.claude/CLAUDE.md`, memory, and send the coordinator a project-instructions line.
2. **FSRS helper (not built, needs "make it"):** small script to pull one due card from `~/.hermes/assistant.db` `fsrs_cards` for a menu and write the rating back (reuse `services/checkin/daily.py` `apply_reviews` / `FSRSEngine`). Rating map: wrong or guessing → Again, right → Good, `e` → Easy.
3. **Quick-reply links:** Matt agreed not to build them (Safari tab per tap, agent must hold its turn).

## Quirks
- The World Music quiz thread's live session doesn't reload skills; the coordinator relays rule changes to it.
- The morning check-in page (`services/checkin`) already has FSRS flashcards (answer, then Again/Hard/Good/Easy) with 30 `music102_` cards.
