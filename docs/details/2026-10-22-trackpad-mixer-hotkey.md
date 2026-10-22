# Trackpad mixer hotkey (2026-10-22)

## 12:20 Hotkey summons the mixer on the built-in trackpad

Asked: a hotkey that summons the mixer one-shot on the MacBook's built-in trackpad; when the mixer dismisses, the pad returns to normal.

---

### Hotkey choice

⌃⌥⌘V ("volume"). Checked every live Hammerspoon binding (⌃⌥⌘ M, L, R taken) and Keyboard Maestro's macros (⌃⌥⌘ A, T, M, I taken). V is free in both. Raycast/Alfred hotkeys weren't checked (not easily readable); if ⌃⌥⌘V does something else, that's why.

---

### How it works

- Hammerspoon `modules/trackpad_mixer_summon.lua` binds ⌃⌥⌘V and posts the distributed notification `ca.mattmurphy.trackpad-mixer.summon`.
- The mixer sets `Pads.builtInSummoned`, so built-in pad frames count as mixer frames (cursor blocked while touching, like the old pad), and shows the full HUD. Strip touches act live right away (no preview ring, since the HUD is already up).
- When the HUD hides (4s idle, Esc, click outside) or collapses to the fades strip, `HUD.onDismiss` ends it; a finger still down is released so the cursor never stays blocked.
- Pressing ⌃⌥⌘V again while it's up closes it.
- Works with the old Magic Trackpad unplugged (it was unplugged during the test): the built-in pad is registered on demand.

---

### Tested / untested

