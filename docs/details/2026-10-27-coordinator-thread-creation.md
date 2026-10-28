# Coordinator thread creation issue (2026-10-27)

## 18:10 Why the Everything coordinator couldn't start a thread in ~/projects

**Asked:** the Everything project coordinator can't start a new thread in ~/projects; find out why.

---

### Folder is fine
- `~/Library/Logs/Claude/remote-control.log`: `/Users/matt/projects` is served (env_015p1o93hMvvV1zfQtXNJ6PQ). New sessions attached there fine at 17:46 and 18:01 (18:01 = this session).
- Same account/org (e1b0bd7e / 7da8d1cb) the whole time, so the coordinator's "Testing account" guess is wrong.

---

### Only the Glass TV Stremio task fails
- Coordinator (cloud session session_01UsR2dpXiZFvE9kJ5c9kLBh) called `start_thread` 7 times 23:55–00:00Z, all for "Add Stremio add-on support to Glass TV" (6 on ~/projects, 1 on ~/projects/ai-os), across 3 different message ids.
- Every one: Mac acks the work, then within ~150 ms `not attached (session_ended)` — the server had already closed the session. Tool error: "the Remote Control session could not be made this thread's session and was closed".
- Early briefs mentioned Torrentio / AutoStream / Real-Debrid; later ones were plain but attached Matt's message as context.

---

### Likely cause (inferred, not confirmed)
- The server closes the session before it reaches the Mac, only for this task's content. Most likely a server-side check on the brief/attached message (Stremio + earlier torrent/debrid context in the project), not the folder, Mac or account.
- Can't see the server's reason from here.

---

### What to try
- Start the Glass TV add-on work yourself from the Code tab in ~/projects/glass-tv (no coordinator brief), or have the coordinator start it with a brief that doesn't attach the old message.
- If that also dies instantly, it's an app/server bug: report it via the app's feedback with session id cse_01UsR2dniMTqrPBYuVEt3QGH.

Undo: nothing changed.

## 21:50 It is not Glass TV: the coordinator chat hit 30 threads

**Asked:** Matt's unrelated new-thread request also failed, even after fully quitting and relaunching Claude. It worked earlier today. Find what's really wrong.

---

### Every new thread fails since 5:55 pm
- `~/Library/Logs/Claude/remote-control.log`: every coordinator-started new thread since 17:55 ends the same way: the Mac acks it, then ~150 ms later `not attached (session_ended)`. 13 failures in a row (17:55–18:16, then 21:33–21:34 after the relaunch), on both `~/projects` and `~/projects/ai-os`, for different tasks.
- Resumed threads still attach fine (18:17, 18:19, 19:56, 21:39). So the Mac, folders, account and the app are fine.
- `main.log`: for the failed ones the app never gets to "Starting local session"; it goes straight from "Acknowledging work" to "Stopping work". The server already closed the session. The coordinator's tool error says the session "could not be made this thread's session and was closed", i.e. the server refused to link the new session to the thread.
- That's why relaunching Claude didn't help: the refusal is on Anthropic's side.
- So the earlier "torrent/debrid wording" theory is wrong: unrelated tasks fail the same way.

---

### The 30-thread pattern
- Before 10-26 22:44 every new thread had its own random-looking id. Since then every thread id starts `cse_01UsR2d…`, which looks like they all hang off one parent: the coordinator chat that started at 10-26 22:44.
- That coordinator started exactly **30** threads successfully (10-26 22:44 → 10-27 17:46). Every coordinator start after that (13 tries) failed.
- The one success after 17:55 (18:01) was a Code-tab session being published, a different path, not a coordinator start.
- Inference, not confirmed: the server caps how many threads one coordinator chat can start, and the cap is 30. Neither the logs nor any doc state this limit.

---

### Fix to try
- Start a **new coordinator chat** in the Everything project and ask it to start one small thread. If it works, the cap theory holds.
- If a new coordinator chat also fails, it's a wider server problem: report it from the app's feedback with session id `cse_01UsR2dm2M8nDUa29N4wMyX8` (21:33 failure).

---

### Follow-up worth doing
- A rule so the coordinator hands itself off before it hits the cap (e.g. at ~25 threads started), and tells Matt plainly when start fails instead of guessing. Also tell Tyler about the cap, since he'll use the same one-coordinator setup. Not done yet; offered to Matt.

Undo: nothing changed on the Mac.
