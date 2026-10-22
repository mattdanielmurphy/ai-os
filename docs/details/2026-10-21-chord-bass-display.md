# Live chord / bass note display (idea)

## 23:35 Approaches for a live chord / bass HUD

What Matt asked (via coordinator): while he jams to songs, show the current chord, or at least the bass note, next to the song key detector. Sketch 2-3 approaches with feasibility; build only on "make it". Also record the classical score-following "vision" without building it.

What I found: the Song Key HUD (`~/.hammerspoon/modules/song_key.lua`) already has a live ear: `bin/song-key-listen` taps system audio with audiotee and runs Essentia on 20 s windows every 4 s, printing HPCP (pitch-class profile). The Piano HUD (`modules/piano_hud.lua`) already names chords from MIDI and has chord-naming code. So most of the plumbing exists.

Recorded both ideas in `~/.hammerspoon/IDEAS.md` (committed and pushed).

---

### Approach A: extend the listener

Add a second fast loop to `song-key-listen`: ~0.5-1 s windows, Essentia `ChordsDetection` on HPCP for the chord, and pitch of a low-passed band (below ~250 Hz, e.g. pYIN/`PitchMelodia` or just the strongest low chroma bin) for the bass note. Emit JSON lines; the Song Key pill gets a third line, or a sibling pill.
- Feasibility: high. Everything is already installed; maybe a day.
- Accuracy: bass note good on clear mixes; chords roughly 60-70% right on busy pop (triads only, misses 7ths/sus, flickers). Smoothing + "snap to the song's key" (we know it) helps a lot.
- Latency: ~0.5-1 s behind the music. Fine for "what's the chord", too late to play on the downbeat.

---

### Approach B: look the chords up instead

Hooktheory (already queried for the key) has human chord transcriptions for many songs; Chordify has them for most YouTube songs. Fetch the progression and step through it in time with playback position from nowplaying-cli.
- Feasibility: medium. Getting the chords is easy where they exist; syncing them to the recording (intro length, tempo) is the hard part and needs beat tracking or alignment.
- Accuracy: much better chords (real 7ths, inversions) when the song is covered; nothing when it isn't.
- Could show "coming next" chords, which A can't.

---

### Approach C: existing apps

Chordify (web), Moises and Capo (Mac) already do chord detection with a playback view. None listen to whatever is playing system-wide; you have to load the song into their player. Worth trying first if he only jams to a few songs.

---

### Recommendation

Start with A, bass note first (most reliable), chord second, snapped to the known key. B later as an upgrade for songs Hooktheory covers. Nothing built yet.
