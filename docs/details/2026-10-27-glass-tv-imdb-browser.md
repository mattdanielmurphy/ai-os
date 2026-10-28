
## 17:40 Glass TV: calmer IMDb page, browser inside the main window
**Asked:** hide the whole IMDb sidebar (More to explore down) plus visual noise in the upper half; stop opening IMDb in a new window, but keep an easy way out like the player.

**Done (app/browser.swift, main.swift, player/core.swift):**
- Read the live desktop DOM in the built-in browser and wrote a style sheet (injected at document start so nothing flashes): hides IMDb's top bar, the Cast & crew / reviews / trivia row, All topics and share, "Your rating" and popularity, the Videos/Photos tiles, trailer reaction counts, IMDbPro lines, streaming + watchlist + mark-as-watched, and the user/critic review counts. Kept: title, IMDb rating, poster, trailer, genres, plot, creators, stars, awards, episodes.
- Sidebar: `.right-rail-more-to-explore` and its grid column, plus the ad slot above it.
- Browser is now a panel over the main window (also over the player when X-Ray opens it). Bar: "Glass TV · Esc" pill, prev/next page arrows, title, open-in-Safari. Esc closes; ⌘[ and ⌘] still work for page history (menu items only enabled while the browser is up).
- While the panel is up the player ignores keys (otherwise Esc would have started its hold-to-stop, and Space would pause).

**Rejected:** a smart "Back" that closes at the first page (confusable with page history); a separate hold-Esc like the player (IMDb has no destructive Esc, so a tap is enough).

**Untested:** the native panel was compiled and installed but not clicked through (no input clearance on Matt's Mac during his call). The CSS was verified in the built-in browser at desktop width. Selectors use IMDb's data-testid names, which are more stable than its hashed classes but can change.

**Undo:** `git revert` the commit, then `./build.sh`.

## 18:05 Wider IMDb page, Esc leaves full screen, double-click = full screen only
**Asked:** centre or widen the main column now the sidebar is gone; tapping Esc must exit full screen; double-click should only toggle full screen, not pause/play.

**Done:**
- IMDb: the page grid becomes one full-width column (matches the title block above), checked in the built-in browser at 1400px. Chose wider over centred so it lines up with the hero.
- Esc (player/core.swift): in full screen a tap leaves full screen and nothing else; windowed, hold-Esc still stops watching. An 0.8 s guard after leaving full screen stops a re-posted held Esc from carrying on to "stop watching".
- Clicks: a single click now waits a beat (tweak `player.clickDelaySeconds`, 0.25 s) before play/pause, so a double-click never pauses. If a slow double-click lands after the pause fired, it's undone. Same logic in the X-Ray overlay (iina-plugin/overlay.html, delay fixed at 250 ms there).
- Cost of the delay: play/pause by click is 0.25 s slower. Lower the knob in the Tweaks panel if it feels laggy.

**Untested:** none of the native bits (Esc, double-click, wider page in the app) were run on screen; compiled and installed only. The launchd server wasn't restarted, so the new tweak shows in the panel after a restart; the app falls back to 0.25 s until then.

**Undo:** `git revert` the commit, `./build.sh`.
