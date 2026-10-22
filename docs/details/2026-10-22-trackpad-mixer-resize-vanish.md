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

## 09:55 Audio Hijack + reverse capture idea

---

### Hijack status

Already fixed by an earlier thread (commit 242e78f, 09:42): while Audio Hijack is open, apps in its saved sessions stay untapped. Gap: an app you add to a Hijack session while it's open is picked up on the next refresh, not instantly (untested).

---

### Reverse capture plan

Not a bad idea; the buffer is easy because the mixer already taps every app. Proposed POC:
1. Mixer keeps a rolling 5 min buffer of everything except Music (stereo 48 kHz float ≈ 115 MB RAM; could halve with Int16).
2. When non-Music audio stops, a small HUD button shows for ~10s (own hud_slots slot).
3. Click → a strip with the waveform of the buffer; it pre-selects the last sound burst (silence-bounded, like Capture MIDI's guess). Drag to change the selection.
4. Enter / button → WAV saved to ~/Desktop (or clipboard), Esc closes.
Hard parts: the waveform picker UI, and the "guess" logic. Rejected: ScreenCaptureKit (separate capture path, duplicate permission), buying GhostTape/ReplayMac (no picker, but worth a look first).
Existing tools: GhostTape, ReplayMac (github picccassso/ReplayMac), Hotmic.
