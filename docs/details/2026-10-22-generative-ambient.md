# Claude-driven generative ambient music

## 23:15 First experiments

What Matt asked: beautiful ambient music made by Claude playing real instruments (Arturia
Augmented Grand Piano, Cardinal patches with good control schemes), as lightly as possible on
his Mac; also whether a minimal Ableton default set cuts its ~2.1 GB idle memory. Separate
project from the explainer reels, which will use it as background music.

---

### Piano renderer works

New private repo `~/projects/claude-ambient` (github.com/mattdanielmurphy/claude-ambient).
`compose.py` writes a note list (Eno "Music for Airports" method: six voices, each looping a
1-3 note phrase on its own loop length, 17.9-31.9 s, so overlaps never repeat; D-flat major
pentatonic, soft velocities, tiny timing jitter). `render.swift` hosts the Augmented Grand AU in
AVAudioEngine offline manual-rendering mode, sends the notes, adds Apple Large Hall reverb,
writes a WAV; ffmpeg fades in and normalises to -20 LUFS. Silent: nothing hits the speakers, so
no take-control banner needed. A 3-minute piece renders in about 10 s. I have not listened to
it (can't); loudness and peak checks show real signal. It uses the plugin's default preset.

---

### Renderer memory cost

Peak ~440 MB for the few seconds it runs, zero when idle. Compared with keeping Ableton open,
this is the lightest real-instrument path. Rejected for now: Reaper (not installed, paid,
its headless CLI render is great but only needed for full mix chains); VCV Rack headless
(plays to the audio device in real time, not to a file).

---

### Minimal Ableton set halves memory

Measured with `measure_live.sh` (opens Live, idles 75 s, reads phys_footprint, the number
Activity Monitor shows, then quits). His Default.als template (3 MIDI tracks, 2 audio, 2
returns, 9 AU plugins incl. Augmented Grand, Timeless 3, Pro-R 2, Saturn 2, Pro-Q 4):
**1.80 GB**. Ableton's factory empty set: **0.88 GB**. Helpers add ~70 MB. So ~0.9 GB is
Live itself; the rest is his plugins. I did not change his default template: that's his call.
Undo: nothing to undo; Live was quit both times.

---

### Take-control slip

I took clearance (light banner, ticket t12) for both Live launches. Between runs the ticket
already read "done" (it seems to have ended early) and my script carried on into the second
launch without re-checking. The second launch happened without an active grant.

---

### Cardinal is blocked

Cardinal `.vcv` files are zstd tars of `patch.json`, easy for Claude to write. Setting the AU's
state didn't load a patch, but pointing HOME at a temp folder whose
`Documents/Cardinal/templates/synth.vcv` is the patch does load it (log confirms). Even a plain
VCO-to-output patch renders silence in the offline host, so something in Cardinal's AU
doesn't process there. Also noted: `/Library/Application Support/Cardinal` is missing (the AU
complains about the install). Next tries: host Cardinal in Element or Ableton, or debug the AU.

## 07:15 Cardinal works after reinstall

Matt reinstalled Cardinal. `/Library/Application Support/Cardinal` now exists, and that was the
cause of the silence: the same plain sine patch that rendered silent now peaks at 0.58.

---

### Omri patch renders

`patches/omri-beginner-cardinal.vcv` (converted) loads every module (Bogaudio, Surge XT LFOs,
Surge XT Delay swap) and renders 68 s at -24 LUFS raw, peak 0.21, driven by the 60 s note score.
Saved as `~/projects/claude-ambient/out/omri-beginner-cardinal-01.m4a` (normalised to -20 LUFS;
`out/` is gitignored). Nobody has listened yet; only levels checked. A harmless assertion about
MIDI output being unsupported in the AU shows in the log. Did not open Cardinal's GUI (no screen
input needed). README updated with the working command.
