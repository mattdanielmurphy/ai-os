# Missed morning check-ins (2026-10-25)

## 21:40 Check-in watch: re-send after the crossword, nudge when missed

Matt asked (via the coordinator): he stopped doing morning check-ins and nothing noticed; and when he wakes late, his
iPhone Shortcut opens the crossword instead of the check-in.

---

### Why the crossword wins

The check-in job texts at about 7:53 (thread/chat link, then page link). The daily crossword texts at 9:00 from the
same Photon sender (his crossword profile `matt`, hour 9, confirmed from its delivery log: sent 9:00 every day
Oct 14–25). His automation "When I get a message from Claude" runs "Claude Capture URL", which overwrites
`pending_claude.txt` with that message's links; "Claude Open Pending" opens them when he first opens his app. So when
he wakes after 9 the file holds the crossword link.

Rejected: filtering the automation by "Message contains claude.ai" on the phone. It would work, but only Matt can
edit his iPhone automations, and the Mac fix needs nothing from him. Rejected: moving the crossword hour (his
choice, and the crossword is a product with its own rules).

---

### What re-sends the links

`services/checkin/missed.py tick`, run every 10 minutes by launchd (`com.matt.agent.checkin-watch`). If today's
links went out, the check-in hasn't started, and it's 5 minutes past the crossword (`watch.crossword_at` in
`ladder.json`, default 09:00), it texts once: "Your morning check-in is still waiting…" plus how many days in a row
he's missed, then the two links last. That message now overwrites the crossword in the pending file. Once a day only;
skipped if the morning job itself ran after the crossword.

---

### How missed days are noticed

A day counts as done if the chat started (the Mac connector's `checkin_today` now runs `missed.py started`) or the
page's results reached `history.jsonl` (ingested next morning). Study-only records don't count. `missed.py status`
shows today's state and the streak. Right now: Oct 23, 24 and 25 were all missed.

---

### The nudge in Claude

The existing habit-gate hook (UserPromptSubmit) now also asks `missed.nudge()`: on Matt's first own Claude message
of the day before 17:00 while the check-in waits, the agent opens its reply with one warm line and the check-in
link, then handles his message normally. Never holds the message, no guilt, never bedtime or alarm talk (habits
rule: no bed or wake reminders). Once a day.

---

### Untested and how to undo

Untested for real: the re-send hasn't fired yet (first chance is tomorrow 9:05), and I can't see his phone, so I
haven't confirmed the Shortcut opens the second text. The page-only check-in (without the chat) isn't visible the
same day, so if he only does the page the 9:05 re-send still goes out. Undo: set `"enabled": false` under `watch`
in `services/checkin/ladder.json`, or `launchctl bootout gui/$(id -u)/com.matt.agent.checkin-watch`.

## 21:45 Mistake: a stray text tonight

When I switched the watcher on at 9:30 PM it ran right away, saw today's check-in had been missed and the crossword
had gone out, and texted Matt the re-send. I had no "too late in the day" cutoff. Fixed: `watch.resend_until`
(14:00) in `ladder.json`, with a test (`test_no_resend_late_in_day`). It won't send again today either way, since
today's `resent_at` is set.
