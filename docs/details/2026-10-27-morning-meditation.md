# Morning meditation + hypnosis (2026-10-27)

## 02:45 Meditation and hypnosis tracks built

**Asked:** add a guided mindfulness meditation to the morning check-in (secular, science-driven teacher style, calm Speechify voice, a generative ambient bed with no AI music), plus one deep-relaxation hypnosis track. Give play links.

---

### Two tracks are live

Player page: https://matt-pages.vercel.app/3a22db06-7d4d-4779-adde-1e377c22caa3/ (`#morning` and `#hypnosis` jump to each).

- **Morning mindfulness**, 10 min 19 s, voice Douglas (Speechify, tagged relaxed/meditation, American), speed 0.88.
- **Deep relaxation** (hypnosis), 22 min 21 s, voice Marian (Speechify, soft British female, tagged meditation), speed 0.84.

---

### Music is not AI

Both beds come from `~/projects/claude-ambient/out/`: the 20-minute "Breath" loop (meditation) and the 22-minute "Magicicada" loop (hypnosis). They're real Arturia Augmented Grand Piano notes written by a Python score and rendered by an Audio Unit host, the same way as the Oct 22–23 ambient pieces. No generative-audio model is involved, so they fit the no-AI-music rule. I didn't add nature sounds: there's no non-AI field-recording source on hand, and the Breath loop is already the calm, sparse one.

---

### How the script was written

