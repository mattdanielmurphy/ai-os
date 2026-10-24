# Remote Control threads stalling (2026-10-24)

## 04:40 Why the Speechify thread went deaf, and the fix

Asked (coordinator, for Matt): find why RC threads stall and messages don't wake them; case: "Speechify reel voice" (cse_01M6QgUTFgmFrRGV2ygWEPG5) replied 03:47Z, Matt's "key added" at 03:49:21Z never woke it.

---

### The chain of events

1. 03:46:50Z the thread ran `claude-control ask` (to open `.env` in VS Code). The Mac was at 20.5 of 21.5 GB swap, load ~40, so `hs -c` timed out 3 times and the wrapper printed "hammerspoon unreachable" and quit. Hammerspoon had in fact made the ticket, just late.
2. The orphaned banner then showed with nobody behind it, counted down and was "granted".
3. Matt dismissed it with Esc Esc / Stop. `stopTicket` blocked the session for 2 h (confirmed: `claude-control blocked` listed 417b6116… with 78 min left) and sent SIGINT to its claude pid.
4. The thread had already finished its turn (03:47:26Z). SIGINT to an idle stream-json Claude process makes it exit cleanly: system log shows claude[5581] "Entering exit handler" at 21:47:47 local; transcript `cost-state` says totalDuration ends exactly then. The app recorded `priorErrorMark: stream_ended_no_result`.
5. The desktop app's Remote Control bridge never logged "session ended" for it, so it kept the thread "attached" to a dead process. New messages were not redispatched. That last part is a Claude app bug, not ours.

---

### Ruled out

- **VPS / network**: remote-control.log polls show `poll_errors: 0`; the bridge was connected throughout.
- **context-alert mod holds**: nothing in `tmp/held/holds.log` after 19:06Z.
- **Hang-guard hooks / watchdog**: watchdog never kills; guards only deny commands.
- **qmd Stop-hook refresh** started 21:47:23, a coincidence: other abnormal exits don't line up with it.

---

### Fix 1: claude-control can't kill idle agents

`~/.hammerspoon/modules/claude_control.lua` + `bin/claude-control` (commit b5bd4dc):
- An agent's ask is granted only after its wrapper has polled at least once; a ticket with no poll for 8 s is dropped (no banner left behind).
- The wrapper sends one request key for all 3 tries (no duplicate tickets) and calls `forget(key)` when it gives up.
- Stop sends SIGINT only to a *granted* holder. A pending ask's wrapper already gets "stopped" (exit 3).
- Tested live: orphan ask dropped after ~8 s, never granted; same key returns the same ticket; live ask still granted; forget drops.
- Untested: pressing Stop for real (needs Matt's keys). Remaining risk: Stop on a granted holder that already ended its turn still kills it.

---

### Fix 2: the nightly restart never restarted

`scripts/nightly_restart.sh` logged "restarting" every night, but uptime is 4 days. `«event aevtrest»` only shows the "Are you sure?" dialog; now `«event aevtrrst»` (restart; apps with unsaved work can still cancel). The uptime parse also grabbed `usec` (log said "up 497837 h"); fixed. Dry run: "up 101 h". The real restart is untested until 04:30.

---

### Memory right now

16 GB RAM, 20.5 GB swap. Biggest: VS Code extension host 4.2 GB + rust-analyzer 2.4 GB, accountsd 3.2 GB (known leak), cowork VM 1.7 GB, Claude renderer 1.6 GB.

---

### Reviving the stalled thread

Sent the thread a relay with Matt's "key added" via session messaging; its turn started. Unblocked it in claude-control.

Undo: `git revert b5bd4dc` in ~/.hammerspoon; revert the nightly_restart.sh commit in ai-os.
