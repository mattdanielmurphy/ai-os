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
