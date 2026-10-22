# Capture Audio (rolling system-audio buffer) — details

## 09:45 Existing tools vs proof of concept

What Matt asked: a Capture-MIDI-style rolling buffer of all system audio except Apple Music; a HUD button appears
after audio plays; clicking it opens a picker to grab a clip. Simple proof of concept, plus an honest check on
whether it's a bad idea or hard.

---

### Audio Hijack already does most of it

Installed: Audio Hijack 4.5.5, Loopback 2.4.10, BlackHole 16ch. Audio Hijack 4.1+ lets the System Audio block
exclude sources, so "all system audio except Music" is one block
([Rogue Amoeba 4.1 notes](https://rogueamoeba.com/company/lists/archives/press/2023-01-20-audiohijack-410.html)).
Its Time Shift block keeps a live buffer you can pause and rewind ([podfeet](https://www.podfeet.com/blog/2022/04/audio-hijack-4/)).
What it lacks: a "save the last N seconds" button. Workaround: a session System Audio (exclude Music) → Recorder
that runs all the time, then trim the file afterwards. Costs disk (~1 MB/min as AAC), zero code.
Caveat: a separate thread is looking at Audio Hijack interfering with Matt's mixer; an always-on session might
make that worse.

No dedicated Mac app found for retroactive system-audio capture (AudioBuffer and Pretake are iPad apps for
mic input; Retrocord is a $399 interface recorder).

---

### Custom build is moderate, not hard

macOS 15.7 has Core Audio process taps (14.2+): a global tap that excludes chosen processes (Music.app) with no
virtual driver. Pieces:
1. Swift helper: tap + in-memory ring buffer (5 min stereo 48 kHz float ≈ 115 MB; Int16 ≈ 58 MB). Writes the
   last N seconds to a WAV on request. Small, well-trodden (AudioCap sample code exists). One sitting.
2. Silence detection → show HUD button via Hammerspoon in its own slot. Small.
3. Picker with waveform and a drag selection. This is the rabbit hole; a crude version is "last 10/30/60 s"
   buttons, no waveform.
Risks: first run asks for the "System Audio Recording" permission; the tap must ignore Apple Music even when it
plays through Ableton? (No: it only excludes the Music process.) Memory and CPU cost are small.

---

### Recommendation

Step 1: try Audio Hijack (System Audio excluding Music → Time Shift → Recorder) for a few days.
Step 2, only if he keeps wanting it: Swift tap + ring buffer + "save last 30 s" HUD button, no waveform picker.
Rejected: building the waveform picker up front (rabbit hole), BlackHole/Loopback routing (changes output device,
fights the mixer).

Undo: nothing changed except IDEAS.md and this file.
