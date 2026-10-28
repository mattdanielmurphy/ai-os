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
