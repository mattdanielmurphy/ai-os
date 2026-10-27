# Glass TV: bigger colour posters, tap to play

## 07:58 Poster grid changes

**Asked:** turn off the black-and-white default look, much bigger posters with less space between, IMDb rating under each poster, click a poster to start playing without adding it to the library.

### Black and white look removed
The trending shelf used a `.quiet` greyscale filter until hover. Removed from `web/base.css`; the trending note now says "Tap a poster to play it."

### Bigger posters, tight gaps
Rows: 120px → 220px columns; grids: 110px → 200px min; gap 12px → 6px. App width 1100 → 1400px. Also fixed an old bug where `body{max-width:1040px}` from base.css beat the override in app.css (so the app was stuck near 1000px wide).

### IMDb rating underneath
Score moved from a badge on the poster to a line under it. Ratings now also load for local files, trending and search results (before: library only). Each lookup gets 2.5 s; slow ones keep caching in the background and appear on the next load. Unreleased titles have no IMDb score, so they show none.

### Tap to play
Any poster plays on click. The server builds the title on the fly (`toItem` in `src/server.ts`) without saving it to the library, and remembers it in memory so "play the next one" and break-glass extras still work until the server restarts. Tonight's plan, tokens and the break-glass rules are unchanged (play still goes through `canPlay`). "+ library" is now a small text button under the poster, optional. "Pick episode" shows on every TV poster.

### Trade-off
Titles played without adding them won't show in "Pick up where you left off" (that shelf reads the library). Progress is still saved, so adding it later picks up where you were.

### Tested
Unit tests pass. Scratch server with fake player: trending ratings filled in (40 of 48, the rest unreleased); clicking Interstellar in trending started playback; library count unchanged. Live server restarted and serving the new page. Not tested in real IINA.

### Undo
`git revert 813fc20` in ~/projects/glass-tv, then `glass restart`.
