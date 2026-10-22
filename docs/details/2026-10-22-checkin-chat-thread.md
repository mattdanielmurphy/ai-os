# Morning check-in: regular chat, not a Code thread (2026-10-22)

## 09:30 Why today's check-in was a Code thread, and the switch

Matt said: "the check-in I got for this morning was a CODE thread, not a chat thread".

---

### Root cause found

The earlier thread (2026-10-21) built the regular-chat path (My Mac connector `checkin_today` + `chat_mode.md`) and a
`claude.ai/new?q=Morning%20check-in` link, then stopped to ask Matt to pick: (1) link + one tap to send, or (2) the Mac
clicks send past claude.ai's "use caution" warning. He never answered, so `daily.py` kept starting the Code thread
(tmux Remote Control CLI) and texting its `claude://` link. Nothing was broken; the switch was never made.

---

### Chat link now default

Took option 1 (the recommended one; his message makes clear he wants chat). Changes in `services/checkin/daily.py`:
- `prepare` always writes `data/checkin-<date>.md` (what `checkin_today` serves) but no longer starts the Code thread.
  `--code-thread` keeps the old flow as an opt-in fallback.
- `send` texts `CHAT_URL` then the page link (Shortcut opens both; page on top). If a Code thread was started, its
  link is used instead.
- Saves a Sonnet session every morning (no idle Code thread).
Rejected option 2: it means automating a click past a safety warning; needs Matt's explicit yes.

---

### Still untested on iPhone

Whether `https://claude.ai/new?q=...` opens in the Claude iOS app or in Safari is unverified (only tested in Chrome on
the Mac). If it opens Safari, fallback: rerun with `--code-thread`, or find an app deep link.
Also: he must tap send himself (claude.ai doesn't auto-send `?q=` text).

---

### How to undo

Add `--code-thread` to step 3 in `~/.claude/scheduled-tasks/morning-checkin/SKILL.md`, or revert the commit.
Tested: unit tests pass; mocked prepare+send in tmp/ sends chat link + page link and never starts the Code thread.
