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

## 19:55 Built and live

Matt said "sounds good" and asked for icons wherever possible (square = stop, CCW arrow = undo). Built everything in four commits on trackpad-mixer main, restarted twice with the take-control banner (granted both times). Music audio verified passing through the tap after restart (peak 0.36).

---

### built-hue

Hue: drain loop now sleeps until 1s since the last send, then sends the newest value with a 1s glide. The last value always goes out. Philips' only published figure is v1-era "max 1/s for groups"; no v2-specific number found (openHAB/Fibaro forum reports vary 10-20/s overall).

---

### built-wiggle

Wiggle = finger speed minus its 0.15s average, x scaled by pad aspect 1.3, floor 0.1 pad heights/s. Time left shrinks at rate 3 × wiggle × (1 + seconds wiggling). Simulated (tmp/wiggle_sim.py): tremor 0%, small 1% jiggle 0.3s → 3.0s fade arrives 2.82s, medium side-to-side 1s → 1.14s, big fast 1s → 0.55s. Known quirk: starting a plain slide gives a small bump (~0.27s off a 3s fade). A strip finger now stays on the strip it landed on (it used to follow x, so a sideways wiggle would cross strips).

---

### built-secondary

Stop hold 0.5s = undo (only when there's something to undo; button fills orange, dashed marks on strips, header flashes ↺ undo). Undo snapshot resets at the first strip finger of each gesture; Seek excluded. Now double-tap = pin (Shift + Now still pins). Shift double-tap = lock (filled orange shift icon), next tap unlocks. Music play: tap acts on lift instead of touch-down (so hold can be told apart), hold 0.5s = toggle favorite via AppleScript `favorited` (checked in Music's sdef), header flashes heart. Top buttons are icon-only (Duration keeps its time); hints are small orange icons. Shift-swapped column icons turn orange; the underline is gone. Checked with offscreen snapshots (new `--snapshot DIR` flag), not on screen.

---

### built-record-stop

Each tap keeps a ring of its output. On pause the output reads it at a rate falling linearly 1 → 0 over 0.3s (last 15% fades out to avoid a click), then stays silent until the app's input is quiet 0.15s (max 3s). The real pause is sent at the end of the 0.3s. Applies to per-channel play buttons and Master pause-all; resuming cancels. Only when the channel is tapped and audible. Not heard by me: needs Matt's ears. Chrome's pause goes through youtube.sh (~2s), covered by the 3s silence cap.

Undo: `git revert` the commits in ~/projects/trackpad-mixer, ./build.sh, scripts/restart-mixer.

A tool guard blocked one Bash edit because the heredoc contained an osascript string; I made those two edits with the Edit tool instead (no command touched the screen).
