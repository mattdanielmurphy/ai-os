# Smart queue for project threads

## 23:45 The design

What Matt asked (via the coordinator): queue a prompt for a thread; when the thread's agent stops, decide whether to send it or whether the agent's latest reply needs Matt first; show a HUD indicator; reuse the quote tool's queued-comments bar; build on context-alert's hold, held-for-threads.md and the custodian.

---

### Where it lives

Inside the context-alert mod, which already runs in every thread session on the Mac and already holds messages (cold-cache holds). The queue is a second kind of hold. No new service, no polling: the thread's own session knows the exact moment its agent stops (`turn.complete`), so the decision happens then, not on the custodian's hourly tick.

Rejected: a coordinator-side or script-side poller. It would only see "status_bucket" and would be up to an hour late; the mod sees the turn end instantly and has the agent's last reply text in hand.

---

### How Matt queues

1. In the thread: start a message with `/q ` (or `⏳`). The mod catches it before the agent sees it, reacts ⏳ on it, and holds it.
2. From the project chat: tell the coordinator "queue for <thread>: …". The coordinator sends the thread a note starting `thread-queue add:`; the mod takes it without waking the agent. This is the "coordinator posts into a thread directly" path, the same trick as context-alert's `handed-off:` note.

---

### When it sends

At the end of each agent turn (and right away if the agent is idle when he queues), Haiku reads the agent's latest reply plus the queued text and answers READY or WAIT. WAIT = the reply asks Matt something (a question, a choice, a 👍 offer, test/review this) that the queued text doesn't answer. If Haiku fails, a keyword check decides (question mark, 👍, "try", "test", "review").

READY → the mod submits it as Matt's next turn, swaps ⏳ for 📨. WAIT → it stays; once Matt answers and the agent's next turn ends, it's checked again. A turn that errored or was stopped never releases the queue.

Overrides on his queued message: ⏩ = send now, ❌ = drop. `/q send` and `/q drop` do the same.

---

### The HUD

The mod writes `~/projects/ai-os/tmp/thread-queue/<thread>.json`. A Hammerspoon module draws a pill on Claude's window, in the same style and spot family as the quote bar: "⏳ 2 queued · 1 waits on you". Click: list per thread, open the thread.

The pill drawing moves out of quote_comment.lua into a shared `modules/claude_pill.lua` both use.

---

### held-for-threads.md and the custodian

The coordinator should deliver held items as `thread-queue add:` notes, so the thread decides when they land and they show on the HUD. The custodian keeps its hourly sweep as the backstop for threads whose Mac session was offline.

## 00:30 Built and tested

---

### Mod side built

context-alert 0.5.0. One hard engine rule shaped it: a `prompt.submit` hook can't submit a new prompt (it would wait on itself). So when the queue goes out from a message (agent idle, ⏩, `/q send`), the mod swaps that message's text for the queued text; when it goes out at a turn's end, `turn.complete` submits it. 32 mod tests pass (6 new: send after the turn, hold on a question then ⏩, idle send, coordinator note, drop + stopped turn, keyword fallback).

Only the agent's main turns count; subagent turns never release the queue. An interrupted or failed turn keeps it and the pill says so.

---

### Pill built

`modules/thread_queue.lua` + shared `modules/claude_pill.lua` (the quote bar's count pill now draws through it; checked its image still renders the same). Sits 164 px above Claude's bottom edge, just over the quote bar; knobs in the Tweaks panel under "Thread queue pill". Tested live: a queue file made the pill appear within ~1 s and vanish when removed. Colour is the quote bar's existing teal, no new colour.

---

### Not tested yet

A real `/q` in a live project thread: the mod loads after the plugin update and the Claude app's next restart (nightly 04:30, or sooner if Matt restarts it). Whether Remote Control fires `prompt.submit` for a mid-turn message at arrival or at delivery is unknown; both paths are handled.

---

### How to undo

Hammerspoon: remove the `thread_queue` line in init.lua. Mod: `/q` messages simply pass through if the queue code is reverted (git revert of the context-alert commit).
