# Fix the nightly restart (2026-10-25)

## 22:58 Busy check, restart follow-up, morning check

Asked (via the coordinator, from the Mac slowdown thread): the 4:30 nightly restart (`scripts/nightly_restart.sh`) hadn't restarted the Mac in 6 days. Fix the busy check, make the restart happen, and add a way to know it ran. Don't restart the Mac now.

---

### Why it never restarted

The log (`~/Library/Logs/launch-agents/nightly-restart.log`) tells the story:

- **Oct 22-23** logged "restarting" six times a night but nothing happened. Two bugs: the uptime parse was broken ("up 497837 h"), and the script sent `aevtrest`, which only shows the "Are you sure you want to restart?" dialog. Both were fixed on Oct 23 at 22:32, after that night's run, so the real restart (`aevtrrst`) has **never actually been tried**.
- **Oct 24-25** waited all night: the script treated the Claude app's "Electron" NoIdleSleep assertion as "a turn is running". That assertion has been held for 44 hours straight (`pmset -g assertions`), so it means nothing; it's the app's keep-awake, not a turn.

---

### New busy check

A night is skipped only for real Claude work, checked at each 15-minute slot:

- any Claude Code transcript (`~/.claude/projects/**/*.jsonl`, which covers Code tab and project-thread sessions) written in the last 10 minutes, or
- a Bash tool command (an `eval` child of the claude CLI, the same test `tool_watchdog.py` uses) that has been running for less than an hour. Older ones are background servers and would block forever, like the assertion did.

Rejected: keeping the assertion with an age limit (it doesn't track turns at all), and checking CPU use (noisy).

Tested: with this thread active it waits and names the busy thread; with an empty fake home and no running command it reaches "dry run: would restart now".

---

### Knowing whether it worked

- **After the restart request**, the script waits 2 minutes. If the Mac is still up, it logs "restart cancelled" plus loginwindow's own reason (usually which app refused to quit), so the next retry and the morning check can say why.
- **Morning check**: a new launch agent `com.matt.agent.nightly-restart-check` runs `nightly_restart.sh check` at 9:00 (or on wake if the Mac slept through it). If the Mac hasn't booted since 4:00 that day, it shows a toast "The Mac didn't restart last night" with the uptime and the last reason from the log. It stays silent when it worked.
- Copies of both launch agents are now in `config/launchd/`.

---

### Untested and risks

- **The real restart has never run.** Tonight is its first real try. An app that asks "quit anyway?" (possibly the Claude app itself with sessions open, or a Terminal with running processes) will cancel it; tomorrow's log or toast will say which.
- **A thread that keeps working overnight** will still block the restart, by design. The morning toast will say so.
- Undo: `git revert` the commit, and `launchctl bootout gui/$(id -u)/com.matt.agent.nightly-restart-check` plus move its plist to the Trash.

## 23:00 The app that blocked it was Claude

Matt remembered seeing a dialog in the morning and guessed Ableton or Claude.

---

### Claude failed to quit

macOS's own log for the Oct 23 4:30 try shows the restart did start (no "Are you sure?" dialog), then stopped with loginwindow's message: "Your Mac hasn't restarted because Claude failed to quit." That is the dialog Matt saw. Ableton didn't appear.

---

### Quit Claude first

Before asking for the restart, the script now quits the Claude app itself (it already knows no thread is working), waits up to 30 seconds, and force-quits it if it's still open. Ableton is left alone, so unsaved music still stops the restart and keeps its save prompt.

If the restart is still cancelled by another app, the script logs that app's name (it now reads loginwindow's "hasn't restarted because" message) and reopens Claude so threads keep running. Reopening goes through the take-control queue (`claude-control lock`).

---

### Still untested

Quitting and reopening Claude haven't been run for real, since that would close this thread. Tonight's 4:30 run is the first test; tomorrow's log or 9:00 toast will show the result.
