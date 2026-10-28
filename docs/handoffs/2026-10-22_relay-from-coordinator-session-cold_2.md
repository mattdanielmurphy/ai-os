# Handoff: trackpad-mixer fader fixes (2026-10-22, cold)

## Chain
- Old thread: cf365c0d-cb0f-4997-a1a9-f92e69c877ee (spawned by coordinator session session_01VoTF4gTooLHghCQaTs4ask). Reopen with `claude --resume cf365c0d-cb0f-4997-a1a9-f92e69c877ee` (expensive: cold cache).
- Details file: `~/projects/ai-os/docs/details/2026-10-22-<thread-slug>.md` (check exact slug — appended to throughout this thread per Matt's "every reply has a details file" rule).

## Chain summary
- Built a hotkey (⌃⌥⌘V) to summon trackpad-mixer one-shot on the MacBook's built-in trackpad for demos; built, restarted safely, live. Not yet tested by Matt with real fingers.
- Fixed Audio Hijack bug: mixer released control of apps in a saved session even when AH was idle (not just when recording), so Music's own fader broke. Fixed to only release during an active session (polls 5x/sec for AH/helper activity). Confirmed in logs: detects running sessions correctly.
- Diagnosed why Matt's "System-Wide Audio" AH source misses the mixer's effect (pre-fader capture) — told Matt to swap to two Application sources instead: TrackpadMixer app (post-fader mix) + Ableton Live (never mixer-controlled). Not yet tried by Matt.
- Multiple rounds tuning wiggle-acceleration and fade curve based on Matt's feedback (see "This thread" below for the final/current state).

## This thread
- **Wiggle acceleration fix**: originally jumped straight to full accel; Matt said it should ramp smoothly over ~0.4s. Then Matt clarified the *real* bug: wiggle speed tracked each instantaneous wiggle-moment and never decayed, so a sustained wiggle looked like it "jumped levels" (small→medium→suddenly way-too-fast) instead of smoothly scaling. Fixed by averaging wiggle intensity over ~0.8s and capping rate-of-change to at most 2x/sec. Live, untested by hand.
- **Fade curve**: added loud-end weighting so fades spend less time in near-silent range and more time in the audible/loud range (`Fade.loudWeight` in `Sources/Mixer.swift`). First pass (2.5) went too far — "too much time at the loud end now." Pulled back to 1.8 (full rise reaches ~28% at 10% time, ~68% at 50% time). Live, untested by hand.
- **Stepped faders fix**: faders were applying 20 discrete volume jumps/sec instead of smooth motion. Fixed to interpolate continuously between updates (~60ms slew). Covers per-app faders only — Matt should flag separately if Ableton/Master/Lights still step.
- **Tweaks panel**: all fade-length, curve-weight, and wiggle-ramp constants moved into `~/projects/trackpad-mixer/tweaks.json`, editable live via ⌃⌥⌘T panel without rebuild/restart (per coordinator request).
- Mixer rebuilt and safely restarted after each change via its safe restart script. Audio confirmed still flowing after restart. Committed and pushed to trackpad-mixer repo each round.

## Working on now
Just shipped the combined fix (stepped faders + wiggle ramp decay + fade curve pullback to 1.8) and pushed. **Nothing has been hand-tested by Matt yet** — all four pending verifications (⌃⌥⌘V hotkey with real fingers, AH TrackpadMixer+Ableton source swap, wiggle ramp feel, fade curve feel) are outstanding. Thread stopped right after the push, waiting on Matt's test feedback.

## Keep in mind
- Matt corrected the wiggle diagnosis twice — first fix (smooth 0.4s ramp to max) was based on a wrong mental model (attack time), second fix (0.8s averaging window, 2x/sec cap) is based on his precise description: speed should decay/smooth across sustained wiggling, not jump between discrete levels.
- Fade curve went from no curve → 2.5 loud-weight (too far) → 1.8 (current, unverified). Expect another round of tuning from Matt's live feel.
- `Fade.loudWeight`, wiggle gain/rise/max-boost, and fade timing are all now in `tweaks.json` — tune there first, no rebuild needed, before touching Swift source.
- Mac input (hotkey testing) needs claude-control clearance per CLAUDE.md; don't synth input yourself to verify ⌃⌥⌘V — ask Matt.
- Short bold point-form replies per coordinator note; build on 👍 if a choice is needed.
- trackpad-mixer is LIVE — always use its safe restart script, never kill/restart ad hoc.

## Next steps
1. Wait for Matt's feedback on the four untested items (hotkey, AH source swap, wiggle feel, fade curve feel) and iterate on whichever he flags; check `tweaks.json` values first before editing `Sources/Mixer.swift` or `Sources/HUD.swift`.

## Read first
- `~/projects/trackpad-mixer/tweaks.json` — all current tunable constants (fade curve, wiggle ramp, timing).
- `~/projects/trackpad-mixer/Sources/Mixer.swift` — fade curve (`loudWeight`) and per-app fader interpolation logic.
- `~/projects/trackpad-mixer/Sources/HUD.swift` — wiggle detection/speed-ramp logic.
- trackpad-mixer's HANDOFF/notes file (restart script location, architecture) — read before any restart.
- `~/projects/ai-os/docs/details/2026-10-22-<slug>.md` — full decision log for this session (find exact filename, likely dated 2026-10-22).

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-22_relay-from-coordinator-session-cold_2.md and continue. Then: the movement of the lines for the faders is STILL weirdly jerky. make sure it's always smooth, after all the math of the wiggling etc is taken into account the final curve must be and especially look smooth.
Honestly even if you just literally add some smoothing to the visuals itd be fine"
