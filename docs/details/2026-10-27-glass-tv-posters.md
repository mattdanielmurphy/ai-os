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

---

## 08:00 Black-and-white as a setting, more tweaks

**Asked:** keep the black-and-white look as a setting, and put a lot more in the Tweaks menu.

### Black-and-white switch
Settings → Look → "Black-and-white trending posters" toggle, off by default. Saved in `state.json` (`settings.greyTrending`), so it survives restarts. Only the trending shelf goes grey, colour returns on hover, same as the old look.

### New tweak knobs (18)
Poster width (rows), library grid poster size, gap, corner rounding, app width, IMDb score on/off, score text size, hover outline, toast time, search delay, B&W strength, B&W fade, B&W fade-back time, hold-to-commit seconds, voice search length, "Pick up where you left off" count, trending titles per genre (up to 20), how long the page waits for IMDb scores. UI knobs apply on the next screen refresh. Rejected: putting the B&W on/off in tweaks too, since he called it a setting.

### Note
Hold-to-commit time is now tweakable (0.5–5 s); it's part of the anti-binge flow, so it's his call to lower it. Trending per genre above 12 needs the 12-hour trending cache to expire first.

### Tested
Settings toggle on/off in the scratch app (posters went grey / back to colour), a knob change showed up live, unit tests pass, live server restarted. Not checked inside the ⌃⌥⌘T panel itself.

### Undo
`git revert 973be76` in ~/projects/glass-tv, then `glass restart`.

---

## 08:10 Break-glass final button, Mac shortcuts

### Final spend-or-decline button
**Asked:** after the 5-minute wait, one more press to continue vs decline; the token is only ever lost on that final press.
**Before:** when the countdown hit zero the page auto-claimed, spending the token, then showed an "unlocked" screen.
**Now:** at zero the wait screen shows "Spend 1 token and watch <title>" (or "…and pick one more" when there's no episode to continue) next to "No thanks, keep my token". Breaking the glass and reaching zero spend nothing. Pressing spend takes the token and plays right away. The server still refuses a claim before the wait ends ("Still waiting"). The old "unlocked" screen is no longer reached.
**Tested:** scratch server: at 0:00 tokens stayed 2, spend → 1 token and one extra unlocked; early claim refused; decline kept the token.

### Standard Mac shortcuts
**Asked:** the macOS app had no standard shortcuts.
**Cause:** the Swift app never built a main menu, and macOS shortcuts come from menu items.
**Now:** Glass TV menu (About, Settings ⌘,, Hide ⌘H, Hide Others ⌥⌘H, Quit ⌘Q), Edit (undo, redo, cut, copy, paste, select all, Search ⌘F), View (Reload ⌘R, zoom ⌘0/⌘=/⌘-, Full Screen ⌃⌘F), Window (Minimize ⌘M, Zoom, Close ⌘W).
**Untested:** it compiles, but I didn't relaunch the running app (that needs his screen). He has to quit it from the Dock once and reopen it with `glass`.

### Undo
`git revert a381ffa` in ~/projects/glass-tv, `./build.sh`, `glass restart`.
