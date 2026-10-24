# Scroll-to-read reel mockup

## 01:50 Mockup built and live

What Matt asked (via the coordinator): a quick interactive mockup of the scroll-to-read reel idea in `services/reels/IDEAS.md` (2026-10-24 entry).

---

### Page and links

- Folder: `~/projects/pages/site/scroll-read/` (one `index.html`, no build deps).
- Public: https://matt-pages.vercel.app/5d527aa8-30be-40ad-bb89-2b80f82e1782/
- Local live reload: http://pages.test/scroll-read/
- Just for Matt: a feel test, not a product.

---

### How the pull works

- Every word of the reading blocks is wrapped in a span; a gradient blob (reel look: hairline palette, Onest, Martian Mono labels) sits behind the current word in document coordinates, so plain scrolling never makes it lag.
- Any scroll the page didn't cause (touch, wheel, keys, scrollbar) starts a gesture. Stretch `t` = distance scrolled in this gesture ÷ threshold (default 30% of screen height).
- Below the threshold the blob leans toward the centre line by `pull × t² × 0.8` of the gap and stretches toward it; reading keeps going (small scrolls never move the narrator).
- At the threshold it "lets go": flies (eased, Fly speed knob) to the first word of the line crossing the centre, and keeps following the centre line while scrolling continues. Reading pauses meanwhile.
- Finger lift + 170 ms with no scroll (covers iOS momentum) ends the gesture; a let-go gesture resumes reading from the centre word. A small gesture just snaps back.
- Hands off, the page auto-scrolls gently to keep the current word between 16% and 64% of the screen height.

---

### Read aloud switch

- Off by default. On = the device's own voice (Web Speech) reads from the current word to the end of the block; word-boundary events drive the highlight when the voice sends them, otherwise the fake timer does. Mockup only; a real reel would use the Pandora narration.

---

### Tune panel

- Corner "Tune" button: reading speed, skip threshold, pull strength, fly speed. Saved in the browser (localStorage). Not wired to the shared tweaks file (mockup).

---

### Tested

