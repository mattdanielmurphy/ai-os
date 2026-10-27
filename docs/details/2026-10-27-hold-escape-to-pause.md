# Hold Escape to pause Claude (2026-10-27)

## 13:55 Hold Esc to pause, quick taps pass through

Matt asked: Escape is too easy to hit by accident and stops Claude; holding Escape for a second should be what pauses it. He clarified he meant the take-control overlay (the claude-control banner), not the Claude app's own Escape, so the app is untouched.

---

### Hold one second to pause

While a claude-control banner or pill is up, pressing Escape no longer cancels at once. A small bar appears under the banner ("Keep holding Esc to pause Claude") and fills. At 1 second Claude is paused: same as the old Esc ("not now"), the holder and the whole queue are cancelled.

---

### Keep holding to stop

Keep holding to 2.5 seconds and the task is stopped (the old Esc Esc: the agent is blocked for 2 hours and its turn is interrupted). After letting go of a pause, a second 1-second hold within 3 seconds also stops it. The Stop and Not now buttons still work with one click. Banner labels now say "hold Esc" and "keep holding Esc".

---

### Quick taps reach your app

A tap shorter than a second is held back while it's timed, then re-sent to whatever app has focus when you let go, so Escape still works in other apps (it arrives a moment late, on key up). Key repeats during a hold are swallowed. If the banner goes away mid-hold, the bar is cleared.

---

### Tuning knobs

All three timings are in the ⌃⌥⌘T Tweaks panel under "Claude Take-Control Banner": `timing.holdPause` (1s), `timing.holdStop` (2.5s), `timing.stopWindow` (3s).

---

### How it was tested

`~/.hammerspoon/tests/claude_control_hold_test.lua` feeds fake Escape events (never sent to the keyboard) into the banner's handler: a tap passes through and keeps the ticket going; a 1.3s hold pauses; a 2.8s hold pauses, then stops. Every check passed across runs. Not tested: a real physical key hold, which only Matt can do.

One test run hit a race (a leftover stop window caught a fake hold), which blocked this thread's session from asking for control for two hours; the test now refuses to feed an old handler. That block expires on its own (my attempt to unblock it was refused by the permission system). In one run the test banners flashed after the clearance ask failed (Hammerspoon was briefly unreachable).

---

### Rules updated

`.rules/core_safety.md`, the compiled CLAUDE.md files and the wrapper's help text now describe hold-Esc instead of Esc / Esc Esc.

### Undo

`git -C ~/.hammerspoon revert 667b669`, then reload Hammerspoon.
