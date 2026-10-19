# Morning check-in

Claude-native replacement for the Telegram morning flow, in two stages, both in one Code thread opened from an
iMessage link on Matt's phone. The thread's first message links the page; the page opens in the app's viewer on top
of the thread, and closing it lands him back in the chat:

1. **Page** (Artifact https://claude.ai/artifact/5CLZnpsQVxcFDP7bmALrNC, `template.html` built by `build.py`):
   breathing animation → gratitude (typed) → newly unlocked habits → flashcards (instant ✅/❌, then
   Again/Hard/Good/Easy) → "close this page and go back to the thread for part two". No model runs here. Results save to the page's db
   (`checkins/<date>`).
2. **Talk thread** (Sonnet, Remote Control CLI in tmux): plain conversation, no question menus, so Matt can use
   Claude's dictation. How he feels, the day ahead, one light plan, then the comic as the reward. Its instructions
   (`checkin_prompt.md`) go in as a hidden system prompt; the only visible opener is "Morning check-in".

History: 2026-10-17 the page was shelved for a question-button thread; 2026-10-19 Matt found the thread worse
(Apple-only dictation in menus, a model call per card, the setup prompt and comic link visible at the top) and
asked for this split.

## Files
- `ladder.json`: habits, their dose levels, and the queue of steps to add later. Edit freely.
- `ladder.py`: the habit ladder. `plan` picks today's doses; `record` logs what was done. Rules are in its docstring.
- `daily.py`: the daily job (`prepare`, `send`). See its docstring.
- `build.py` + `template.html`: the page.
- `checkin_prompt.md`: the talk thread's hidden system prompt; `{…}` fields are filled by `daily.py prepare`.
- `scheduled-task.md`: the Claude scheduled task's prompt (installed at `~/.claude/scheduled-tasks/morning-checkin/SKILL.md`).
- `data/` (gitignored): `history.jsonl`, `state.json`, `days.json` (due count, comic, thread link, sent time),
  `build/cards.json` (today's due cards), `inbox/` (calendar and yesterday's page doc), `checkin-<date>.md` (the
  thread's system prompt as sent), `comic-<date>.png`.
- Tests: `python3 -m unittest test_ladder test_daily` from this folder (assistant venv).

## Daily job
- Claude scheduled task `morning-checkin` (7:45 daily). It does what needs Claude tools: read yesterday's page doc
  (ArtifactData), read Google Calendar, publish the page (Artifact). The rest is `daily.py`:
- `prepare` records yesterday's page results (ladder, FSRS deck with the page's ratings, gratitude line in the
  Obsidian habit log; all idempotent), plans today, picks a fresh C&H comic and downloads it, starts the talk
  thread, and builds the page with today's due cards. `send` iMessages the thread link (`claude://`) via Photon, once
  per day. A page can't link into the app itself: claude:// links do nothing there and https links open Safari
  (tested 2026-10-19), so the thread links the page rather than the other way round.
- Page results land in the ladder and the deck the next morning. The thread records reflection minutes itself
  (`ladder.py record reflection=N`) and writes its notes to the Obsidian habit log.
- The thread is a `claude --remote-control --model sonnet` CLI session in tmux (`checkin-thread`), because unattended
  scheduled runs can't start or Remote-Control-link desktop sessions. Each run replaces yesterday's.
