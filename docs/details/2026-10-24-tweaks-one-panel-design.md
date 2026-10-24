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

## 07:45 Step 1 built: Tweaks panel runs on Knobs

**Asked:** Matt 👍'd option A. Step 1 = the Knobs component, and the panel switches to it with likely set, folds, search, copy name.

---

### What is live

- `~/projects/ui-mixer/knobs/knobs.js` + `knobs.css`: dependency-free component. Knob kind follows the value (number → slider + number field, bool → switch, hex → colour, `choices` → chips, else text). Key `fade.hold` → section "Fade", label "Hold".
- Tweaks panel (`~/.hammerspoon/modules/tweaks_panel.html/.lua`) now inlines Knobs instead of Tweakpane (moved to Trash). All old features kept: follow focus/pin, Apply (+ rebuild), Reset all, presets, open project/file, notes, Esc closes.
- New: Likely set, summarised folds, per-section Reset, search, copy name, ⌘Z/⇧⌘Z.

---

### How Likely works

Only for apps with more than 8 knobs (small apps just show every section open). Up to 6 knobs: those marked `likely` in the file (future), moved before, or changed from default; most-moved first. Moves are counted in `hs.settings` `tweaksPanel.usage`, one count per drag (2 s debounce). The set is decided when the panel renders, so knobs don't jump while you drag. Likely rows show their section name in the note.

---

### How search works

Offline fuzzy match over label, key, note, tags, section and app; every typed word must match. A small plain-word map helps ("slow"/"fast" → timings, "big" → sizes, "faint" → opacity). "/" or ⌘F focuses it; Esc clears it (a second Esc closes the panel). No AI fallback yet (step 4).

---

### Shared module

Source of truth is `ui-mixer/knobs/`; `knobs/sync.sh` copies it into `~/.hammerspoon/vendor/knobs/` (Hammerspoon pages load through `wv:html()`, so files are inlined, and the public Hammerspoon export can't depend on `~/projects`). Rejected: reading straight from `~/projects/ui-mixer` (breaks the export).

---

### Tested

Headless WebKit test with the real reels (20 knobs) and reload-indicator files: 21 checks pass (likely order, folds, summaries, slider → set, undo, in-place update, search, Esc, copy, Apply, presets, picker, no sideways scroll at 360 px, no errors light/dark). Lua tests pass; Hammerspoon reloaded and the inlining checked inside it.

**Not tested:** the real window on screen (I didn't open it; it would change your screen). Clipboard copy inside the real webview (headless used the fallback path).

**Not done yet:** the UI Mixer's own rail still uses the old shell; moving it onto Knobs is next. Steps 2–4 (agent rule + scanner, picker, ask-an-agent/AI search) wait.

**Undo:** `git revert` 01c9a10 in ~/.hammerspoon (restores Tweakpane from git history).

## 07:25 Headings: shorter, not balanced

**Asked:** Matt's phone screenshot: the balanced subheading "1 · AGENTS MARK THEM AS / THEY CODE (FROM NOW ON)" was no better, maybe worse.

---

### Why balance failed

`text-wrap: balance` removes the lone word by making two half-width lines. For a short subhead that still reads as broken. The real fix is copy: a subheading should fit one line on a phone. Same idea as Matt's "rewrite the line" thought, done by hand here.

---

### Headings rewritten

All long subheads cut to one line ("1 · Agents mark them", "2 · A scanner", "3 · A cheap cleanup pass", "A. One shared component", "C. Keep both"…); the dropped words moved into the first sentence below. Redeployed.

---

### Checker catches it now

`orphans.cjs` also flags any h2–h6 that wraps at all, and an h1 whose last line is one word. On the old page it flagged all six bad headings at 360 px; the new page is clean at all 5 widths.

---

### Rule tightened

"No orphans" now says: subheadings fit one line at 360 px; balance is only a safety net.

## 07:30 do.test links become the extra

**Asked:** do.test links for md files and artifacts "really suck"; they should come in addition to the normal links.

---

### New link format

Details and other markdown: sent with SendUserFile, linked by the `/mnt/project-files/...` path (opens the in-app preview, works on the phone), attached on the reply, then `· on Mac` (do.test) after it. Pages/artifacts: their https link first. do.test alone stays only for folders and code.

---

### Where it's saved

`.rules/core_safety.md` (file-link rule + details-file bullet), `~/.claude/CLAUDE.md`, and the `link-files-and-folders` memory. Compiled with build_rules.py and pushed.
