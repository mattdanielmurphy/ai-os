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
