# Morning check-in

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

## Not built yet
The daily job that runs these in order: read yesterday's page results (ArtifactData `checkins/<date>`) →
`ladder.py record` → start the Sonnet thread → `build.py --thread-url` → publish → iMessage the link.
Cards and the comic are still fixtures (`cards.json`, `comic.png`).
