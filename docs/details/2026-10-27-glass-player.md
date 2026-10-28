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

## 18:30 Stremio add-ons

**Asked:** add support for Stremio add-ons to Glass TV.

---

### What add-ons do now

Glass TV already used two Stremio add-ons hard-coded (Cinemeta for catalogs, Torrentio for streams). Now any add-on works: Settings → Stremio add-ons takes the same link you'd paste in Stremio (`manifest.json` URL or `stremio://` link), checks its manifest, and lists it with what it does and a Remove button. Code: `src/addons.ts`, routes `/api/addons`.

- **Streams:** every add-on with streams for that title is asked alongside the built-in provider; all results are ranked together by the existing quality ranking, so the best playable link wins.
- **Subtitles:** OpenSubtitles comes installed. When a remote episode or movie plays, up to 6 subtitles (3 English, 1 per other language) are added to the player's subtitle menu, named like "English 2 (OpenSubtitles v3)". They are never switched on by themselves.
- **Search:** add-ons whose catalogs support search add results TMDB and Cinemeta missed (IMDb-id titles only, since Glass TV plays by IMDb id).

---

### Limits worth knowing

- **Torrent-only add-ons can't play by themselves.** Glass TV has no torrent client, so it only plays web links. An add-on like Torrentio needs its debrid-configured link (set up on its site with Real-Debrid) to be useful. Unconfigured Torrentio added for the test gave 10 torrent results, all skipped.
- **Catalog browsing isn't on the home screen.** Add-on catalogs only feed search, to keep the anti-binge home (your shows first, trending folded away). Shelves from add-ons could come later if wanted.
- Add-ons with non-IMDb ids (anime kitsu ids, live TV channels) are ignored for now.

---

### Tested

- 22 unit tests pass (2 new: link normalising, which add-on handles what).
- Against a test copy of the server: added Cinemeta via a `stremio://` link, a bad URL gave a clear error, Torrentio added; search for "Nathan for You" merged results; streams for Nathan for You S1E1 came from both sources and ranked; OpenSubtitles returned English, Russian, Spanish and Polish subtitles; all 6 loaded into the player engine unselected.
- Settings section checked in light and dark (headless).
- **Not tested:** the add-on subtitles inside a visible Glass Player window (Hammerspoon was unreachable for screen clearance; tested with the same engine headless).
- Live: server restarted at 18:28 while nothing was playing. Undo: `git revert 3f7404a`.

## 19:40 Explore feed, peek, scrollbars and IMDb browser

**Asked:** Explore should come from Cinemeta and any catalog add-on (replacing TMDB trending), not be folded, peek below a library that fills the first screen with a hero, macOS scrollbars, and an IMDb button opening a clean in-app browser.

---

### Explore from add-ons

Explore now lists every catalog of every installed add-on that needs no extra input (Cinemeta's Popular and Featured, plus your Netflix, HBO Max, Disney+ and Prime Video shelves from the catalog add-on you added), then genre shelves from the first catalog that offers genres (knob `home.exploreGenreRows`, default 8; `home.explorePerShelf`, default 20). Titles already in your library are left out. Cinemeta is now a default add-on (installed once; removing it keeps it removed). A new catalog add-on shows up here by itself. Shelf labels name the add-on when more than one add-on fills Explore. The old TMDB trending is gone from home (TMDB still powers search and artwork).

---

### Unfolded with a peek

Explore is a normal section now, no fold. The library area takes at least the first screen minus a peek (`ui.explorePeek`, default 190 px), so Explore's heading, first shelf label and the tops of its posters show at the bottom. The hero that fills that space is still to come (three options being made).

---

### Scrollbars

The rows had `scrollbar-width: thin`, which draws WebKit's old non-native bar. Removing it gives the normal macOS overlay scrollbars (they appear while scrolling, per System Settings).

---

### IMDb button and clean browser

Hovering a poster shows a small IMDb button (top right). It asks the server for the title's IMDb id (own id, Cinemeta id, or a TMDB lookup) and opens it in a reusable in-app window (`app/browser.swift`): about 40 ad and tracker hosts are blocked with a WebKit content blocker, IMDb ad slots, "More like this", news, video gallery, sign-in promos and the footer are hidden, videos don't autoplay. Back/forward/open-in-browser buttons sit in the title bar (⌘[ ⌘] work, Go menu). Outside the app it opens a normal browser tab.

**Not verified:** how clean IMDb actually looks. IMDb shows a robot check to automated browsers, so I couldn't load it in a test; the hidden-element list is best-effort. Tell me what still distracts and I'll hide it.

---

### Tested

Explore API returned 10 shelves of 20; IMDb link lookup worked; home checked headless in light and dark (peek visible, IMDb button on hover, no errors); 22 tests pass; app and player build. Live at 19:38 (server restarted while nothing played; app reinstalled). Undo: `git revert 80f67e3`.
