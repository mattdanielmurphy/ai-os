# Glass TV: toolbar, poster sizing, episode picker

## 19:55 Toolbar, posters, picker, watched marks

**Asked:** a draggable custom toolbar clear of the stoplights; posters that scale with the window and never get blown up past their resolution; hover says "Click to play/resume" + S/E only; a big Pick episode button; picker seasons that fit; episode names hidden by default with a master setting; watched marks per episode and per season.

---

### Toolbar
- The native app (`app/main.swift`) now has a `GlassWebView` that gets the toolbar's drag areas and the controls inside it ("holes") from the page. A press on the toolbar outside a control calls `performDrag`; a double-click zooms (follows the system "double-click a title bar" setting).
- The stoplights are moved to sit vertically centred in the toolbar.
- Three looks, switchable live with the `ui.toolbarStyle` tweak (⌃⌥⌘T): 1 one row with the stoplights, 2 slim "Glass TV" title strip above the controls, 3 frosted glass with a centred pill search. Default is 1.
- **Untested in the real window:** dragging, double-click zoom, centred stoplights, and whether controls under the enlarged title bar still click. Screen access for the test was declined.

---

### Posters
- Width = 14% of the window (`ui.posterScale`), between 110 px (`ui.posterMin`) and 250 px (`ui.posterWidth`), and never more than 500 px ÷ pixel ratio, so a 500 px TMDB image is never upscaled.
- TMDB poster size raised from w342 to w500; older saved w342 URLs are rewritten in the page.
- Fixed a CSS order bug (Bun bundles base.css after app.css) that kept the library grid stretching posters.

---

### Hover and picker
- Hover overlay: "Click to resume" (if started) or "Click to play", plus S/E. No episode names.
- Big white "Pick episode" button at the bottom of TV posters on hover (replaces the small text link).
- Seasons are small wrapping number chips (Specials, 1, 2, …), with a ✓ on fully watched seasons. Opens on the season you're up to.
- Episode names hidden by default. "Show names" in the picker and "Episode names" in Settings flip the same saved setting.
- Each episode has a ✓ button; "Mark season N watched/unwatched" does the whole season. Partial progress shows as a thin bar.

---

### Watched
- Saved in state.json as `watched` (episode key → time). Finished-in-app episodes count too.
- "Up next" now skips watched episodes: marking season 1 watched makes a show start at S2 E1.
- Unmarking a finished episode resets its saved position.

---

### Not live yet
- The server bundles the web page when it starts, and an episode was paused in IINA, so I didn't restart it. `glass restart` makes it live. The app itself is rebuilt in /Applications; quit and reopen it for the toolbar.

### Undo
- `git revert` the commit "Draggable toolbar with centred stoplights…" in ~/projects/glass-tv, then `./build.sh`.
