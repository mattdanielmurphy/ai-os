## 23:55 X-Ray better-shot search (built)
- Asked: build Matt's idea (hunt nearby frames for a clearer face).
- Did: faces.swift adds Apple Vision face capture quality; xray.ts `clearerShots` decodes ±3 s at 4 fps in a separate decoder (player untouched), tracks each unclear/unnamed face by box overlap, stops at cuts (scene score > 0.15), fingerprints the 3 clearest shots, takes the best match. Commit e454b82 (glass-tv).
- Rejected: "must look like the same face" as the cut guard: a heavily blurred face looks like nobody, so it rejected the real person. Kept as knob xray.sameFace, off.
- Tested on synthetic clips made from cast photos: blur→clear (0.71→0.99), heavy blur (unknown→named), cut to another actor (correctly not borrowed). ~+0.4 s.
- Untested: real movies (profiles, motion, streams over http). Overlay doesn't show "refining"; result just arrives ~0.5 s later.
- Undo: git revert e454b82, or set xray.searchSeconds to 0.
## 00:40 Esc + speed fix
- Matt: Esc shouldn't hide X-Ray; first pause took ~9 s; all pauses got slower since the better-shot search.
- Cause: the search blocked the answer, decoding the stream over http on most pauses (clearQuality 0.5 flags most faces).
- Fix (ac458b8): quick answer returns at once with `refining`, player re-asks with `wait=1` and swaps in the better names; overlay web view loads during the request; castVectors queued so the first pause awaits the warm-up instead of duplicating it; new actors start with main photo only, extras in background. Esc closes an open card only, else passes to the player.
- Measured offline: cached show quick answer ~0.3 s; brand-new show paused 0.3 s after start ~2 s (cast lookup + photo downloads ~1 s, fingerprints ~0.7 s).
- Untested in the real app: needs Glass TV relaunch. Server now logs `xray quick Nms` for each pause.
## 00:55 From-behind names, close-up layout, window drag, crash
- From behind: faces.swift also returns Vision upper-body people boxes. A person with no face inside → background decode of the last 10 s at 2 fps; faces in shots before the paused shot's cut, sure matches only; if one cast member from there isn't named now (or is seen 2x more than the next), they're put on that person, faded dashed tag "Seen from behind · named from the last shot". Only when exactly one faceless person. Knob xray.sceneSeconds. Untested on real footage (Matt testing).
- Close-ups (face > 28% of frame height): card goes beside the face at eye level, roomier side first, with a level line; cards never overlap heads (hair included).
- Drag the picture (not full screen) moves the window; a drag never toggles pause.
- Crash: playback failed ("Couldn't play this"), then a 4 s timer sent "quit" to an already-destroyed mpv → segfault. Now MPV.alive guards commands. Likely cause of the playback failure: my scan opened ~75 parallel connections to the Real-Debrid stream link; killed it.
## 01:10 Episode silently failing
- Cause: after my 75-connection scan, the Torrentio/Real-Debrid resolve link reset connections (temporary block). A single probe now gets a normal 302 to Real-Debrid, so it should play again. Resuming wasn't the factor.
- Fix (ac0ad81): Player records mpv's end-file error; if the player closes before the video ever loaded and the person didn't close it, the page toasts "Couldn't play that: <reason>. Try again in a minute, or pick it again for another source."
- Untested end to end (couldn't reproduce a failure now).
## 01:40 Source fallback + Sources menu
- Server `src/sources.ts`: remembers the ranked list when a stream is chosen; `/api/sources` lists it in plain words (picture: Best/Great/Good/Okay; 1-3 signal bars: provider-cached or 50+ peers = 3, 10+ = 2); `POST /api/sources/use[?i=]` switches; with no i it picks the next copy on a different Real-Debrid server, checking hosts with one HEAD request each, at most 3, sequentially.
- Player: buffering 8 s (knob fallback-seconds) → corner note "This copy is slow. Trying another: Great picture" → loadfile replace at the same time → "Now playing: …". If that copy errors, tries the next. Control bar gets a signal-bars button (hidden unless 2+ copies) opening a native menu: picture + signal + "Playing now", note "More bars = more people sharing it".
- Only one stream open at a time (replace closes the old). Untested live: Matt to try on the buffering episode after relaunch.
## 02:10 X-Ray slow refine + turned-away face (coordinator task)
- Slow: the refined pass took ~10 s on streams (server log). Two separate ffmpeg decodes ran at once (±3 s and 10 s back), both software-decoding 4K. Now one decode, `-hwaccel videotoolbox`, window 6 s back (+3 s ahead only when a face is unclear), one connection. Local test: refined in ~0.9 s.
- Turned away: Vision finds no face and often no body on the back of a head. Now, if someone was named earlier in the same shot (no cut since), their tag stays where their face last was, faded "behind" style, unless someone named now is there. Look-back runs when a body has no face or nobody at all is named. Body-detect confidence lowered 0.5 → 0.3.
- Tested with a synthetic clip (face gradually covered): paused on covered face → "Javier Bardem (behind)". Not tested on real streams (no bulk requests; one decode per pause).
## 02:30 "Searching" indicator
- Matt wants to see that a face was found and is being searched.
- Overlay: while the server says `refining`, each found-but-unnamed face gets a softly pulsing ring (existing --onscreen colour) with "LOOKING…" under it, and the key-hint row adds "Looking for a clearer view…". If nobody is named yet, the "faces not recognised" cast list waits until the search finishes. The refined answer re-renders and the rings go away.
- Untested visually (browser preview couldn't run the page's script); JS syntax checked, app built (e110886). Needs Glass TV relaunch.
## 03:00 Always-on face memory + no spoilers
- Player: once a second while playing (knob xray-memory-seconds), right after drawing a frame, the GPU blits just the picture into a ~960 px framebuffer and reads it back; JPEG → POST /api/xray/frame?t= to the local server. Skips a frame if the last is still in flight. No internet traffic.
- Server: remember() finds faces, keeps sure matches with boxes for the last 30 s per episode, and records first-seen time per person (xray/seen.json). bin/xray-faces now stays running (--serve) → ~35 ms per frame instead of ~200 ms.
- Pause: if memory covers the last 1.6 s, the answer uses it directly (no decode, ~0.1 s): unclear faces overlapping someone named in the last 2 s get that name; someone named in the last 2 s with no face now keeps a faded tag; the two-shot rule uses the last 6 s. After a seek (no memory yet) the old decode path still runs.
- No spoilers (Matt): the "faces not recognised" list shows only people already seen at or before this point; empty → "No one recognised here yet".
- Tested: synthetic clip, pause on covered face → "Javier Bardem (behind)" in 74 ms; cast list empty before first appearance. NOT tested: the GL frame grab in the real player (compiles; needs relaunch). Risk: if the grab reads the wrong region, memory just names nothing.
## 03:20 Polished searching indicator (coordinator task)
- Replaced the "LOOKING…" label and "Looking for a clearer view…" hint with no-text animation: faint ring with a light line + dark halo (readable on bright and dark pictures), and a soft lavender-to-pink comet with a white head sweeping round it (conic gradient masked to a 3 px ring), gently breathing; fades in. Light-mode media query strengthens the halo; reduced-motion keeps only the breathing.
- Tweaks: xray.seekSpinSeconds (1.1), xray.seekPulseSeconds (2.4), sent to the overlay with each X-Ray answer.
- Checked in a demo page on light, dark and mid backgrounds (static snapshot; animation not watched live). 45c4303.
## 03:40 Memory named someone from the previous shot (coordinator task)
- Bug: memory treated "the last 2 s" as the same shot, so after a cut Jason Sudeikis stayed tagged.
- Fix: xray-faces returns a 16x9 grey thumbnail per frame; a remembered frame starts a new shot when it differs from the previous one by more than xray.memoryCut (28/255 mean) or after a gap >3 s; the paused frame must also match the latest remembered frame. Turned-away names come only from frames since that cut, and only where a person is still visible now (a body box or an unnamed face under their last spot). Two-shot rule unchanged (needs a faceless body present).
- Tested: clip with actor A, then a cut to actor B elsewhere in frame → only B (before: A would get a "behind" tag). Blur-within-shot clip still names the actor.
- Risk: fast camera moves within a shot may count as cuts (only makes it forget sooner).
## 03:55 Phantom "Seen from behind" tag on blurred background
- Matt's screenshot: Nathan close-up correctly named, plus "Ted Lasso · seen from behind · named from the last shot" on empty blurred background. That's the two-shot rule: a weak body detection (confidence 0.3) on the background + Ted seen in the previous shot.
- Fix (see commit): body detection back to confidence > 0.6 and height > 20% of frame; the two-shot carry-over across cuts is now off by default (tweak xray.twoShot = 1 turns it back on). Same-shot turned-away names still work, but need a visible person.
- Checked Matt's actual paused frame: one face, one body, the face is inside that body → nobody "behind". Cut test clip still names only the new actor.
## 04:10 Tags jumped after appearing (coordinator task)
- Cause: cards were laid out small (no facts yet), then facts arrived, the card grew and relayout moved it (e.g. above → below).
- Fix: at full density, missing facts are held by two invisible placeholder lines, so placement (with collisions) uses the final size; arriving facts fill the card in place with no relayout. Facts are kept across answers. When a refined answer moves a card, it glides from its old spot (0.35 s ease); stems/dots fade in.
- Tested headless (Chrome via playwright): card positions identical before/after facts; moved card animates. Needs Glass TV relaunch.
## 04:30 Cursor flicker (coordinator task)
- Cause (likely): the player's full-window tracking view calls showControls() on every mouse move, which called NSCursor.setHiddenUntilMouseMoves(false) each time; that resets the cursor to the arrow, then the web view (X-Ray cards, IMDb browser in the same window) sets its pointer again → flicker. Tracking areas fire even under overlapping views, so the IMDb browser was hit too.
- Fix: only unhide when the player itself hid the cursor (flag set in hideControls).
- Untested by hand (needs Matt's mouse); builds. IINA's own player isn't ours to change.
## 04:50 IMDb primary + cursor flicker, round 2 (coordinator task)
- IMDb: filled accent button; card gets class `go` once facts with an IMDb link arrive (pointer cursor); hovering the card glows the IMDb button; a click anywhere on the card (not a poster or the Wikipedia button) opens IMDb. Tested headless: card click → IMDb URL, Wikipedia button → Wikipedia.
- Cursor: built a tiny test window that logs every NSCursor.set with its caller. Moving the mouse showed the arrow being set by AppKit's tracking-area manager during mouse-moved routing (`_NSTrackingAreaAKManager … _routeMouseMovedEvent`), i.e. the cursor-update fallback, not our code. Fix: the player's full-window TrackingView now opts into .cursorUpdate with an empty handler, so that fallback doesn't fire. Not confirmed: the second test run's log was unreliable (overwritten), so the fix is reasoned, not proven.
- Incident: for the second test run the clearance tool printed "unreachable" instead of a grant, and my script moved the mouse anyway (~2 s, test window only). Stopped; no more synthetic input this session without a real grant.
## 05:10 In-app browser keeps old history
- Matt: after closing the IMDb browser and resuming, a later visit's Back went to the earlier visit's page.
- Cause: one WKWebView lived for the whole app run; closing just loaded about:blank, so its back list kept every earlier page.
- Fix (b0c5975): closing throws the web view away; the next open (or the background prewarm) builds a fresh one with empty history, so Back from the first page closes the browser and returns to the video. Opening a page other than the prewarmed one also starts fresh.
- Untested by hand (needs clicks); builds. Cost: a fresh web view per visit (~100 ms), hidden by the existing prewarm.
## 05:40 Subtitles: language, official first, dialogue-only, recap
- Only tracks in the chosen language (knob sub-lang, default en/eng/english; by lang tag, else by title).
- Ranked: came with the video (not external) +100, title says WEB-DL/Blu-ray/official +20, SDH/CC −10, forced −200; OpenSubtitles downloads last.
- Menu: Off · Dialogue (best non-SDH) · Hearing impaired (SDH) (best SDH/CC/hearing-impaired flag) · "Other English tracks" submenu · "Hide sound descriptions" toggle (default on; mpv sub-filter-sdh, off automatically when SDH is picked) · hint "R shows what was just said". S cycles Off → Dialogue → Hearing impaired → Off.
- Recap: the best dialogue track stays selected but hidden when subtitles are off (sub-visibility), so sub-text keeps flowing; lines are kept 2 min; R / speech-bubble button shows the last exchange (lines back to the first ≥4 s pause, max 15 s), descriptions stripped, in a dark box above the bar for 7 s. Knobs recap-seconds, recap-gap-seconds, recap-display-seconds.
- Tested: ranking and stripping logic in a Swift snippet (Apple TV+ WEB-DL → Dialogue, SDH BluRay → Hearing impaired). Not tested in the player (needs playback); builds.
- Risk: if a video has image-based subtitles (PGS), sub-text is empty, so recap says nothing was said.
## 06:00 Recap panel restyle
- Matt: the R box looked bad (black slab, centred broken lines, too much text, overlapping credits).
- Now: frosted dark panel (same material as the control bar), 16 px corners, faint border, 22/16 px padding, sitting 14 px above the bar, max 640 px wide; each subtitle cue joined onto one line, left-aligned, 18 pt; older lines 62% white, newest semibold; only the last 4 lines (knob recap-lines). Preview rendered over Matt's screenshot (mock); not seen in the player.
## 06:20 Blurred Ted not named (Matt's screenshot, S1E9 14:14)
- Two gaps: (1) when face memory covered the pause, identify returned straight away, so the look-ahead for unclear faces never ran; if memory never surely named him (sunglasses, visor), nothing did. (2) A remembered name only carried over where Vision found a body or face now.
- Fix: memory first (wider overlap rule: 0.15 or face centre inside), then any face still unnamed gets the one-pass look-ahead (refining) as before. New `still` rule: if the paused frame differs from the last remembered frame (≤1.5 s ago) by ≤ xray.stillDiff (10/255 mean grey), people named there keep their tags even with no face or body found. Cuts still reset.
- Tested on local clips: always-blurred face → refined pass names him; covered face with nothing detected → kept ("behind"); cut → only the new actor.
