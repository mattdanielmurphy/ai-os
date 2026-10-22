# Trackpad mixer: vanished while resizing (2026-10-22)

## 09:50 Mixer disappeared mid-resize

Matt: "when I was resizing, it disappeared; prevent that happening".

---

### Two causes

- **Idle timer**: the mixer hides 4s after the last activity. The timer only reset on each drag step, so pausing mid-resize (or pressing an edge and holding before moving) let it fire.
- **Corner click-through**: the panel's rounded mask makes its corner pixels transparent, so a press right on a corner (where you grab to resize) went to the app behind. The "click outside closes it" monitor then hid it.

---

### The fix

- hud-kit `HUDWindow` now exposes `interacting` (mouse down on the panel) and `onStart`. Rule added to its header: owners never auto-hide while interacting.
- Mixer: cancels the hide timer on mouse-down, refuses to hide while interacting, restarts the 4s timer on release.
- Click-outside ignores presses within 16pt of the frame.
- Also removed a duplicate HUDWindow setup that `togglePin` re-ran on every pin (copy-paste slip from the hud-kit commit).
- Rejected: longer idle timeout (wouldn't fix the corner case, and slows normal auto-hide).

---

### Untested

- Not hand-tested; needs Matt to resize it, pausing mid-drag and grabbing corners.
- A corner press still can't start a resize where the mask is transparent; it just no longer hides the mixer.

### Undo

`git revert HEAD` in trackpad-mixer and hud-kit, `./build.sh`, `scripts/restart-mixer`.
