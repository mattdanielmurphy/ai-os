# Morning check-in

Claude-native replacement for the Telegram morning flow: one Code thread a day, opened from an iMessage link on
Matt's phone, that asks each step with AskUserQuestion buttons (they render in the iPhone app).

Order in the thread (seed prompt: `checkin_prompt.md`, model Sonnet):
breaths → gratitude (free text) → flashcards (buttons, then ✅/❌ and the answer) → record → day ahead →
dictated reflection ending in one light plan → comic image (SendUserFile) plus its link.

The Artifact page that came before is shelved (2026-10-17, see `shelf/INDEX.md`); `template.html` and `build.py`
stay here for a possible later page (breathing animation, audio).

## Files
- `ladder.json`: habits, their dose levels, and the queue of steps to add later. Edit freely.
- `ladder.py`: the habit ladder. `plan` picks today's doses; `record` logs what was done. Rules are in its docstring.
- `daily.py`: the daily job (`prepare`, `send`) and the thread's recorder (`finish`). See its docstring.
- `checkin_prompt.md`: the thread's seed prompt; `{…}` fields are filled by `daily.py prepare`.
- `data/` (gitignored): `history.jsonl`, `state.json`, `days.json` (due count, comic, thread link, sent/finished
  times), `build/cards.json` (today's shuffled cards), `checkin-<date>.md` (the seed as sent).
- Tests: `python3 -m unittest test_ladder test_daily` from this folder.

## Daily job
- Claude scheduled task `morning-checkin` (7:45 daily, `~/.claude/scheduled-tasks/morning-checkin/SKILL.md`). It only
  does what needs Claude tools (read Google Calendar), then runs `daily.py prepare` and `daily.py send`.
- `prepare` plans today, takes today's dose of due flashcards from the FSRS deck (`~/.hermes/assistant.db`) and
  shuffles their options, picks a fresh C&H comic and downloads its image to `data/comic-<date>.png`, and starts the thread. `send` iMessages the thread link
  (`claude://code/session_…`) via Photon, once per day.
- The thread records itself: `daily.py finish --breaths N --gratitude N --answer CARD_ID=INDEX …` grades the cards,
  applies them to the deck (right = Good, wrong = Again; idempotent) and writes breaths/gratitude/cards to the
  ladder; then `ladder.py record reflection=<minutes>` after the reflection. A thread Matt never finishes records
  nothing, which the ladder counts as a missed day.
- The thread is a `claude --remote-control --model sonnet` CLI session in tmux (`checkin-thread`), because unattended
  scheduled runs can't start or Remote-Control-link desktop sessions. Each run replaces yesterday's. It may run
  `daily.py finish`, `ladder.py record` and `apple-reminders add`, and edit the Obsidian vault (habit log).
