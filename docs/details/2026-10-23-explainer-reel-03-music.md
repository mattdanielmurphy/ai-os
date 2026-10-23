# Explainer reel 03 with music (2026-10-23)

## 16:10 Reel 03 live, hang fixed

Asked (via coordinator): find why two sessions froze at "remove orange, then muted test", fix it, finish reel 03 with the ducked ambient bed, commit, push.

---

### What hung

The frozen session's transcript (`musing-shirley-034e9f/1024e0a4…jsonl`) ends on one call: opening `file://…/003-air-traffic/reel.html?mute` in the Claude browser pane. The build before it had finished (reel.html written 15:42). The pane call never returned. Headless Chrome loads the same page in under 1.5 s, so the page is fine; the pane is the problem (big local file:// media page). No stray ffmpeg/Chrome processes were left. Also: macOS has no `timeout` command, so "timeout 300" advice silently fails here; `perl -e 'alarm N; exec @ARGV'` works.

---

### What I changed

- `services/reels/test.sh` + `headless_test.cjs`: headless Chrome (playwright-core from another project's node_modules, system Chrome), `?mute` and `--mute-audio`, detached with a 2-minute alarm, logs to `tmp/test.log`, prints the mix every second.
- `build.py`: ffmpeg gets `-nostdin` so it can never sit waiting on input.
- README: reel 03 link, music knobs, "never open reels in the browser pane".
- Memory `mute-media-tests.md`: the hang lesson.
- Orange was already gone (panel theme `warm` is patch-yellow `#dcc300`); grep found no orange hexes in reel 03.

---

### Test result

Muted headless run, 20 s: music fades in over ~1 s to 0.38 (level 0.4), voice starts at ~2.5 s, music dips to ~0.22 under speech and swells to 0.33–0.39 in gaps; beat 2 starts at ~10 s; no page errors. Not heard by ear (by design).

---

### Untested and undo

- Not listened to: the duck depth (0.45) may want tuning by ear; knob `duck.depth` in tweaks.
- Published as https://claude.ai/artifact/BnqUN9XerZsqF5sepZtdy7. Undo: delete the artifact; revert this commit.

## 16:45 Voice picker, timing, flash, compact layout

Matt asked: pick the voice in the player (and pick another British woman), let the slide fade in before the voice, fix slides flashing full then re-revealing, drop the duplicate narrator caption, shrink the UI so it fits without scrolling.

---

### Slide flash cause

`show()` forced a reflow (to restart the slide fade) before adding the hidden `.rv` class to parts, so the browser had already painted them visible; adding `.rv` then *transitioned* them to hidden, and the reveal faded them back. Fix: add `.rv` before the reflow. Headless check: the last part's opacity stays 0 for the first 300 ms of a new slide.

---

### New British voice

Deepgram Flux has only one British woman (Gemma). Aura-2 has Pandora (British, calm, smooth); `tts.py` now routes `pandora` to Aura-2 on `/v1/speak` (speed works there too). Reel 03 bakes Pandora (default), Gemma and Maeve; Voice button / V key cycles and remembers the pick. Rejected: Aura-1 Athena (older model). Cost: one take + one transcript per voice.

---

### Timing and layout

- `beat.lead` 0.15 → 0.7 s, so the voice starts after the slide's fade.
- Captions hidden by default (CC button / C key), since the slide already has its own text.
- Controls ~half size; title smaller; the slide sizes to `100dvh - 150px`, so at 1100×900 the page is exactly one screen.
- Untested: very short windows (under ~600 px tall) and phones; the voices weren't heard by ear.
- Reel is 4.5 MB now (three voices).
