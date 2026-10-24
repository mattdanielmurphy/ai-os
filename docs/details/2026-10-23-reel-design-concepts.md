# Reel design concepts (8 looks in Figma)

## 21:24 Eight concepts ready to pick from

**Asked (via the coordinator):** 8 Figma concepts for the explainer-reel look, each at desktop and phone size,
light and dark, no Claude/Tailwind default look, orange banned, Superlogical as a reference Matt loves.
Concepts only: nothing is hard-coded into the reel player until Matt picks. The JSON template and preset
layouts come later.

Figma file: https://www.figma.com/design/kq0mqDApKz6jclSJaMkItj

---

### How each board is laid out

Every board shows the same real content (reel 04, beat 2: "Before: about $2,000" with three cost bars and the
total) so the looks compare fairly. Left: the desktop player at 1440 wide in **light** mode. Right: the phone
player at 390 wide in **dark** mode. Each concept therefore shows both modes once, not every mode at every size
(that would have been 32 frames; easy to add for the finalists).

The phone gets a **portrait slide** (720×1040), not a shrunken 16:9 one: a 16:9 slide on a phone made the labels
about 4 px tall. This hints at what the later preset layouts need: every slide template has a landscape and a
portrait arrangement.

Every player keeps the discoverability rules: a visible Pause button, every shortcut printed as a keycap or
`[key] label`, and on phone a "Swipe ← → for beats / Tap a segment to jump" hint.

---

### The eight concepts

1. **Hairline** (node 3-2): Superlogical's habits. One narrow column, Hanken Grotesk Light/Medium + Martian Mono,
   tinted green-black neutrals, hairline progress line, colour only as a lavender→pink gradient on "$2,000".
2. **Broadsheet** (3-95): newspaper. Barlow Condensed headlines, double rules, transcript column beside the slide
   (past beats dim, current beat marked, upcoming muted). Oxblood highlight.
3. **Poster** (3-219): full-bleed cobalt slide, Archivo Black, canola-yellow bars; the page below is a caption band.
4. **Terminal** (3-296): IBM Plex Mono only; chapter label is a command, caption a `>` prompt, progress a block bar.
   Phosphor green in dark, deep green in light.
5. **Caption first** (3-359): the spoken words are big and the slide is a supporting card. Works with sound off.
   Familjen Grotesk, dusk violet, soft corners.
6. **Blueprint** (3-458): grid paper, cobalt linework, outlined bars like measured parts. Chivo + Chivo Mono.
7. **Gallery** (3-657): slide on a mat with a museum wall label. Instrument Serif + Sans, verdigris and iodine.
8. **Synth panel** (3-767): today's panel theme grown up: Big Shoulders, VFD-teal glow, patch-yellow.

---

### Colour and font decisions

- Colours come only from the candidate palettes in `design/candidates/directions.json` (Apothecary, Prairie,
  Synth panel), per the "never invent a colour" rule; a few dark-mode tints were picked as lighter steps of the
  same hue for contrast (e.g. oxblood → #c9566e on dark, which is not in the file's scale; flag if that bends the rule).
- No orange anywhere, no Inter/Bricolage/Source Serif/JetBrains Mono, no cream backgrounds.
- Synth panel light mode first used VFD teal (#2bd8d5) for text on light paper: unreadable, so the light slide
  now uses deep teal #00807e; the bright teal stays for dark mode.

---

### Untested and caveats

- Mocks only: no animation, no audio, nothing wired into `services/reels/template.html`.
- Not checked with a contrast tool; checked by eye in screenshots.
- The phone status bar and notch are not drawn (just "9:41").

---

### Rebuilding

`services/reels/concepts/builder.js` + `specs.js` hold the builder and the eight specs (fonts, palette per mode,
layout switches). Rebuild by pasting `const C = <spec>; const IDX = n;` + builder into the Figma MCP `use_figma`
tool. Undo: delete the Figma file; nothing else changed.

## 21:50 Round 2: warm, full-page, few controls

**Why a round 2:** Matt's own message (sent before round 1 landed) asked for something round 1 missed:
the whole page is the slide, only a few floating controls, warmer, **no monospace**, a bigger slide that is
nearly full screen, a full screen button kept, and phone-first because his dad will open it on a phone.
Round 1 was built from the coordinator's short brief and was techy (mono labels, keycap rows). It stays in the
file on the page "Round 1 · techy (rejected)".

---

### What every round 2 concept shares

- The slide content is drawn straight onto the page: no stage box, no header bar. Desktop 1440×900 light,
  phone 390×844 dark.
- Controls are only: play/pause, progress, full screen. Shortcut keys still exist in the player, but are no
  longer printed as a row of keycaps (Matt: remove every button that isn't necessary). Phone concepts print a
  one-line swipe/tap hint where the gesture isn't obvious.
- No monospace anywhere. Warmth comes from humanist sans and soft serifs, warm-tinted greys, rounder corners.
  No orange, no cream.

---

### The eight round 2 concepts

1. **Pill** (13-3): one floating pill at the bottom: play, 8 beat dots, full screen; subtitle above it.
2. **Corners** (13-74): progress hairline at the top edge, play bottom-left, full screen bottom-right, no subtitles.
3. **Film subtitles** (13-132): centred subtitles, two small round buttons, progress hairline.
4. **Side rail** (13-191): tappable beat dots down the right edge, play + subtitle bottom-left.
5. **Stories** (13-262): phone-stories segments at the top, tap the sides to move.
6. **Inset card** (13-334): slide as a big rounded card, slim dock below.
7. **One button** (13-395): a play button whose ring fills as it plays, plus full screen.
8. **Today, softened** (13-456): current slide style with a friendly sans and a small glass pill.

---

### Round 2 untested

- Mocks only; no motion. Contrast checked by eye.
- Builder: `services/reels/concepts/round2.js`.
