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
