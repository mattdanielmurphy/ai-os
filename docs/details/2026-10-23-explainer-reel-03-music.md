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

## 16:55 Reels for every agent

Matt: reel 03 is "good enough for primetime"; agents with a lot of info should use reels. Asked: overhead vs text, can he just tell an agent to use it, and add a global rule. Future ideas: fresh generated music every reel; streamline the graphics.

---

### Can agents use it now

Yes, on his Mac. The reels branch was never on `main`, so other agents couldn't find it. I merged main into it (one rules conflict: kept both the "No Claude-default look" and "exemplars" lines; LEAF.md regenerated), pushed to `main`, and fast-forwarded `~/projects/ai-os`. The README's "Make a reel" now describes the hand-written `slides.py` route (no Figma needed). Cloud sessions without the Mac's Deepgram key can't build reels.

---

### Overhead vs text

Measured on reel 03: slides are ~15 KB of SVG-writing Python (≈ 4–5k output tokens), the script ~200 words, build ~1 min per new voice (Deepgram: a few cents per voice), test ~15 s. A text reply of the same content is ~300 tokens. So a reel costs roughly 10–15× the tokens of a text reply, nearly all of it the slides. The streamlining idea (shared layout kit + short JSON per beat, ~1k tokens) is in IDEAS.md.

---

### Rule added

`.rules/core_safety.md` under "Every Word Costs Matt" (compiled into CLAUDE.md, GEMINI.md, AGENTS.md, LEAF.md), a line in `~/.claude/CLAUDE.md`, and memory `explainer-reels-for-big-replies.md`. Short answers stay text.

## 17:00 Reels in cloud sessions

Matt: "fix this" (cloud sessions couldn't make reels).

---

### Cloud key fix

Cloud environments support **network secrets**: the key is stored on the environment, never enters the VM, and Anthropic's proxy attaches it to requests for the listed host (docs: code.claude.com/docs/en/cloud-environments#add-network-secrets). Matt adds one: host `api.deepgram.com`, header `Authorization`, prefix `Token`, value = his Deepgram key. I can't add it (his secret, his settings). Rejected: a plain env var (readable by anything in the VM) and a VPS proxy (more moving parts, still needs a token in the cloud).

---

### Code changes

- `tts.py`: no key + `CLAUDE_CODE_REMOTE=true` → send no Authorization header (proxy adds it); a 401/403 then explains the missing network secret.
- `build.py`: ffmpeg from PATH or pip `imageio-ffmpeg`; durations parsed from ffmpeg (no ffprobe); missing music → `music/default.m4a` (3.5 MB, 96k copy of Piano Airports 04).
- `test.sh`/`headless_test.cjs`: `package.json` pins playwright-core 1.61.1; installs with bun on Mac, npm in cloud; Chromium from Playwright in cloud.
- Rule + README updated.

---

### Cloud tested how

Simulated on the Mac (fake HOME, `CLAUDE_CODE_REMOTE=true`, ffmpeg hidden in a venv): no-key request gets the network-secret message; pip ffmpeg reads durations; build falls back to the bundled loop. **Not run in a real cloud session yet** (needs the secret first); Playwright's Chromium and npm install there are untested.
