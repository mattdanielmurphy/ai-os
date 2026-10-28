# Daily custodian (Code-tab Coordinator)

Ported 2026-10-28 from the Projects "Everything" cloud trigger `trig_0172AJbbznF4f1E1XoaekCFH`.
`scripts/coordinator_custodian.py` (launchd `com.matt.agent.coordinator-custodian`, daily 08:41)
drops the prompt below into the Coordinator inbox; the context-alert mod submits it.

## What the Coordinator does on that message
0. **Quiet check**: if no linked session had a turn in 24 h and `custodian-state.md` shows no backlog, stop.
1. **Loose ends** (most important; sessions active in the last 48 h, not working). Don't trust the state label alone, read the last 3 messages:
   a. *Unanswered*: newest real message is Matt's, 20+ min old → forward it to that session (SendMessage).
   b. *Waiting on Matt*: agent asked, offered an action or asked for a test, 3+ h ago → one short list to Matt.
   c. *Broken*: session failed or stopped mid-task.
   Report each once (log `loose-end <a|b|c> <id> <title>`), again only if it changed.
   Also read `coordinator/threads.json`; for each thread not `done`/`parked`, check its last turn
   (`list_sessions {"linked": true}`). Anything that finished and still needs Matt goes into one short list
   ("5 of N" rule). Never mark a result resolved that Matt hasn't checked.
2. **Cleanup** (max 20 per run, idle 6+ h): DONE (result delivered, nothing open) → archive without asking; UNSURE → ask Matt once in a 👍 list. Also: archive superseded threads and threads that only answered a question; park
   unstarted ideas in Linear (team MAT, label "Parked idea") and set their registry state to `parked`.
3. **Long-thread flags**: threads over ~200k tokens get a `/_handoff` suggestion (once, not daily).
4. **Dates**: compare `docs/SCHOOL.md` due dates in the next 3 days against Apple Reminders; add missing ones.
5. Update `coordinator/custodian-state.md` (last run, what was flagged) so the next run doesn't repeat itself.
6. Say nothing to Matt if nothing needs him.
