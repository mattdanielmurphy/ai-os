# MDMA palette, round 3 (no orange)

## 23:20 Round 3 board: no orange, Mac-window preview

Matt asked: redo the three round-2 directions with no orange, and show a different preview UI style. He also banned orange (except rare small accents, nothing like Claude orange, terracotta or the Tailwind look).

---

### Oranges swapped out

- Apothecary: tincture (#eb8900) → **camphor** #a4c4a1 (pale sage green, like camphor/menthol tins).
- Prairie: sunset (#ff9564) → **spruce** #304e4f (deep blue-green of boreal spruce).
- Synth: panel orange (#ff864e) → **cable magenta** #a32384 (patch-cable magenta).
- Signal red moved slightly redder (hue 24 → 20) so it reads red, not red-orange. It's still close to Tailwind rose-600 (4.6).
- Rejected first tries: camphor at L0.78 (4.9 from Radix green8), spruce at L0.44 h182 (5.8 from Radix mint7), magenta at L0.58 h350 (5.2 from Radix pink11). Re-seeded until each cleared distance 6.

---

### Orange blocked in the generator

`design/candidates/directions.js` now rejects any key with OKLCH hue 30–80 and chroma > 0.06, and anything within ΔE 12 of terracotta or Claude orange (#d97757, #cc785c, #da7756). So no future round can drift back to orange.

---

### New preview style

The round-2 preview was a generic card grid with buttons. Round 3 shows a **Mac utility window** (traffic lights, sidebar of projects, segmented control, a stacked usage meter using all 8 hues, settings rows with chips and toggles, slider, Cancel/Save, a "Synced" HUD pill), since the suite is Mac utilities and HUDs. Tapping a hue row makes it the window's accent (and adds it to picks). Window text uses the system font; board chrome moved from IBM Plex to Schibsted Grotesk + Martian Mono.

---

### Checked and not checked

- Rendered with headless Chrome and looked at the screenshots: windows, scales and accent swap look right. First pass had the HUD pill covering Save; moved it to the sidebar.
- Board chrome dark mode not screenshotted (the previews themselves show both modes).
- Still close to stock (marked on the board): cobalt bottle, oxblood, aurora, signal red, knob blue.

---

### Rule saved

Orange ban saved to `.rules/core_safety.md`, `.rules/web_design.md`, `~/.claude/CLAUDE.md` and the never-terracotta memory (replacing "orange itself is fine").

Undo: revert this commit; republish round 2 from `design/candidates/board2.js`.
