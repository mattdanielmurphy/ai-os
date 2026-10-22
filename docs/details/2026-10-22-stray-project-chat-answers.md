# New threads answering unrelated project-chat messages

## 16:55 Cause found, mod filter shipped

Asked (via coordinator): four threads started on coordinator posts also answered Matt's Big Pun share link or his Audio Hijack message. Find the cause, fix it so a new thread only gets its own root plus attached context.

---

### Server queues a second message

Cause is on the Projects server, not in ai-os. Every affected session's transcript (`~/.claude/projects/*/<id>.jsonl`) shows two `enqueue` operations within 5 ms of the session being created: the coordinator's spawn brief, then a `<wake reason="mention">` with **no `<thread>` element** whose trigger message is Matt's latest project-chat mention. The second one is dequeued when the first turn ends, so the agent answers it ~1 min after its real reply. Its `current-time` is the moment the coordinator started the thread.

- Dictation thread (`ff36ba9b…`): got Big Pun link `…WyeokRB…` at 16:17:46.
- Clipboard thread (`fd91bde5…`): same Big Pun message at 16:17:28.
- Mixer thread (`5fa19a74…`): got the Audio Hijack message `…4F54k7…` at 15:49:15.

When a thread starts on Matt's own message, that second wake *is* the thread's root, so nothing looks wrong. When it starts on a coordinator post, the server fills that slot with the latest project-chat mention instead. Scan of all transcripts: 73 thread-less wakes, all right after a spawn brief; ~42 had a message id different from the thread's own id (some of my thread-id extraction may be off, but the pattern is clear).

---

### Ruled out ai-os

Hooks can't enqueue prompts (they add attachments). context-alert only holds/drops/passes messages; `cold_handoff.py` and `project_mode_cost.py` only read `<wake>`s. QMD hook adds past-thread hints, not project messages.

---

### Filter in context-alert

context-alert 0.4.1 (`mods/context-alert/hooks/register.tsx`):
- A `tool.call` hook on `mcp__hearthbot__reply` reads `thread_id` from the first successful reply and stores it.
- `prompt.submit` drops a `<wake>` with no `<thread>` whose message id isn't that thread id ("Not this thread's message…"), so the model never sees it.
- Before the first reply the thread id is unknown, so nothing is dropped (safe default). The stray always arrives after turn 1, and turn 1 normally ends with a reply.

Rejected: dropping every thread-less wake after a spawn (that also drops the legit root when a thread starts on Matt's message); asking the coordinator to stop posting roots (doesn't fix the server).

Tests: 3 new in `context-alert.test.tsx`, all 23 pass; `plugin validate` passes. Installed to the managed scope; takes effect after the Claude app restarts (the nightly restart covers it).

---

### Still open

- Server bug should be reported to Anthropic; the mod only hides it on Matt's Mac.
- Untested live: whether a real MCP result reaches `tool.call` in the exact shape the regex expects (it stringifies the whole result, so either form matches).
- Undo: `git revert f59927c9`, bump the version, `claude plugin update context-alert@ai-os-mods`.
