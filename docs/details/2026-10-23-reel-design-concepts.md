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

## 21:58 Round 3: Hairline-based

**Matt's feedback (on round 1):** every concept except Poster made the slide a small window inside the page;
the slide must be the page, with subtle controls floating on it (full screen takes it all, controls included).
Favourite: Hairline (clean bones, likes its fonts). Liked: Caption first's look (not its big caption on top),
Gallery's look (but overdone, reads as AI), Poster a bit (graphics too big). Disliked: Terminal, Blueprint,
Synth panel (not warm). Dislikes the dot next to the chapter label.

---

### What round 3 does

- All 8 are Hairline variants: Hanken Grotesk Light/Medium, tinted neutrals, hairline rules.
- The page is the slide; content is centred vertically on it; controls float at the bottom at 78% opacity.
- Graphics are smaller than rounds 1–2 (title 52 px desktop, bars at most 440–520 px).
- No dot by the chapter label.
- Variants borrow what he liked: 03 soft bars + tinted card (Caption first), 04 serif headline only
  (Gallery, toned down), 05 pale colour wash (Poster, calmed).
- 01 and 06 keep Martian Mono for the tiny label only (he said he liked Hairline's fonts); the rest have no mono.
  Pick a no-mono one if the earlier "no monospace" still stands.

---

### Round 3 concepts

01 Hairline, as is (14-3) · 02 no mono (14-67) · 03 soft card (14-133) · 04 serif title (14-191) ·
05 colour field (14-255) · 06 warm grey (14-327) · 07 dot bars (14-393) · 08 aspen (14-469).
Round 2 (13-2) already had the page-is-the-slide layout; it stays in the file for reference.
Builder: `services/reels/concepts/round3.js`. Mocks only, contrast by eye.

## 22:05 A mixer so Matt can mix and match himself

**Asked:** he never saw round 2 and commented on round 1. Get rid of the faint lines cutting through the bar
numbers; why can't he delete things in Figma; he wants to mix and match ideas himself without describing
changes and waiting. Round 3 notes: Hairline loved; Gallery's serif font feels played; warm grey and many
others beautiful; dot bars liked but dot/line contrast too strong and bars too thin; Aspen and colour field
feel corporate (a bank); drop 4, 5 and 8. Subtitles are required; #3's subtitles about 50% bigger. Not keen on
soft-block bars or the card behind the total.

---

### Lines removed in Figma

The faint 1 px "track" behind every thin bar ran under the numbers. Removed from all round 3 boards (30 lines),
and the mixer has no tracks at all.

---

### Why he couldn't delete in Figma

He owns the file (it's in his Drafts, made with his account). The lines sit several frames deep (board →
page → slide content), so a plain click selects the whole board. **Cmd-click** (deep select) or double-click
down into the frame selects the line itself; then Delete works.

---

### Why a web mixer instead of Figma

Figma can do mix-and-match with components and variants, but it needs Figma know-how and every option has
to be built as a variant first. A small web page with chips and sliders renders the reel page live at desktop
and phone size, in light and dark, and is the same thing the future JSON template will do. So the mixer is
also the first draft of the template's settings (palette, font, label, highlight, layout, graphics size, bars,
bar thickness, dot size, line strength, total style, subtitle size and position, controls, controls strength).

- Link: https://claude.ai/artifact/U9TF2nu8irgwBizQxoh1Yw (source: `services/reels/concepts/mixer.html`).
- Presets: Hairline, Hairline no mono, Warm grey, Dot bars (thicker line, softer contrast), Soft card,
  Film subtitles. Serif title, colour field and aspen are gone.
- Subtitles are always on; default size 22 px desktop (about 50% bigger than round 3), 72% of that on phone.
- "Copy settings" copies one line of JSON to paste back; his mix is remembered in his browser.
- Full screen icon in a preview really goes full screen with the controls on it (desktop browsers).

---

### Mixer tested

Headless Chrome at 1400 and 400 px wide: no errors, no sideways scroll, presets switch. Not tried on a real phone.

## 22:20 The mixer becomes its own project

**Asked:** make the mixer and the techniques its own project for reusing on future UI.

---

### What's in ui-mixer

`~/projects/ui-mixer` (private GitHub repo `mattdanielmurphy/ui-mixer`):
- `shell/` the generic mixer: options rail, presets, desktop + phone previews, light/dark, real full screen,
  Copy settings, remembers your mix. Knows nothing about reels.
- `subjects/reel-player/` the reel page: renderer, palettes, presets, options. A new UI = a new subject folder.
- `build.ts` (bun) bundles shell + subject into one HTML file for the Artifact tool; `check.cjs` tests every
  preset at desktop and phone width in headless Chrome.
- `TECHNIQUES.md`: everything learned (Figma builder rounds, Matt's design feedback, when to switch to a mixer).
- `figma/`: the round 1–3 builder scripts.
The reel mixer link is now built from this project (same URL).

---

### Agents will use it on their own

New rule 1m in `.rules/core_safety.md`: for UI with several possible looks, read TECHNIQUES.md, do at most one
concept round, then build a mixer subject. Plus a memory entry and a line in ABOUT_MATT's "Where things live".

---

### Tested

`bun run check`: built, all 6 presets clicked at 1400 and 400 px, no errors, no sideways scroll.
Not tried on a real phone. The artifact link is shared "anyone with the link" (you set that).
