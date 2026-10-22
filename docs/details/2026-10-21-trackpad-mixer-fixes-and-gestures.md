# Trackpad mixer fixes and gestures (2026-10-21)

## 19:15 Logic check before building

Matt asked (old thread "Trackpad mixer polish"): cap Hue update rate, any-axis wiggle acceleration, secondary functions on hold/double-tap, fix the Shift underline look, a Favorite button for Apple Music, record-stop on pause. He asked for examples of the logic first. Nothing built yet.

---

### hue-rate

Now: every fade frame calls `HueLights.set`, which spawns `python3 hue.py` and PUTs `grouped_light`. Only one call is in flight and stale values collapse, so the lag is most likely the bridge's own queue. Philips' docs put group (room/zone/home) commands at about 1 per second and single lights at about 10 per second; above that the bridge queues or drops them. (Re-check the exact figure on developers.meethue.com before hardcoding.)

Plan: at most 1 group command per second, each with `dynamics.duration` ≈ 1s so the bridge glides between steps (smooth, not steppy). The final value always goes out on lift / fade end. Example: drag 100% → 20% over 3s = ~4 commands (70, 45, 25, 20), each gliding 1s. Rejected: per-light commands at 10/s (needs every light ID, and 10+ lights would still exceed it).

---

### wiggle

Now: only vertical reversals of ≥3% pad height count, each takes a flat 0.25s off.

Plan: measure back-and-forth motion in both axes. Speed-up grows with how big and how fast the wiggle is, and keeps adding while it continues, so the fade keeps accelerating.
- Tiny side-to-side jiggle, 0.3s → fade arrives ~10–20% sooner.
- Big fast side-to-side, 1s → fade finishes in a fraction of its time.
- Keep wiggling → keeps accelerating until it arrives.
- Plain slide up/down to a new level → no speed-up (that moves the target).
- Resting finger → nothing (tremor under a small threshold ignored).
- The finger stays owned by the strip it landed on, so a sideways wiggle never crosses into the next strip.

---

### secondary

Matt's rule: a button normally tapped → hold = secondary; a button normally held → double-tap = secondary.

Proposed (to confirm):
- Stop (tap): hold = undo the last fade (levels back to where they started).
- Play/pause (tap): hold on Music's column = Favorite. Other columns: nothing yet. Shift + hold = previous stays.
- Now (tap = jump, hold = live, so both): treat as held → double-tap = pin HUD.
- Duration (held): double-tap-hold = sweep already exists. Keep.
- Shift (held): double-tap = Shift lock, stays on until tapped again.

---

### underline

The thick orange bar under Shift-swapped column icons goes. The swapped icon itself turns orange instead (same accent, no extra shape).

---

### favorite

Music AppleScript: `favorited of current track` (older Music: `loved`). Toggles, with a heart filled/outline from the track's state shown in the HUD. Recommended home: hold Music's play button.

---

### record-stop

The mixer already carries Music's audio through its own tap, so it can slow it itself: on pause, play the next 0.3s from a short buffer at a rate falling 1.0 → 0, pitch dropping with it, then send the real pause. Resume is normal (no spin-up). Works for tapped channels (Music, Chrome, IINA), not Piano (Ableton) or Master.

## 19:20 Making Stop-hold undo obvious

Matt: fine with hold-Stop = undo, but it must be blatantly obvious what's happening. Proposal: while Stop is held, its button fills up (same hold-progress fill Duration uses) with "undo" under it, and ghost marks appear on every strip at the levels it will go back to. Let go before full = plain Stop. Full = levels fade back, header reads "undo · back to before". Nothing to undo = no fill, label greys out. Rejected: instant snap back (jarring, and silent if he didn't see it).