Meditation: original text in the style of a secular attention teacher. Breath anchor, then the key idea that noticing the wandering is the rep (cites the mind-wandering research finding that we're off-task nearly half the time), then sounds, thoughts as events that just appear, body check, open awareness, an intention for the day, and a gentle exit. No spiritual claims.

Hypnosis: safety line first (don't use while driving), three breaths, progressive relaxation head to feet, a 10-to-1 deepening count, staircase to a self-chosen safe place, four simple suggestions about calm, ~4.5 minutes of quiet music, then a 1-to-5 count back up to alert. It ends awake, not asleep, since it's for relaxation.

---

### How it's built

`services/checkin/meditation/build.py` reads a script (one spoken line per line, `[pause N]` for music-only seconds), voices each line once via `services/reels/tts.py` (cached by text, so edits re-record only changed lines), places them on a timeline, lays the loop under them at -13 dB, ducks the music ~4 dB while the voice speaks, and normalizes to -18 LUFS (quiet, for headphones). Pauses measure about -30 dB mean; speech about -20 dB.

---

### Check-in page change

The Breathe step now has a secondary button "Or a 10-minute guided meditation" that opens the player page at the morning track in the browser (an Artifact page can't host the audio). Tapping it saves `meditation: true` in that day's page doc and the Done summary shows it. The daily job rebuilds the page from the template each morning, so it appears from tomorrow's check-in. Tests (ladder, daily, missed) pass.

Rejected: making the meditation a mandatory step (would lengthen every check-in; the habit ladder should grow it slowly instead), and embedding the audio in the Artifact (unreliable on iPhone, big asset).

---

### Not tested yet

I checked the files, levels and that the page serves them (HTTP 200, audio/mp4), but I haven't listened all the way through. Lock-screen playback on the iPhone is untested.

**Undo:** revert commit f5a79ae5 in ai-os (removes the button); the page lives at `~/projects/pages/site/still`.

## 03:05 Voice was a joke, ducking too strong

**Matt said:** the Douglas voice is a hilariously bad fit (keep it as "Meditation attempt #0" for his brother), Marian is not too bad, and the ducking made the music vanish whenever the voice spoke. He'll pick a voice in the Speechify playground.

---

### Attempt zero is kept

The page now lists the morning track as "Meditation attempt #0" (an outtake), same audio and link (`#morning`).

---

### Ducking is now a fixed 3 dB dip

Cause: a sidechain compressor at ratio 5 with a low threshold, plus loudnorm in one-pass mode, which rides the gain like an automatic level control. Together they pulled the music way down under every line. Now `build.py` draws a volume envelope: the music dips exactly 3 dB (`DUCK`), fading in 0.8 s before a line and out 2 s after (`DUCK_IN`, `DUCK_OUT`), and loudness is one static gain measured over the whole mix. The hypnosis track is rebuilt with it (music sits about 10 dB under the voice and no longer disappears).

---

### Check-in button hidden for now

The "Or a 10-minute guided meditation" button on the check-in page is hidden until there's a real meditation with a voice Matt picked, so he doesn't get the joke version at 7:45. Un-hide by removing `hidden` from `#bmed` in `services/checkin/template.html`.

---

### Next step waits on Matt

Once he names a voice from the Speechify playground, rebuild with `build.py scripts/morning-mindfulness.txt` after changing its `# voice:` line (it renders to a new file name so attempt #0 stays), add it to the page and un-hide the button.

## 04:40 Meditation attempt #1

**Matt asked:** for a second meditation attempt now, instead of waiting for a voice pick.

---

### Attempt one uses Marian

Same script as attempt #0, read by Marian (the voice he called "not too bad") at speed 0.86, so it runs 11 min 53 s. Same Breath piano loop, with the new gentle 3 dB ducking. Script: `services/checkin/meditation/scripts/meditation-attempt-1.txt`. It's the top track on the page (`#morning`); attempt #0 moved to `#attempt0`.

---

### Music a bit louder

Bed raised from -13 to -10 dB (`MUSIC_DB` in `build.py`), because the sparse Breath loop sat almost 20 dB under the voice. Music peaks now land about 12 dB under the speech. The hypnosis track was not rebuilt with this.

---

### Check-in button back on

The check-in page's Breathe step shows "Or a 12-minute guided meditation" again, linking attempt #1. It appears from tomorrow's check-in. To hide it again, add `hidden` back to `#bmed` in `services/checkin/template.html`.

---

### Still untested by ear

Levels checked; I haven't listened through it.

## 04:50 Smoother, quieter voice

**Matt said (about Deep relaxation):** the voice is too loud against the music and loud overall; it sounds a bit artifact-y (blamed the slowed speed); maybe run a subtle FabFilter or similar over it.

---

### Speed back to natural

Both Marian tracks (hypnosis and meditation #1) now use speed 1.0, so Speechify sends no rate change and reads at its natural pace. Slowing it (0.84–0.86) was the likely source of the artifacts. They got shorter: hypnosis 21 min, meditation 11 min.

---

### FabFilter on the voice

New `fx.swift` hosts Audio Units offline (same approach as claude-ambient's `render_mix.swift`) and runs the voice bus through `voice_fx.json`: Pro-DS de-esser (4 dB max), Pro-C 2 in Clean style (threshold -26 dB, low ratio, soft 24 dB knee, auto gain) to even it out, and Pro-R 2 as a small, dark room at 11% mix to soften the TTS edges without mud. Plus a 70 Hz low cut. Edit `voice_fx.json` to change any of it; `swift fx.swift --list aumf:FC2p:FabF` prints a plugin's parameter names.

---

### Levels

Music raised from -10 to -2 dB under the voice (`MUSIC_DB`), so voice peaks now sit about 8 dB above the music instead of 12+. The whole track is now -21 LUFS, about 5 dB quieter than before. Also fixed a hidden cause of extra loudness: ffmpeg's `alimiter` auto-levels by default, which had pushed earlier renders ~2 dB over target.

---

### Not changed

Attempt #0 stays as it was (the joke). Untested by ear.

## 12:50 Voice louder, plus a plan for drone, chimes and levels

Matt listened to meditation #1 (Marian): much better, but the voice is a touch too quiet against the music. He also wants a never-wavering drone, guiding chimes the voice introduces, difficulty levels, and a clear line between breathing exercises and mindfulness.

---

### Voice is louder now

The music bed sits 2.5 dB lower under the voice (`MUSIC_DB` in `services/checkin/meditation/build.py` went from -2 to -4.5). The voice itself and the final loudness (-21 LUFS) are unchanged, so the whole track doesn't get louder, only the balance moves toward the voice. I picked 2.5 dB because "a touch" usually means 2-3 dB, and the last two moves were 3 dB each way. Undo: set `MUSIC_DB` back to -2 and rebuild.

---

### Drone that never wavers

Add a third layer under the piano bed: one sustained drone on the loop's root (and maybe its fifth), rendered from a real synth Audio Unit like the rest of claude-ambient. It is never ducked, never faded except at the very start and end, and sits at a fixed level. Only the piano layer dips under the voice. The artistic piano bed stays as it is on top.

---

### Chime the voice introduces

Early in the script the voice says something like "when you hear this sound, take it as a reminder to come back to the breath", then plays the chime once. After that a `[chime]` tag in the script (or an automatic interval) plays it. The chime would be a soft bell or bowl tone from a real instrument (Arturia Augmented Mallets is already installed), not a generated sound.

---

### Difficulty levels

One script, many levels. Each level sets: total length, how long the silences are (a multiplier on every `[pause]`), how much instruction (lines tagged with the highest level they appear in get dropped above it), and how often the chime plays. Example: level 1 = 5 min, chime every 30 s, lots of guidance; level 5 = 20 min, chime every 3 min, mostly silence. The build makes one track per level and the player page gets a level picker.

---

### Breathing is not mindfulness

Mindfulness scripts get at most two or three settling breaths at the start, then the voice hands the breath back ("let it do whatever it does on its own") and never directs it again. Attempt #1 already does this. Breath-pacing (sounds that guide in and out) becomes a separate kind of track, a breathing or relaxation exercise, never mixed into a mindfulness session.

---

### Untested and open

The voice change is rebuilt and on the page, but nobody has listened to it yet. Nothing in the plan above is built.

## 13:45 Difficulty slider, drone and bell are live

Matt asked for a difficulty slider on the page that starts at one minute, and said to build everything now.

---

### The slider has eight levels

The Still page has a new card at the top, "Sit with the bell", with a slider from level 1 to 8. Each level is its own pre-built track; moving the slider swaps the track and the line under it says how often the bell rings and how many reminders there are. The page remembers your last level on that device.

| Level | Length | Bell every | Reminders during the sit |
|---|---|---|---|
| 1 | 1 min | 15 s | none |
| 2 | 2 min | 20 s | none |
| 3 | 3 min | 30 s | 1 |
| 4 | 5 min | 45 s | 3 |
| 5 | 7 min | 1 min | 3 |
| 6 | 10 min | 90 s | 3 |
| 7 | 15 min | 2 min | 2 |
| 8 | 20 min | 3 min | 2 |

Short levels can't fit many bells around the talking, so level 2 rings 3 times and level 3 rings 3 times. Levels 1 to 3 use one settling breath; 5 minutes and up use two, then hand the breath back.

---

### Drone that never wavers

A KORG Alexandria organ holds D, A and D under the piano for 21 minutes, softened with a low-pass. Its level moves by about 1 dB over the whole track, it never dips under the voice, and it sits about 10 dB below the piano. I chose the organ because the pad and analog synths I tried swelled or faded over time (measured, not listened to). If it's too loud or quiet, the knob is `DRONE_DB` in `build.py`.

---

### The bell

Arturia Augmented Mallets, preset "Gentle Bells", one high A that fades in about 5 seconds. The voice introduces it ("When you hear this sound, take it as a reminder. If your mind has wandered, gently come back to the breath."), rings it once, and after that it rings on a steady grid during the silences, never over the voice. Volume knob: `BELL_DB`.

---

### How it's built

`levels.py` writes one script per level. `build.py` learned `[bell]`, `[fill]` (silences that stretch so the track hits its exact length), `# drone:`, `# bell_every:` and `# fade_out:`. Rebuild everything with `python3 levels.py` then `build.py scripts/level-N.txt`.

---

### Not listened to yet

I can't hear the audio, so the drone and bell levels are set by measurement only. The drone could be too present, and the bell might feel too loud or too quiet against the piano. Tell me which and I'll move one knob.

## 12:40 (Oct 28) Meditation is now the first step of the check-in

The coordinator passed on Matt's ask: the morning check-in must start with the level 1 guided meditation (1 minute), and the level should move up and down on its own with use and consistency.

---

### First step of every check-in

The check-in page now opens on "Sit": today's guided track plays right inside the page, then Breathe, Grateful, Recall and Talk follow as before. The old "Or an 11-minute guided meditation" link is gone. Today's page was republished with it, so it's live now.

---

### It moves up and down by itself

It's a habit on the existing ladder (`ladder.json`, `meditation`, levels 1, 2, 3, 5, 7, 10, 15, 20 minutes), on its own weekly clock like the study block:
- Up one level after a full week of finishing the track every day.
- One missed check-in day undoes the newest step up; two or more missed days drop everything back to the smallest version, so meditation goes back to 1 minute.
- Stopping early two days in a row eases it down a level (the page saves the whole minutes heard).
I kept the ladder's weekly pace rather than inventing a faster one, so 20 minutes is at least seven weeks away.

---

### Audio inside the check-in page

Claude pages can't load audio from other sites, and their file store only takes images and video, so each level track is stored as an mp4 with a tiny still frame (80 kbps, 0.6 MB for 1 minute, 12 MB for 20). The page now also declares the `assets` capability. The track ids are in `services/checkin/meditation/assets.json`.

---

### Untested on the phone

I checked the page flow headless (Sit shows first, Next goes on to Breathe, no errors) and the ladder with tests, but I haven't heard the track play inside the real Claude page on the iPhone. If it doesn't play, tell me.
