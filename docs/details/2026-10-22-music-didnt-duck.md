# Music didn't duck during dictation (2026-10-22)

## 09:58 Cause and fix

Matt: music didn't duck while dictating with ⌥R in Claude.

---

### Root cause

- Dictation detection worked: mixer log shows `dictation started: ducking` each time.
- But Audio Hijack was open, and today's change (trackpad-mixer 242e78f) leaves every app in Hijack's sessions untapped, including Apple Music. The duck works by lowering tap gain, so untapped Music was never touched.

---

### Fix

- `Sources/Taps.swift`: track untapped audio processes (bypassed + Hijack-captured, minus Claude and the mixer). On dictation start, if any is running output, duck the master volume (scalar x0.45, about -16 dB) instead of tap gain; restore after (1.5s ramp).
- Volume moved by hand mid-duck: left alone. Pre-duck level saved in UserDefaults `duckSavedMaster`; restored on stop() and at next launch, so restarts/crashes never leave it low.
- Side effect: Ableton playing now ducks too (via master), if it outputs to the default device.
- Rejected: AppleScript Music volume (Music-only); always using master (would lose per-app duck when Hijack is closed).

---

### Untested

- Not tested with real dictation (I can't dictate). Built, mixer restarted cleanly.
- Undo: `git revert` the commit in ~/projects/trackpad-mixer, `./build.sh`, `scripts/restart-mixer`.
