# Cold-thread auto handoff (context-alert 0.4.0)

## 23:50 Auto fresh thread, Sonnet writer, links, same-thread question

Matt asked (via the coordinator): 1) default to a fresh handoff when a project thread's cache has expired, no 👍 needed; 2) the handoff writer moves from Haiku to Sonnet or Opus at low effort; 3) the old thread says "Handed off to <link> because the cache expired" and the new one links back; 4) find out whether the new thread can happen under the hood so the same thread just continues.

---

### Auto move is live

When a message lands in a cold project thread, the mod (mods/context-alert/hooks/register.tsx) still holds it (no model call), posts one line in the thread, and starts the handoff. New: as soon as the handoff is written (about 30 s), it asks the coordinator for the fresh thread by itself (`autoFresh`). Matt can still:

- ⏩ or reply "here"/"go" before then: continue in this thread (pays the full re-read).
- ❌: drop the message.
- ✋/👀: stop the automatic move; his next message moves it (with that message added).
- 👍 or any other reply: move it now, with what he wrote added.
- Edit the held message: the handoff is rewritten with the new text and the timer restarts.

A sequence number (`holdSeq`) makes sure only one of "auto" and "Matt answered" ever sends. If the handoff fails twice, the thread gets a "Handoff failed" line and the message stays held, so ⏩ or a retry still works.

Rejected: a fixed wait (say, 2 minutes) before moving. The handoff itself takes ~30 s, which is already a window for ⏩; adding more just delays the answer.

---

### Sonnet writes handoffs

scripts/cold_handoff.py now runs `claude -p --model sonnet --effort low` (was `--model haiku`). Verified the flags on this Mac's CLI and ran a real handoff on a 1.5 MB transcript: 31 s, good brief. Picked Sonnet over Opus: cheaper and fast for summarising, and low effort keeps it quick. The slash command is now `/cold-handoff` (old `/haiku-handoff` and `/fresh` still work); band button says "Handoff by Sonnet".

---

### Both thread links

- New thread: the coordinator's brief now asks it to make the new thread's opening line "Continued from [the old thread](#parent) because its cache expired." The parent id comes from the `<thread ts=…>` in the held message's envelope.
- Old thread: after starting the new thread, the coordinator sends the old thread `context-alert handed-off: <new thread id>` via message_thread. The mod catches that relay before the model sees it and posts "➡️ Handed off to [the new thread](#id) because the cache expired." So the cold thread's model never wakes, and it costs nothing.

Untested live: whether the coordinator follows the new link instructions (it reads them as free text), and that a message_thread relay reaches the mod's prompt.submit hook (it should: relays arrive as user turns like this thread's own spawn relay did, starting with `<relay from="coordinator"`). Unit tests cover the mod side.

---

### Same thread continuing

Honest answer: possible, not built, needs one live test first.

- The mod API has `$.command.run({ command })` (can run built-in commands such as `/clear`), `$.prompt.submit({ text })` and `$.session.compact({ instructions })`.
- Compact is no help: it re-reads the whole cold thread at full price to summarise it, which is the cost we're avoiding.
- The promising path: on a cold hold, write the handoff (Sonnet, from the file), then have the mod run `/clear` in the same session and `$.prompt.submit` "Read <handoff> and continue. Then: <his message>". From Matt's side the same thread just answers, with a fresh, small context.
- Risk: `/clear` starts a new conversation inside the session. Unknown whether the project thread's Remote Control link and the project system prompt survive it. If they don't, the thread goes deaf. That needs a test on a throwaway project thread before it ships.
- Path forward: one disposable thread, let it go cold (or fake the cache time), trigger the clear-and-reseed, check it still replies in the thread. If yes, switch the default from "new thread" to "same thread" and drop the link lines.

---

### How to undo

Revert the commit "context-alert 0.4.0" in ai-os, then `claude plugin marketplace update ai-os-mods` and `claude plugin update context-alert@ai-os-mods` with the app's bundled binary, then restart the app.
