# FaceTime "Record this call?" prompt didn't show (2026-10-27)

## 14:20 Prompt missing during Tyler call

Matt was on a FaceTime call with Tyler and no "Record this call?" prompt appeared.

---

### Transcript started by hand

Ran `call-transcript start tyler --left Tyler --right Matt` at 14:13. It connected (BlackHole) and began writing `~/calls/2026-10-27-tyler.md` immediately. Wrote `~/calls/.transcript.owner` so the watcher treats this transcript as its own: it stops it when the call ends, which also saves it to Obsidian and slub-hq like a prompted recording would.

---

### Watcher crashed at 1:54 pm

Hammerspoon was alive (running since 11:37, never down). The console showed one error at 13:54:54: `hs.application.get("FaceTime")` returned something that wasn't an app, so `hs.axuielement.applicationElement` threw inside `tick()`. The poll loop reschedules itself only after `tick()` returns, so that one error ended the loop for good. Every call after 1:54 pm went unseen.

---

### Fix

- `loop()` now runs `tick()` inside `pcall` and logs failures, so one bad check can't stop the watcher.
- `faceTimeCall()` checks the value really is an `hs.application` and wraps the AX call in `pcall`.
- Reloaded just this module (no full Hammerspoon reload, nothing on screen). Verified: timer running, detection returns `true Tyler Murphy`.
- Commit `a69fc62` in ~/.hammerspoon, pushed. Undo: `git revert a69fc62`.

Untested: the prompt itself showing on the next new call (the current call already has a recording, so the watcher correctly doesn't ask).
