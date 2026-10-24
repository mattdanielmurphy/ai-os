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

## 07:10 Orphans: name, fix, rule, idea

**Asked:** what's the one word hanging on its own line called; headings must never have one; idea of a robust minimal component library with guards, incl. an LLM rewriting a line to fit.

---

### Orphan is the name

Typographers call a lone word on a paragraph's last line a *runt* or (in web circles) an *orphan*; strictly, "orphan/widow" also mean a lone line split across a page or column. Fix in CSS: `text-wrap: balance` (headings: evens out line lengths) and `text-wrap: pretty` (body: the browser avoids a short last line). `pretty` didn't catch "self-contained." (hyphenated last word), so the last two words were bound with `&nbsp;` (the old "widont" trick).

---

### Page fixed and checked

Added balance/pretty + two `&nbsp;` bindings to the design page, redeployed. New `~/projects/ui-mixer/orphans.cjs` loads a page headless at 360/390/430/768/1280 px and lists every h1–h3/p/li whose last line is one word; before: 3 hits, after: none. It measures each word's line via Range rects.

---

### Rule saved

`.rules/core_safety.md` "No orphans" (compiled into ai-os CLAUDE.md) and a line in `~/.claude/CLAUDE.md`: balance headings, pretty body, bind last two words, check with orphans.cjs.

---

### Component library idea recorded

In ai-os `IDEAS.md`. Order of defences: CSS first (free), then &nbsp; binding, then detect leftovers with orphans.cjs and have a cheap model (Haiku) rephrase only that line. The LLM step is cheap per line but needs a build step that knows the copy source; it suits static pages, not live text. Shrinking text rejected (Matt's own point: mixed heading sizes look bad).

Undo: revert the rule commit; remove the CSS lines from the page.
