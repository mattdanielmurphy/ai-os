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
