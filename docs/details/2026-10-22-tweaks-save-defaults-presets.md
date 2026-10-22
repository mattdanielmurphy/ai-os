# Tweaks panel: changed-knob colour, save as defaults, presets (2026-10-22)

## 17:05 Built and live

Asked (via coordinator): (1) a knob changes colour as soon as it differs from its default; (2) save tuned
values as the new defaults the official build ships with, or as named presets to switch between.

Code: `~/.hammerspoon` commit 7f12087 (`modules/tweaks.lua`, `modules/tweaks_panel.lua`,
`modules/tweaks_panel.html`, `tests/tweaks_test.lua`). Undo: `git -C ~/.hammerspoon revert 7f12087`, reload.

---

### Changed knobs coloured

A knob whose value differs from its default gets the panel's existing `--accent` role colour on its label
plus a 2px inset edge mark (box-shadow, so nothing shifts). Tooltip says "Changed from default X".
Numbers compare with a tiny tolerance, colours ignore case. Same rule in Lua (`M.differs`) and JS.
No new colours: only the panel's existing accent token.

---

### Save as defaults writes code

Decision: defaults stay in code (the knob declarations), matching the architecture review ("defaults stay
in code, as now"). Rejected: a separate committed defaults file (needs bundling in build.sh and a second
source of truth). The panel's **Save as defaults (ships in the build)** button:
- finds the declaring file: a tracked .lua/.swift in the tweaks file's git repo that names the tweaks file
  and declares every changed key (skips tests/, vendor/, tweaks.lua and Tweaks.swift docs);
- rewrites each declaration's first literal (`["k"] = { 1.2` / `.number("k", 1.8`);
- updates the running Lua module's declarations in memory and the file's `default`, so colours clear at once;
- commits and pushes just that file, only if it had no other uncommitted edits (else says "Not committed").
Swift apps (Trackpad Mixer): code is rewritten and committed, but the running app keeps its old defaults
until rebuilt, so the knob stays coloured until then (the panel says so).

---

### Presets kept outside git

`~/Library/Application Support/MDMA/tweak-presets/<app>.json`, the shared state folder the review proposed,
so switching never dirties a repo. Per app: a collapsed **Presets** folder with a picker, Load, Delete,
a name field and "Save current values as preset". Loading sets only knobs the preset knows.
Live values themselves were NOT moved to that folder (that's the separate migration in the review).

---

### Tested

Unit tests for diff + Lua/Swift rewrites (`lua tests/tweaks_test.lua`); end to end on a scratch git repo
(rewrite, commit, preset save/load/delete); panel page rendered in light and dark with stub data. Not
clicked in the real ⌃⌥⌘T window (needs Matt's screen). Risk: regex rewrite only handles one-line literal
defaults; anything else reports "couldn't find the code" instead of guessing.