- Headless Chrome at 390 px, light and dark: small scroll → no let-go, reading continued; big scroll → let-go, release resumed at the centre word; no page errors.
- Orphan check: clean except a false positive on the `Space` keycap line (the keycap's border shifts its line top by a pixel).
- Untested: a real iPhone (momentum timing, voice word events on iOS Safari).

---

### Undo

- `pages` has no delete; move `~/projects/pages/site/scroll-read` to the Trash and `pages deploy` again.

## 11:50 Drag scroll, list fix, Speechify voice

Matt asked: middle-button drag to scroll on desktop (not Windows-style autoscroll; maybe a "third stage" later), fix the squashed numbered list in his screenshot, and swap the device voice for the new Speechify TTS.

---

### List words fix

The numbered list items are a 2-column grid (number, text). Wrapping each word in a span made every word its own grid cell, so words stacked in two columns. Fix: the text now sits in one `<span data-read>` inside each `<li>`, so the grid has just the number and that span.

---

### Middle drag scroll

Middle button down → the page follows the mouse like a finger (drag up = page moves up). It counts as a scroll gesture, so a big drag still makes the highlight let go and fly to the centre, and releasing resumes reading there. Default autoscroll and middle-click paste are blocked; the cursor shows a grabbing hand and text selection is off while dragging, so left-drag highlighting is untouched. Hint added to the desktop hint line. The "keep holding to keep scrolling" third stage is recorded in services/reels/IDEAS.md, not built.

---

### Speechify narration

The page can't call the API (key would be public), so `site/scroll-read/build_audio.py` renders one mp3 per readable block with ai-os `services/reels/tts.py` (simba-3.2, beatrice_32) and writes `public/audio/manifest.json` with each page word's start time, aligned to Speechify's word marks (all 16 blocks matched in order). The page plays the clip for the current block from the current word and drives the highlight from the audio clock; at the end of a block it moves to the next clip. Jumping (tap a word, or the big-scroll snap) seeks within the clip. The speed slider changes playback rate (230 wpm = 1×). Rebuilds only re-render blocks whose text changed. ~770 KB of audio.

Rejected: calling Speechify live from the page (exposes the key); one long clip for the whole page (simpler seeking per block, cheaper re-renders).

---

### Tested and untested

Tested headless (Chrome, muted) locally and on the deployed link: list items have one text child, middle drag scrolls 300 px, voice loads the Speechify clip and the highlight advances with it. Not tested: real iPhone audio (iOS sometimes blocks the next clip's autoplay after a block ends), and how it sounds. The orphan checker flags "Space" in the desktop hint; that's a false positive from the key-cap box sitting at a different height than the text.

Undo: `git revert 3dad30f` in ~/projects/pages, then `pages deploy`.

## 12:00 Voice on demand, speed bug, stretch refinement

Matt: the voice was sped up; he doesn't want audio pre-rendered (paying for unused inference), but generated on first use and cached for the next person; the stretch should keep the blob on its word with a faint, paler, narrowing pull, and no stretch at all while paused.

---

### Speed bug cause

Shared `services/reels/tts.py` sends `<prosody rate="100%">`; Speechify reads that as +100%. Same sentence: 9.72 s plain, 4.87 s with rate="100%". Reported to "Reel player fixes", which owns the shared fix. The new endpoint sends no prosody at all; speed comes from the browser's playback rate.

---

### Voice on first use

`~/projects/pages/tts.ts` + `api/tts-vercel.ts`: GET `/api/tts?page=<id>&b=<block>`. It only speaks the text of that page's `[data-read]` blocks (bundled into the function at deploy), so it's not an open TTS proxy. Cache key sha1(voice|model|text) in a Vercel Blob store `pages-tts` (public, created 2026-10-24, linked to matt-pages); first request renders and stores mp3 + word marks, later ones return the cached URL. Dev server runs the same handler with a disk cache in `pages/tmp/tts-cache`, key loaded from ai-os .env into memory. The page aligns marks to its own words, plays the current block, and warms the next one. Any page with data-read blocks can use it; the reel thread was told.

Rejected: pre-rendering (Matt's cost point); Speechify from the browser (exposes the key); VPS cache (more moving parts than Blob at this scale).

Blocked: `SPEECHIFY_API_KEY` isn't on Vercel yet, so the live endpoint answers "voice not set up" and the toggle shows that note. Local dev works end to end.

---

### Stretch refinement

The blob no longer grows taller. Under pull it stays on its word, thins up to 14% and pales (less saturation, a little brighter). A separate faint, lighter taper reaches from its edge toward the centre line, narrowing to a thin tip as the pull grows. Paused or ended: no pull, no snap, no pill, scrolling is plain scrolling. Checked in light and dark by headless screenshots.

Undo: `git revert ace0f4b` in ~/projects/pages, then `pages deploy`; delete the Blob store with `vercel blob delete-store`.

## 12:10 Saved settings, voice on by default, waveform, arrival fade

---

### Settings are saved

Every setting (the four sliders, the new fade slider, Read aloud on/off, Tune panel open) lives in one browser record, `scroll-read-settings`. Reloads and redeploys keep it. On load, only settings that still exist are read, so removed ones are dropped quietly. The old `scroll-read-tweaks` record is migrated. Tested: changed the speed, turned the voice off, opened Tune, reloaded; all three stayed.

---

### Read aloud by default

The voice starts on. Browsers refuse to play sound before the first tap or key press, so until then the highlight reads silently, the toggle shows "Tap anywhere to hear the voice", and the first tap starts the voice. A web page can't tell whether the phone's silent switch is on, so "muted" can't be detected; turning it off is remembered instead.

---

### Speaking waveform

Five small gradient bars next to "Read aloud" bounce only while the voice is actually playing (not loading, paused or blocked). Still bars with reduced motion.

---

### Arrival fade

The blob sits at about a third of its opacity while moving and comes to full opacity only once it has settled on the word. The distance over which it fades is a Tune slider ("In-transit fade", default 28 px).

Undo: revert the latest scroll-read commit in ~/projects/pages and `pages deploy`.

## 12:15 Position memory, tap-gated start, landing preview

---

### Position is remembered

The current word is saved as it changes (`scroll-read-position`). On reload the page scrolls so that word sits a bit above the middle, and reading resumes from it. Tested: word 8 before reload, word 8 after.

---

### No silent start

With Read aloud on, the page now loads paused with "Tap anywhere to start reading", because browsers block sound until the first tap. The first tap on the page starts reading and the voice together. Taps on controls (play, switch, Tune) do their own thing instead. The same pause-and-wait kicks in if a browser blocks playback later.

---

### Subtler transit fade

The blob now dips only to 78% of its opacity while moving (it was 35%), easing back to full on arrival. That removes the flashing.

---

### Landing preview

While you pull (voice playing, not yet snapped), the word on the centre line, where the blob would land, gets a dashed outline with a faint fill. It starts faint and firms up with the pull, turning solid near the snap point. Let go early and it fades away; pull through and the blob flies into it. A hint line explains it.

---

### Your defaults

Defaults are now 310 wpm, threshold 16%, pull 1.00, fade 70 px, fly 0.13. Your browser already had these saved; new visitors get them too.

## 16:40 Speechify key on Vercel, voice live

Matt 👍'd the offer. The key was copied from ai-os .env into the matt-pages Vercel project (Production, marked sensitive) through a pipe, never printed. Redeployed. Live check: the first request for a block took 2.2 s (rendered and cached in Blob), the repeat took 0.7 s (cache hit), and the word timings are normal speed ("Reading" is 0.41 s). The headless run on the live link heard the voice after the first tap. Undo: `vercel env rm SPEECHIFY_API_KEY production` in ~/projects/pages.
