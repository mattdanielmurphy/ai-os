# Song Key pill: music only, easy to dismiss (2026-10-27)

## 03:00 Music-only gate and dismiss controls

**Asked:** the Song Key pill (Hammerspoon `modules/song_key.lua`) popped up for the scroll-to-read reel's voice. Make it fire only for music and easy to dismiss (Esc, click, auto-fade).

**Why it happened:** the pill showed for anything in macOS Now Playing. Reels register there (title = reel title, app = Claude desktop or a browser), so a spoken reel looked like a song.

---

### Speech check

The listener (`bin/song-key-listen`) now also reports `ler`: the share of 50 ms frames quieter than half the 20 s window's average. Speech pauses between words; music rarely drops out.

Measured on files on the Mac:

| Audio | ler |
|---|---|
| Reel voice (003, 004) | 0.48-0.51 |
| Reel voice over its music bed | 0.35-0.40 |
| Interviews, meeting recording, sound drops | 0.36-0.52 |
| Songs, jams, trap beat, vocal demo | 0.00-0.21 |

Threshold 0.3 (tweak `ear.speechLer`). Two of the last three readings must agree. Rejected: key strength and chroma flatness/stability (overlap too much); ML speech classifiers (Essentia TensorFlow models aren't installed, heavier).

---

### When the pill shows

- Apple Music or Spotify track found on Hooktheory/AcousticBrainz: shows at once.
- Anything else (browser, etc.): waits until the ear hears music (~8-12 s).
- Speech hides it; a quiet bar doesn't (no flicker).
- Claude desktop audio (reels) is ignored outright.
- If audio capture fails, it falls back to the old behaviour for songs found online.

The listener now runs while anything plays, not only while the pill is up, so it can decide before showing.

---

### Dismissing

- Click anywhere on the pill: hidden until the next song.
- Esc: works for the first 8 s after it appears (tweak `dismiss.escSeconds`), shown by an "ESC HIDES" chip. Limited so Esc isn't stolen from other apps the whole time music plays.
- Auto-fade after 25 s (tweak `dismiss.autoHide`, 0 = never).
- Opening Hooktheory moved to a small ↗ in the corner (click used to open it).

---

### Untested / risks

- Not tested live end to end: nothing was playing and it's ~3 am, so I didn't play audio on the Mac. Pure logic tested (`lua tests/song_key_test.lua`), the listener tested on real files, the module hot-reloaded cleanly, and with Chrome playing a spoken hypnosis track the pill stayed hidden.
- Singer-songwriter tracks with lots of silence could read as speech; raise `ear.speechLer` if a real song gets hidden.
- The keyboard's tonic colour in the pill is terracotta (`#e07a5f`), which breaks the colour rule; left alone because it's outside this ask.

**Undo:** `git -C ~/.hammerspoon revert 7670653`.

## 04:35 No Esc; hover Close like Trackpad Mixer

**Asked:** Esc is too common a shortcut; keep the self-fade; add click-to-close like Trackpad Mixer.

---

### What changed

- Esc removed entirely (and its "ESC HIDES" chip and tweak).
- Moving the mouse over the pill dims it and shows one big "Close" button, copied from Trackpad Mixer's hover overlay. It acts on mouse release. Only real mouse movement shows it, so a pill that appears under a resting cursor stays clean.
- Clicking anywhere else no longer hides it (matches the mixer). The ↗ corner still opens Hooktheory and sits above the dim layer.
- Auto-fade stays at 25 s, but waits while the mouse is over the pill so it doesn't vanish under your cursor.

---

### Untested

- Rendered and hover-tested in headless Chrome. Not tested in the real Hammerspoon pill with the mouse, since that needs input on the Mac. Piano HUD uses hover in the same kind of window, so it should work.

**Undo:** `git -C ~/.hammerspoon revert HEAD`.
