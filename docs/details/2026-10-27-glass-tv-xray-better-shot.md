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
