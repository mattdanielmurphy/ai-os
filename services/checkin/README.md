# Morning check-in

> **2026-10-17: the Artifact page is shelved** (see `shelf/INDEX.md`). The check-in is moving to native question buttons in a Code thread, which work on the phone. The page code stays here until that replaces it.

Claude-native replacement for the Telegram morning flow. Order each morning:

1. **Page** (Artifact, opened from the iMessage link): breaths → gratitude → newly unlocked steps → day → flashcards → comic.
2. **Thread** (Sonnet): the page's last button, "Now reflect with Claude", opens it. Dictated morning reflection,
   therapist-style, ending in one light plan for the day. Seed prompt: `reflection_prompt.md`.

## Files
- `ladder.json`: habits, their dose levels, and the queue of steps to add later. Edit freely.
- `ladder.py`: the habit ladder. `plan` picks today's doses; `record` logs what was done. Rules are in its docstring.
- `build.py`: renders `template.html` with today's plan and the thread link into `morning-checkin.html`.
- `data/` (gitignored): `history.jsonl` and `state.json`.
- Tests: `python3 -m unittest test_ladder` from this folder.

## Daily job
- Claude scheduled task `morning-checkin` (7:45 daily, `~/.claude/scheduled-tasks/morning-checkin/SKILL.md`). It only does
  what needs Claude tools: read `checkins/<yesterday>` from the page's db, read Google Calendar, publish the Artifact.
- `daily.py prepare` does the rest: `ladder.py record` for yesterday (gratitude=1 if non-empty, cards=reviewed or the
  planned dose if none were due), applies the page's card ratings to the FSRS deck (`~/.hermes/assistant.db`,
  idempotent), plans today, picks real due cards and a fresh C&H comic, starts the Sonnet reflection thread and builds
  the page. `daily.py send` iMessages the page link via Photon, once per day.
- Why not launchd: the page db, Artifact publishing and Google Calendar are only reachable as Claude tools.
- The reflection thread is a `claude --remote-control --model sonnet` CLI session in tmux (`checkin-reflection`),
  because unattended scheduled runs can't start or Remote-Control-link desktop sessions. Each run replaces
  yesterday's. Its link (`claude://code/session_…`) is behind the page's last button.
- Per-day bookkeeping (due count, comic, thread link, sent time) is in `data/days.json`.
