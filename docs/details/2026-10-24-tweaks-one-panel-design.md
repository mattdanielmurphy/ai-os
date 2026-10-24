# Tweaks + UI Mixer: one panel (design)

## 06:45 Design options for merging Tweaks and the UI Mixer

**Asked (via coordinator):** think through merging the UI Mixer controls into the Tweaks panel as one shared component; how knobs get discovered; organisation without overwhelm (likely set, folds, fuzzy search with cheap-model fallback, element picker); "ask an agent to add this"; copy item name. Design only, no build.

**Read:** `~/.hammerspoon/modules/tweaks.lua`, `tweaks_panel.lua/.html` (Tweakpane 3.1.10 in an hs.webview), `tweaks_registry.json` (10 apps, 1–20 knobs each), `~/projects/ui-mixer` (README, TECHNIQUES.md, shell.js), the "Tweaks panel upgrade" thread (focus-follow, Apply + rebuild, inline notes now live).

**Page:** https://matt-pages.vercel.app/499b568d-cc20-4627-8fb8-683cc9301cde/ (source `~/projects/pages/site/tweaks-one-panel/`).

---

### Option A recommended

One shared web component ("Knobs") lifted from the mixer's rail, reading the existing tweaks file format plus optional extras (chips/choices, section, likely, search words). The panel swaps Tweakpane for it; the mixer becomes Knobs + preview + presets. Why: every later feature (search, picker, copy name) is built once; the file format stays, so no app (Lua or Swift) changes. Rejected B (panel swallows mixer: mixers lose shareable Vercel links, panel window gets heavy) and C (share format only: two UIs drift, features built twice).

---

### Knob discovery

Three layers: a rule that agents declare feel values as knobs as they write them (same length as a literal, one block at the top, feel values only, so code doesn't get worse); a dumb scanner (`tweaks scan`) for existing code; a Sonnet cleanup pass that names, groups, writes notes/search words, picks the likely set, and edits, with one diff per app for review.

---

### Calm organisation

Likely set (3–6) open, the rest in folded sections with value summaries (mixer pattern); usage promotes knobs over time. Fuzzy search offline over names/notes/search words; Haiku fallback only in the Mac panel (no keys in public pages). Element picker: web first via data attributes (ingredients: click-to-component, LocatorJS), HUDs later via region→knob maps. Ask-an-agent sends app + picked element + search words to the coordinator. Copy name copies `App › key`.

---

### Untested and risky

Nothing built. Biggest unknowns: picker for native HUDs (each HUD must report its regions), and the Haiku fallback needs a key path from the panel. Mock values on the page are illustrative.

**Undo:** delete the page folder in `~/projects/pages/site/tweaks-one-panel` and redeploy.
