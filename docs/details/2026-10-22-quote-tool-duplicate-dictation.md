# Quote tool: duplicated dictation (2026-10-22)

## 10:05 Body text copied again under the second quote

Matt: with dictation running he queued a comment (Return), kept dictating body text, then ⌥R'd a second quote. The body text appeared again below the new quote.

---

### Root cause

`dictating()` looked for a stop/recording button inside Claude's message box. Claude's box has no such button (noted when the tool was built), so it always returned false. So:
- Return cleared the box (⌘A, Delete) under a live dictation session.
- ⌥R #2 pasted the quote and pressed ⌘D "to start" dictation. That actually stopped the running session, and on stop Claude re-typed the session's transcript at the caret: the duplicate.

---

### The fix

- New `bin/mic-users` (Swift, CoreAudio process list, macOS 14+). `--watch com.anthropic.claudefordesktop` prints 1/0 when a Claude process starts/stops recording. Hammerspoon runs it as an hs.task and keeps `claudeMic`. ~0.4% CPU. Binary is gitignored; the module builds it with swiftc if missing.
- Plain "mic in use" is useless here: audiotee, TrackpadMixer and PS5Voice keep the mic open.
- Return on a comment: stops dictation, waits for text to land, queues + clears, then restarts dictation (fresh session) if it was on, so he can keep talking.
- ⌥R: stops dictation first (existing settle), and only presses ⌘D to start if dictation isn't already on.
- Verified live once: during Claude dictation, `Claude Helper` (com.anthropic.claudefordesktop.helper) shows as recording; gone after stop.
- Rejected: tracking our own ⌘D presses (drifts when Matt clicks the mic or Claude stops by itself); polling the mic with hs.execute (blocks HS ~150 ms per poll).

---

### Testing and risk

- Watcher parsing tested; watcher running after hot reload.
- Not tested end to end on screen: two later ⌘D presses didn't start Claude dictation at all (mic check stayed off, nothing in Claude's log), so I stopped poking at his Claude window.
- Console logs "quote_cmt: Claude dictation on/off" for debugging.
- Undo: `git revert` the commit in ~/.hammerspoon.
