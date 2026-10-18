# Check-in: question-button thread replaces the Artifact page

- `services/checkin/daily.py`: `prepare` plans today, takes the cards dose from due FSRS cards (options shuffled per day, stable on re-run), gets a C&H link, starts the `checkin-thread` tmux Remote Control session (Sonnet) seeded from `checkin_prompt.md` (renamed from `reflection_prompt.md`). New `finish` subcommand grades answers, applies FSRS ratings (right=3, wrong=1, log ids `checkin-<date>-<card>`), records breaths/gratitude/cards. `send` texts the thread link. Page build and ArtifactData import removed.
- Card questions are pre-built AskUserQuestion payloads (≤4 per call) embedded in the seed, so the model only relays them.
- Scheduled task `morning-checkin`: steps now calendar → prepare → send.
- Tests: `test_daily.py` (shuffle, grading, batching, seed fields) + `test_ladder.py`, 11 pass. Live: prepare against a scratch data dir started a thread whose tmux pane showed the Breathe question menu; `finish` on a copy applied one FSRS review and was idempotent on re-run.
- Not verified: buttons rendering on the phone for a CLI Remote Control session (needs Matt to open the link).
