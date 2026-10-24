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
