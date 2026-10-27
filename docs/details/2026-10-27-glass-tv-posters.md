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

---

## 18:10 Liquid glass icon, install to Applications

**Asked:** a nice liquid glass icon, and the app should build into /Applications automatically.

### Liquid glass icon
His Mac is on macOS 15, which has no system Liquid Glass icon rendering (that's macOS 26 with Icon Composer), so the look is drawn: blurred colour light behind a thick translucent screen pane, a bright top rim, a soft inner bevel and a small break-glass crack. Colours are the app's own blue tokens (#6192e1, #1251b4, #002b7c, #c2d6f7). No orange.
Three takes in `app/icon/` (per the "show options" rule; installed the first so he isn't blocked): a-blue-screen (default, TV with stand), b-blue-play (play symbol, green glow), c-night (dark with blue and deep red light). Contact sheet: `app/icon/options.png`.
Rejected: a glossy 2000s-Aqua highlight band from the first draft; it looked dated, not glassy.

### Auto-install to Applications
`./build.sh` now renders the icon to an .icns, builds the app, and installs it to `/Applications/Glass TV.app` (replacing the old copy and refreshing the icon cache). `glass` rebuilds and reinstalls first whenever anything in `app/` is newer than the installed app, so Swift or icon edits land on the next open without a manual build.

### Switch icon
`echo b-blue-play > ~/projects/glass-tv/app/icon/CHOSEN && ~/projects/glass-tv/build.sh`

### Untested
I didn't relaunch the running app (needs his screen), so the Dock icon hasn't been checked live; the installed .icns renders correctly at 1024px.

### Undo
`git revert 674ec1f` in ~/projects/glass-tv; move /Applications/Glass TV.app to the Trash.

---

## 19:20 Grand-theatre icon

**Asked:** keep the dark background of the third icon, drop the red/blue "cop" colours and the two round blobs, make the play button *be* the cracked glass, and go for a 20th Century Fox feel: gold, grand theatre, big searchlights.

### What changed
New generator `app/icon/theatre.py`. Dark warm stage (the app's own dark tokens), gold searchlight beams fanning up from the stage edge with bright cores, a warm floor glow, a frosted glass screen with a gold rim and a gold stand. The crack is now the play button: a jagged triangular shard lit gold from behind, with fracture lines running out from its three corners across the glass.
Two takes: **d-theatre-screen** (installed; TV screen and stand, beams cross behind it) and **e-theatre-pane** (no TV frame, just the cracked play shard floating in the beams, beams fan outward).

### Colour choices
Gold comes from the palette's "tape cream" scale plus its yellow scale (#f8e365, #dcc300). It's deliberately yellow-gold, nowhere near orange. Rejected: tape cream on its own, which read as grey-beige rather than gold in the first render.

### Switch icon
`echo e-theatre-pane > ~/projects/glass-tv/app/icon/CHOSEN && ~/projects/glass-tv/build.sh`

### Untested
Not seen in the Dock yet (needs a relaunch). It renders correctly from the installed .icns.

### Undo
`git revert a27e576` and rebuild.

---

## 19:32 Icons rejected

**Matt:** the theatre icons are bad.
**Real cause:** I drew them by hand as SVG code (shapes, gradients, blur). That approach can't reach the polish of a real app icon; the beams, glass and shard all look like vector clip-art. It's a tooling ceiling, not a matter of tweaking.
**Proposal:** generate 4 renders with a real image model (Figma's image generation; GPT Image or Gemini Image) from one brief (dark stage, gold searchlights, glass screen whose crack forms the play button, macOS icon shape). He picks one, I cut it into the app icon. Costs Figma AI credits per image, so I asked first.
