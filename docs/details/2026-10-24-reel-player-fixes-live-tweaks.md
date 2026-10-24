# Reel player fixes + live Tweaks (2026-10-24)

## 18:10 Speed fix, player fixes, live Tweaks

Matt asked (via the coordinator, from the cold reel thread): tables wrap badly; subtitles smaller, current
sentence only, lower; slide content more centred; pause should really pause; Speechify voice far too fast;
all reel and Speechify knobs in the Tweaks panel, live in the browser, Apply makes them permanent.

---

### Voice speed fixed

Cause: `tts.py` sent `<prosody rate="115%">`. Speechify reads percentages as a *change* (range -50% to
+9900%, signed), so 115% meant +115%: 2.15× speed. The scroll-read thread measured the same (100% halved
the length). Fix: rate is sent signed (`+10%`), omitted at 1.0. Default `voice.rate` is now 1.0 (natural).
Reel 004 went from 61 s to ~142 s of speech for the same 335 words. Cache key bumped to `speechify-v3` so
every reel re-records instead of reusing a 2× take. Docs: docs.speechify.ai SSML guide.

---

### All Speechify knobs

`voice.rate`, `voice.pitch` (%), `voice.volume` (dB), `voice.id`, `voice.model` (3.0 / 3.2 / 3.5),
`voice.loudness`, `voice.textNorm`, `voice.paraBreak`, `voice.dotsBreak`, `voice.format`. That is every
field the with-timestamps endpoint takes, plus the SSML prosody that simba-3.x applies (emphasis and emotion
are accepted but ignored by 3.x, so left out). Rate and volume preview live in the browser (playbackRate /
gain against the recorded take); the rest are heard after Apply, and the page toasts "Heard after Apply".

---

### Tables no longer wrap

Compare cards may now run wider than the text column (`layout.tableWidth`, default 1.45×, capped by the
window). Line labels and values never wrap. Checked headless at 1440×900: zero wrapped lines. Phone: one
small "+ box ~$50–100 once" note still wraps in a 2-column card (mono note, narrow column).

---

### Subtitles: sentence, smaller, lower

The subtitle is now its own element under the slide: 20 px (was 26), 88 px gap (was 64), and shows only the
sentence being spoken, words brightening on Speechify's own word timings (build.py now ships per-beat word
times). `subtitle.mode` switches back to the whole line.

---

### Slide sits lower and centred

The slide is centred on its own (the subtitle no longer counts), then nudged down by `layout.lower` (40 px).
If slide + subtitle don't fit above the controls it shrinks, as before.

---

### Pause really pauses

The player used to reveal everything on pause. Reveals now run on a per-slide clock that only advances
while playing (synced to the voice), so pause freezes the slide, the voice and the hold before the next
slide. Tested headless: parts and voice time unchanged across 4 s of pause, resumed from the same spot.

---

### Live in the browser

pages dev server gained `/__pages/tweaks?app=<name>` (tweaks-live.ts): it serves any app's tweaks.json from
the Tweaks registry. The reel page polls it every 400 ms on pages.test only (public copies never poll) and
redraws in place. Tested: a change showed up 58 ms after the file was written. The old in-page "T" tuning
panel is gone (Tweaks replaces it).

---

### Apply makes it permanent

Apply used to need Lua/Swift code declaring the knobs. Now, when no code declares them, the tweaks.json is
its own source: defaults = values, commit + push that file. Then the panel runs `services/reels/apply.sh`
(registered in ~/.hammerspoon/tweaks_apps.json): rebuild every reel whose reel.json names a `page`
(004 → tv-box), copy it to the page, republish mattmurphy.ca/tv-box, deploy Vercel. Tested the save path in
a scratch repo; ran apply.sh for real for this release. The panel's Apply button itself was not clicked.
Also fixed: the panel dropped `choices` when saving a value, so chip knobs (model, format, subtitle mode)
would have turned into text boxes.

---

### Not adopted: shared /api/tts

The scroll-read thread is building one Vercel TTS function for all pages. The reel keeps baked audio for now
so it plays offline on Dad's phone; switch when that function is live if wanted.

---

### Untested / risks

- Nobody has listened to the new take; speed judged by length only (~150 words/min).
- The Tweaks panel follows the focused app; with the browser focused, pin "Explainer reels".
- Apply republishes Dad's tv-box link every time.
- Undo: git revert the commits in ai-os (services/reels), ~/.hammerspoon (tweaks.lua) and pages (tweaks-live.ts).

## 18:15 Apply build failed: bun not found

Matt pressed Apply: defaults saved and committed (beat.lead, duck.depth, music.outro, pace.gentle), then
apply.sh failed with exit 127 because Hammerspoon runs it from `zsh -lc`, which skips ~/.zshrc where bun's
PATH is set. Fix: apply.sh now puts ~/.bun/bin, ~/.local/bin and Homebrew on PATH itself. Re-ran it in a
clean environment (`env -i … zsh -lc`) to finish his Apply: rebuild, republish tv-box, deploy.