Tested: build, safe restart, summon + close via the notification (log shows both). Not tested: actual finger use on the built-in pad, and the real keypress (agents can't touch the pad). Pinning the HUD keeps the pad as the mixer until you close it.

---

### Undo

Revert the commits in trackpad-mixer ("Hotkey summons the mixer…") and ~/.hammerspoon ("Add ⌃⌥⌘V…"), rebuild, `scripts/restart-mixer`.

## 13:50 Music fader breaks when Audio Hijack is open

Asked: Music's fader stopped working whenever Audio Hijack was open, even with no session running.

---

### Cause and fix

Cause: the mixer left every app in Audio Hijack's saved sessions untapped whenever Hijack was open. Music is a source in the "Input Device" session (with Claude), so Music lost its fader.

Fix: they're only left untapped while a session is actually running, judged by Core Audio's IsRunning flag on Audio Hijack's or arkaudiod's audio process. Checked every 0.2s, so a starting recording re-taps quickly. Rejected: Audio Hijack's JS scripting via URL (no way to read state back without hacks, may pull it forward).

---

### Session detection untested

Verified: with Audio Hijack open and idle, Music is tapped again (log: "Music: tapping 1 audio process(es)"). Not verified: that a running session flips the flag. If it doesn't, a recording of Music would come out silent. Test: start the session, play Music, check the recording; the log line "Audio Hijack session running: leaving … alone" confirms it.

---

### Undo

Revert "Only leave Audio Hijack's apps untapped while a session runs" in trackpad-mixer, `./build.sh`, `scripts/restart-mixer`.

## 13:55 Recording post-mixer audio in Audio Hijack

Asked: System-Wide Audio in Audio Hijack records audio as if the mixer weren't there; how to record the mixed result.

---

### Why SWA misses the mixer

The mixer taps each app (muting it at the source) and plays the audio back itself at the fader's gain. System-Wide Audio grabs each app's audio as the app produces it, so it gets the pre-fader copy.

---

### Setup instead of SWA

In the session, replace System-Wide Audio with two Application sources: TrackpadMixer (all tapped apps, post-fader; if it's not in the picker, choose it from `~/projects/trackpad-mixer/bin/TrackpadMixer.app`) and Ableton Live (never tapped, so it isn't in the mixer's output). Add an Output Device block if you stop hearing it. No mixer code change needed: the mixer never taps itself or Ableton, so a running session doesn't change its behaviour. Rejected: a Loopback virtual device (same result, one more app in the chain). Untested; Matt to try.

## 14:00 Wiggle accelerates too fast

Asked: wiggling speeds up the fade at about the right rate, but then it keeps accelerating (3s for 0–30%, then 0.5s for 30–100%).

---

### Cause of the runaway

Each frame of wiggle took a fraction of the remaining time off, and the gain grew with every second of sustained wiggle (×(1 + seconds)). Shrinking the time left by a fraction every frame means the speed (distance left / time left) keeps climbing even at a constant wiggle.

---

### New wiggle model

Wiggle now sets a speed multiplier: goal = 1 + 3 × wiggle speed (pad heights/s), max 8×, eased in over ~0.4s. It only rises; when the wiggle stops, the fade keeps the faster pace to the end. The fade covers its normal time `boost` times faster, so the speed is steady. Rejected: keeping the old credit model with a cap (still curves).

---

### Wiggle untested by hand

Built and restarted; the feel needs Matt's fingers. Knobs: `wiggleGain`, `wiggleRise`, `wiggleMaxBoost` in Sources/HUD.swift. Also seen in the log: an Audio Hijack session with TrackpadMixer as a source was detected as running, so session detection works.

## 14:05 Fade curve spends too long at the quiet end

Asked: rises spend too long in the quiet early part and rush the loud end; should be the opposite.

---

### Loudness-weighted fade curve

Fades were linear in fader level (a 50 dB taper), so a 0→100% rise spent its first ~40% of time below -30 dB, nearly inaudible. Now fades move evenly in level^2.5 (Fade.loudWeight in Sources/Mixer.swift). Rise 0→100: 40% at 10% of the time, 76% at half time, the last 24% takes the second half. Falls mirror it: leave the top slowly, drop fast through the quiet end. Moving evenly in that space keeps the path the same when the fade is restarted on every finger move (an ease-out curve on progress would also work for rises but stalls falls). Fade lengths and wiggle unchanged. Also applies to Lights, Mic and Master. Untested by hand; raise loudWeight (3–4) for an even longer top.

## 14:58 Stepped faders, wiggle tiers, curve pulled back

Asked: fader levels move in discrete steps; wiggle climbs gently to "medium", then one more wiggle leaps to far too fast; the loud-end curve went too far.

---

### Smooth fader audio

Cause: fades send a new gain to the taps at most 20×/s; the audio thread jumped to each new gain within one buffer (~10ms) and held it for the rest of the 50ms, a staircase. Now the gain glides toward its target sample by sample (one-pole, 60ms, `TapChannel.glideSeconds` in Taps.swift), longer than the gap between updates, so it's continuous. Replaced taps now stop 0.3s after their gain is set to 0 (was 0.1s) so the glide reaches silence first. Ableton, Master and Lights aren't taps; if one of them steps, say which.

---

### Gentler wiggle step-ups

Cause: the speed goal followed the instantaneous wiggle, and speed only ever rises, so one fast stroke ratcheted it to a high speed for good. Now the speed follows the wiggle averaged over 0.8s (`wiggle.settle`) and climbs at most 2× per second (`wiggle.maxStepUp`). Both are knobs in the ⌃⌥⌘T Tweaks panel with the rest.

---

### Curve pulled back

`fade.loudWeight` 2.5 → 1.8: a full rise now reaches ~28% at 10% of its time and ~68% at half time (was 40% / 76%).

---

### Tested here

Built, restarted, audio flowing (peak dump). Feel untested by hand.

## 16:50 Smooth fader lines (visual smoothing)

Matt: fader lines still move jerkily after all the wiggle/curve math; the final motion must look smooth, visual-only smoothing is fine; expose the amount in tweaks.


---

### Why the lines jerked

Every finger move calls `Mixer.fadeToward`, which restarts the fade from the current level with a new target and end time. Position stays continuous, but the speed jumps on each restart (new slope, new loud-weight curve span), and touch frames arrive unevenly. Wiggle boost changes `endsAt` too, so speed steps again. The HUD drew `ch.level` raw, so every speed step showed.


---

### Spring smoothing on the drawn lines

`MixerView` (Sources/HUD.swift) now draws each line (level fill, fade-target line, pending-target bar, and the compact strip's bar/marker) at a critically damped spring position that chases the real value (SmoothDamp step, smooths speed as well as position). Stepped once per drawn frame; a `CADisplayLink` redraws at the screen's refresh while any line is still moving and pauses itself when all have settled (no idle CPU). New lines start at their goal (no swoop in). Audio is untouched (it already has its own ~60ms slew).

Rejected: re-architecting fades to keep velocity continuous in the model. Bigger change, touches audio; Matt said visual smoothing is enough.


---

### Smoothing knob

`display.smoothing` in tweaks.json / ⌃⌥⌘T, default 0.08 s, 0 = off, max 0.5. Higher = silkier but the line lags the sound more.

Untested by hand. Undo: set the knob to 0, or `git revert` the commit. Built, snapshot rendered, mixer restarted with `scripts/restart-mixer`, running.

Side note: the HUD accent is `#C2502F`, the terracotta Matt banned; left alone because colours wait for the master palette.

## 16:58 Banner click opened the thread list

Matt: clicking a claude-control banner opened the threads list, not the thread. His click (16:37) predates commit cf6ee8d in ~/.hammerspoon (16:44, another agent), which switched every banner/toast link to `claude://code/project/<chan>?thread=<cmsg>`. The old `claude://claude.ai/epitaxy/project/...?thread=` form loses the query and lands on the list. Checked the Claude app's URL handler (app.asar): `/code/project/<chan>` with `thread=cmsg_…` is parsed into a thread id, so the new form should open the thread. Live Hammerspoon already resolves thread ids to the new form. Not click-tested: opening the app would change Matt's screen, so he tests it with the command in the reply. Possible remaining failure: a feature gate in the handler can divert the link; if so the next fix is in claude_links.lua.
