# MDMA master palette: details

Thread: "MDMA master palette" (restart of the cold "Personal design system and palette" thread).

## 21:10 First swatch board

Matt asked (via coordinator) to design the suite's master palette with him, in small steps. Requirements: one
system, agents never invent a colour, master big enough for ~100 apps, small active subset that grows from the
master, light AND dark for everything (his follow-up: designing both modes is part of the process).

What I did: generated 24 candidate hues x 12 steps in light and dark with Adobe Leonardo
(`@adobe/leonardo-contrast-colors`), published a tap-to-pick swatch board.

---

### Board link and how to use it

https://claude.ai/artifact/49fWnnWw1J4zUsyRhiqkgf. Each row is a hue: light scale, dark scale, and a tiny UI
sample (button, tag, link, heading) in both modes. Tap rows to pick; the bar at the bottom copies the list.

---

### How the scales are made

- Source: `design/candidates/generate.js` (OKLCH key colours per hue) -> Leonardo -> `candidates.json`;
  `board.js` + `board.template.html` build the page.
- Every step is placed by **contrast ratio against the background**, the same 12 targets in both modes
  (1.04 ... 12). So step N means the same job and the same readability in light and dark: 1-2 backgrounds,
  3-5 fills, 6-8 borders, 9 solid, 10 hover, 11-12 text. This is what makes light/dark pairing automatic.
- Background neutral: stone (warm grey). Light bg #f8f8f7, dark bg #1a1917.
- Rejected: Radix Colors as-is (31 hand-tuned scales). Less work, but not ours, and it can't grow past 31.
  Kept as the fallback if the generated scales disappoint.

---

### Banned band skipped

No hue between roughly 30 and 60 degrees (OKLCH): that's the terracotta / rust / burnt orange / coral band.
Side effect: **there is no orange at all**. Honey (75°) is the closest; it might read amber. Matt decides.

---

### Known problem: yellows go muddy

Because step 9 is pinned to 3.6:1 contrast, yellow, gold, honey and citron come out mustard/brown
(e.g. yellow step 9 = #a37d00). Radix solves this by letting bright hues keep a bright step 9 with dark text.
Fix for v2: per-hue override so bright hues keep a vivid solid and flip to dark text. Not done yet.

---

### Open questions for Matt

1. **Pick ~7 hues** for the first unlocked set (neutral is separate).
2. **24 hues vs ~100 apps:** two ways. (a) Grow the master: Leonardo can generate more hues any time, but past
   ~30 neighbours get hard to tell apart. (b) Apps share hues and differ by role. My lean: both; apps claim a
   hue only when they need a distinct identity, and the master grows when a gap appears.
3. **Logo brand colours** (MDMA Appothecary logo thread) must be picked from this master, not a second palette.
4. **One palette file** read by Swift, Lua and HTML: planned as `design/` generating each format from one source.

Untested: I couldn't screenshot the board (preview pane won't render local files); checked values numerically.
Undo: delete the artifact; `git rm -r design/`.

## 21:05 Are these stock colours?

Matt asked how the colours were made and whether they're stock; he wants colours that aren't on 100M other apps.

---

### Honest answer on the source

Not copied from any library, but generic in effect. I spaced 24 hue angles roughly evenly round the colour wheel
at standard saturation and let Leonardo fill the steps. That is the same recipe Tailwind, Radix and Material use,
so the results land near their blue/green/red. Nothing about them is ours.

---

### What makes a palette unique

- **A seed from a real world**, not the colour wheel: hues lifted from a concrete source (antique apothecary
  glass and labels fits the "MDMA Appothecary" name; also prairie/Edmonton winter light, vintage synth panels).
- **Off-grid hue angles and an unusual chroma/lightness curve** (e.g. dusty, mineral, inky) so the suite has a
  personality, not just a hue list.
- **Tinted neutrals** that carry the character on every screen.
- **A distance check**: compare every hue against Tailwind, Radix and Material and reject anything too close
  (a delta-E threshold), so "unique" is measured, not claimed.
- Leonardo stays: it still does the contrast-correct light/dark steps from whatever key colours we pick.

---

### Proposed next step

Board v2: three distinct directions (apothecary glass, prairie light, synth panel), each with ~8 hues + neutral,
light and dark, with the stock-distance check shown. Matt picks a direction, then hues.

## 21:20 Board v2: three seeded directions

Matt 👍'd the three directions and said he likes orange; the ban is terracotta only (LLM-default clay
brown-orange). The rules already said that after a pull, so nothing to change there.

---

### Three directions on the board

Same link, version 2: https://claude.ai/artifact/49fWnnWw1J4zUsyRhiqkgf. Each direction has 8 hues plus a tinted
neutral, a sample "app" in light and dark, and per-hue scales. Picks: a direction button plus hue rows; the
bottom bar copies them.

- **Apothecary glass**: cobalt bottle, tincture (clear orange), absinthe, verdigris, oxblood, lavender oil,
  uranium glass, iodine. Warm paper neutral.
- **Prairie light**: canola, big sky, winter dusk, aspen, sunset (orange), frost, aurora, fireweed. Cool snow
  neutral.
- **Synth panel**: signal red, panel orange, patch yellow, phosphor, VFD teal, knob blue, patch violet, tape
  cream. Aluminium neutral.

---

### Stock colour check

- Every key colour is compared (CIEDE2000) with **986 stock colours**: every Tailwind v3 shade and every Radix
  step, light and dark. 2-3 is a just-noticeable difference; target is 6+.
- If a key is too close, it's nudged up to 8° of hue, 0.06 lightness and 0.02 chroma, smallest change first.
  A bigger search worked numerically but wrecked the colours (signal red turned into salmon), so I capped it.
- **5 hues are still under 6** and marked "close to" on the board: cobalt bottle (5.2), oxblood (5.0),
  aurora (4.5), signal red (3.6), knob blue (4.9). Strong reds and blues are where stock palettes are densest.
- Terracotta guard: any key within 12 of `#c96442` / `#c2502f` is rejected.
- Honest limit: one hue alone can't be truly unique; 986 stock colours cover sRGB closely. What makes the suite
  ours is the **set**: the specific hues together, their neutral and their light/dark curves.

---

### How v2 is built

- `design/candidates/directions.js`: OKLCH seeds per direction -> nudge -> Leonardo light/dark scales.
  The key colour is kept exactly as step 9 in both modes (fixes v1's muddy yellows); text on it flips
  dark/white by luminance.
- `board2.js` + `board2.template.html` build the page. Dev deps added: tailwindcss 3.4.17, @radix-ui/colors
  3.0.0 (only for the comparison).
- The picker page's own chrome uses a few fixed greys; it's a tool, not a suite app, so it isn't on the
  palette.
- Untested visually: still no way to screenshot it here. JS parses; values checked numerically.
