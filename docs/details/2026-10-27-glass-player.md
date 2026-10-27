# Glass TV's own player (Glass Player)

## 13:55 Built Glass Player and merged it

**Asked:** how hard it would be to give Glass TV its own player as nice as IINA, then build it in a worktree and merge after the polish thread.

---

### How hard it was

IINA is a Mac shell around mpv, and mpv (with libmpv) was already installed through Homebrew. So the player uses the same engine and plays the same files. The work was the shell: a window, controls, keys and X-Ray. About a day for the essentials; IINA's extras (picture-in-picture, seek thumbnails, playlists, a big settings window) would be weeks and aren't needed for Glass TV's one-file-at-a-time flow.

---

### What was built

- `app/player/main.swift`: a Swift app that draws video with mpv's OpenGL render API on a CAOpenGLLayer, the same approach IINA uses. Built by `build-player.sh` into `bin/Glass Player.app`; `build.sh` now calls it.
- It takes the same arguments Glass TV gave `iina-cli` (`--mpv-input-ipc-server`, `--mpv-start`, `--mpv-fs` …), so `src/player.ts` drives it over the same JSON socket: position tracking, credits detection and quitting at the credits are unchanged.
- Controls: a dark frosted bar that fades after 2.5 s (tweak `player.controlsHideSeconds`): back/forward 5 s, play/pause, scrubber with chapter marks and a time bubble on hover, elapsed and remaining time, volume (remembered), audio and subtitle menus (hidden when there's nothing to pick), full screen. Title top left.
- Keys: Space, ← → (5 s), ⇧← ⇧→ (30 s), ↑ ↓ volume, M, S, A, F, Esc. Listed in the Playback menu; every button has a tooltip with its key (discoverable).
- Click pauses, double-click toggles full screen, scroll changes volume.

---

### X-Ray kept working

Glass Player asks `/api/xray` on pause and shows the plugin's own `overlay.html` in a see-through web view, with a tiny stand-in for IINA's message API, so there is one overlay page for both players. Key hints are moved up above the control bar. The web view is created on the first pause and released after 3 idle minutes to save memory.

Decision: hardware decoding uses `videotoolbox-copy` instead of plain `videotoolbox`. Plain mode can't produce the paused-frame screenshot X-Ray needs (tested: "Input image format videotoolbox not supported"). Copy mode still decodes on the GPU; it costs a little memory bandwidth.

---

### IINA as a fallback

Settings has a new **Player** line: tap to switch between Glass Player and IINA (`settings.useIina`). If Glass Player isn't built, Glass TV falls back to IINA automatically.

---

### Tested

- Played a generated 3-minute test episode (two audio tracks, subtitles, a Credits chapter): video renders, controls and chapter marks show, IPC properties read correctly, screenshot for X-Ray works.
- X-Ray against a stand-in server: two name tags drew in the right places.
- End to end through a separate test copy of Glass TV: play from the library, position tracked, credits at 150 s detected from the chapter, the player quit itself at the credits and Glass TV recorded it as finished.
- Unit tests: 20 pass.

**Not tested:** a real streamed episode from Real-Debrid, real-face X-Ray inside Glass Player, full screen on a second display.

---

### Live status and undo

- Merged into `master` and pushed. Glass Player is built in `~/projects/glass-tv/bin/`.
- Matt was watching something when it merged, so the server restarts by itself once nothing is playing (`tmp/restart-when-idle.sh`); the episode after that opens in Glass Player.
- Undo: Settings → Player → tap to pick IINA, or `git revert 15fec43`.

## 14:08 Subtitles, full-screen scaling and transitions

**Asked:** subtitles off by default; full screen should fill the screen, with native resolution as an opt-in setting; the full-screen transition squished the picture to the left (his screen recording, ui-recorder 14:05).

---

### Why full screen didn't fill

The recording showed the picture staying window-sized in the middle of the full screen, and a squished frame at the left during the animation. Cause: the player sized each frame from OpenGL's viewport, which kept the old window size after a resize. It now sizes frames from the layer itself (points × backing scale). The layer also keeps the last frame's shape (`resizeAspect`) while the animation runs, so it can't squish between frames.

---

### Subtitles and native size

- Subtitles start off (`sid=no`); S or the subtitles menu turns them on.
- New Settings line under Player: "Show video at its own resolution", off by default. On, it passes mpv's `video-unscaled=downscale-big` (never upscaled, still shrinks to fit).

---

### Tested and not

- Built, typechecked, 20 unit tests pass, settings page bundles.
- **Not tested in full screen:** the clearance banner wasn't reachable (Hammerspoon down), so I didn't take over his screen. The server restarted by itself at 14:07 when nothing was playing, so the next video uses the fixes.
- Undo: `git revert 020241d 494b19b`.
