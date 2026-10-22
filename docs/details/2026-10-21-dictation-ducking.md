# Duck audio during Claude dictation

## 20:52 Ducking built into the trackpad mixer

Asked: any playing audio should duck while Claude.app dictation is on, then come back.

---

### Why the mixer

Existing tools: macOS has no built-in "duck on mic" setting; SoundSource/Background Music don't trigger on another app's mic use. The trackpad mixer already taps every app (named channels + "System" catch-all), so ducking is one extra multiplier on its gain. No new taps, no new process (tonight's coreaudiod wedge came from leaked taps).

---

### How it works

- In `refresh()` (runs on every audio-process change) the mixer caches Core Audio process objects whose bundle ID starts with `com.anthropic.claudefordesktop` (app + helpers).
- A 0.2s timer reads `kAudioProcessPropertyIsRunningInput` on just those objects. On → duck factor ramps to 0.15 (~-16 dB) over 0.3s; off → back to 1 over 1.5s.
- `TapChannel.render` uses `gain * duck`; replacement taps inherit the current duck.
- Log lines: `dictation started: ducking` / `dictation ended: restoring` in `~/Library/Logs/TrackpadMixer.log`.

---

### Untested / limits

- Not yet confirmed that Claude's dictation flips IsRunningInput on a Claude process (probe showed all Claude processes in=0 while idle, as expected). Needs one real dictation.
- Ableton is never tapped, so the piano doesn't duck.
- If the mixer isn't running, nothing ducks.
- Duck depth/timing are constants at the top of TapOutput in Sources/Taps.swift.

---

### Undo

`git revert` the commit in ~/projects/trackpad-mixer, `./build.sh`, `scripts/restart-mixer`.
