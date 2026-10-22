# Architecture plan second opinion (2026-10-22)

Thread: "Architecture plan second opinion". Reviews `docs/ARCHITECTURE.md` (draft, commit 4ebf24b4) from the
"Shared app architecture constraints" thread. Read-only review: nothing in the plan or the apps was changed.

## 14:45 Second opinion on ARCHITECTURE.md

**What Matt asked (via the coordinator):** a fresh, independent read of the shared app plan: gaps, risks,
simpler alternatives, anything that will bite later, in priority order. Report in short points, then send the
notes to the drafting thread. 👍 = the drafting thread adopts the top notes.

**What I read:** the plan (sections 1-9, checklist, open decisions, rule line), the drafting thread, and the
live code it governs: `~/.hammerspoon` (44 modules, `tweaks.lua`, `brand.lua`, `suite.lua`, `hud_slots.json`,
`hud_positions.json`, `tweaks_registry.json`, `bin/ship-public`, tests), `~/projects/hud-kit` (all four
sources + tests), `~/projects/trackpad-mixer` (build.sh, Info.plist, tweaks.json, Palette in HUD.swift),
`~/projects/lidstay`. `mac-utilities` is not a folder on the Mac: it's the public repo that
`bin/ship-public` builds from `~/.hammerspoon`. I found no "launcher" project to check.

**Tests today:** hud-kit `tests/run.sh` passes; all five `~/.hammerspoon/tests/*.lua` pass.

**Verdict:** the plan's direction is right (platform by job, kits, registries, tweaks, roles). Its weak spot is
that almost every constraint is prose that an agent must remember, and the evidence from today says they
don't. The four notes below are ranked by how much later pain they prevent per unit of work.

---

### Enforce with one check script

**Problem.** The plan says every registry "has a test that fails on a clash", but nothing runs those tests:
no git hooks in `~/.hammerspoon`, hud-kit or trackpad-mixer, and `auto_commit.py` runs no tests. Same for the
colour rule: the plan says "one sage accent, don't add new one-off hexes", yet on the same afternoon the quote
tool got a brand-new teal (`#2b5f75`, commit 6432f3b, 14:33). Sage (`#4F8A6C`) appears nowhere in code.
There are 248 distinct hex literals across the Lua and HTML modules (596 literals in `qwerty_midi.lua` alone).

**Proposal.** One `check` script per kit, wired as a pre-commit hook in each app repo (and called by
`ship-public`, which today only runs `suite_test.lua`):

- run the kit's unit tests (hud-kit `tests/run.sh`, `~/.hammerspoon/tests/*.lua`);
- slot clash test (exists);
- duplicate hotkey chord test (cheap grep of `hs.hotkey.bind`, see below);
- colour lint: fail on a hex literal in a changed file outside the palette file, and on any colour in the
  banned warm-orange hue band. Allow-list existing files so it only stops *new* drift.

**Why first.** It turns sections 3, 5 and 6 from hopes into gates, costs maybe an hour, and protects every
later step. Rejected alternative: a CI service; overkill for local, mostly private repos.

---

### One shared state folder

**Problem.** Shared state is scattered over four conventions, and the Swift kit is hard-wired to Hammerspoon's
config folder:

| State | Where it lives now |
|---|---|
| Slots | `~/.hammerspoon/hud_slots.json` (read by `Slots.swift`) |
| Remembered HUD spots | `~/.hammerspoon/hud_positions.json` (written by `HUDWindow.swift`; untracked and not gitignored, so it will get committed by accident) |
| Tweaks registry | `~/.hammerspoon/tweaks_registry.json`, holding absolute `/Users/matt/...` paths |
| Lua tweaks | `~/.hammerspoon/tweaks/<module>.json` |
| Swift tweaks | in the app's repo (`~/projects/trackpad-mixer/tweaks.json`): every tuning session dirties git, and the path in code is `~/projects/trackpad-mixer` |
| lidstay | `/Users/Shared/lidstay/` |

That clashes with the plan's own section 8 ("self-contained, no hard-coded Matt paths"): any hud-kit app
handed to someone else writes into a `~/.hammerspoon` they may not have.

**Proposal.** One neutral folder, e.g. `~/Library/Application Support/MDMA/` with `slots.json`,
`positions.json`, `palette.json`, `hotkeys.json` and `tweaks/<app>.json`. Defaults stay in code (as now), so
the user-values file can live outside the repo. The Tweaks panel then just lists `tweaks/`, so
`tweaks_registry.json` and its absolute paths disappear. Hammerspoon keeps working by reading the new paths
(or a symlink during the move).

**Why now.** One Swift app uses hud-kit today; moving three paths in hud-kit and two in Lua is small. After the
next two or three Swift HUDs, it's a migration. lidstay already shows the right shape: standalone first, and
it defers to the suite when the suite is present.

---

### Port formats not behaviour

**Problem.** Section 2 says that when one kit has a behaviour, port it to the other kit "with the same feel".
Section 4 says the Lua kit gets the HUDWindow behaviour. That means re-implementing drag, centre-snap, edge
resize and Option-symmetric resize in `hs.canvas`, then keeping two implementations and two test suites
feeling identical forever. Every new shared behaviour doubles in cost, and the copies will drift.

**Proposal.** Split the rule:

- **Data formats are shared by both kits:** slots, positions, tweaks, palette, hotkeys. A JSON reader is a
  few lines in either language, already done for slots and tweaks.
- **Interactive behaviour lives in one kit only (hud-kit).** A Hammerspoon HUD that needs window behaviour
  moves to Swift when it's next touched, which section 1 already says for new HUDs.

Rejected: rendering Hammerspoon HUDs through a Swift host over IPC; worth revisiting only if the Utilities
app becomes that host (an open decision in the plan).

---

### One palette file for all

**Problem.** Section 5 makes colours tweak knobs per app; section 6 says colour by role from one palette.
These pull apart: if each app has its own `look.accent` knob, tuning one app forks the look. The plan also
proposes two hand-kept copies (`Palette.swift` and `palette.lua`) and there's a third consumer it doesn't
mention: the HTML panels (`tweaks_panel.html`, `gemini_thread_search.html`, ps5 dashboard, song key).
hud-kit's own doc comment shows `.color("look.accent", "#ff8a00")`, an orange, as the example agents will copy.

**Proposal.** One `palette.json` in the shared folder: roles (`ink`, `paper`, `accent`, `track`, `muted`), each
with light and dark values. Swift and Lua read it at runtime the same way they read slots; HTML gets it as
CSS variables injected by the module that opens the webview. The palette shows as one entry in the ⌃⌥⌘T
Tweaks panel, so retuning the accent changes every app at once. Per-app knobs pick a role, never a hex. When
the palette thread lands, its tokens just replace the file's values. Fix the hud-kit example while there.

---

### Other notes, lower priority

---

### Shared Escape stack

Section 4 says every modal closes on Escape. Today each module grabs a global Escape itself
(`clipboard.lua`, `eye_breaks.lua`; `clipboard.lua` also grabs ⌘Z globally while its toast shows). Two
transient UIs up at once fight over the key, and while either is up, Escape never reaches Ableton or the front
app. A small shared `dismiss` module (one Escape owner, closes the topmost thing, only holds the key while
something is showing) is the shared piece section 4 really needs.

---

### hud-kit build and pinning

- Apps compile hud-kit by relative path (`../hud-kit/Sources/*.swift`), unpinned: a hud-kit edit silently
  changes every app on its next build, and a clone of an app alone doesn't build.
- hud-kit is private while lidstay and mac-utilities are public; a "for the world" Swift app can't depend on it
  as is. Section 7 also says "its own private repo" for every app, which contradicts public lidstay; say
  "private until Matt publishes it".
- The signing identity and bundle assembly are copy-pasted in each `build.sh`, which the plan itself calls a
  bug. Proposal: `hud-kit/build-app.sh` (assemble bundle, Info.plist with `ca.mattmurphy.<app>`, sign) that
  every app calls; pin hud-kit as a git submodule or tag once an app goes public.

---

### Permissions per app

Section 1 makes every new HUD its own Swift app. Each one is a separate process, login item and set of macOS
permission prompts (Accessibility, Input Monitoring, audio capture), and an unstable signature resets them.
That's the price of crash isolation; it's fine for two or three apps, painful at ten. Decide the Utilities-app
shape (open decision 3: one host vs many apps) before the second Swift HUD, because it decides whether HUDs
are apps or plugins.

---

### Public copy path leak

`bin/ship-public` scans for emails, keys and school details but not home paths. Two shareable modules ship
with Matt-only absolute paths: `clipboard.lua` (`/Users/matt/projects/console-compactifier`,
`webpage-compressor`) and `clamshell_guard.lua`. On Tyler's Mac those features silently fail. Add a
`/Users/matt` check to the scan; it's the cheapest "self-contained" enforcement.

---

### Hotkey registry first step

Before building the planned `hotkeys.json` registry, a test that greps all `hs.hotkey.bind` chords and fails on
duplicates gives most of the clash protection today (about 20 bindings now; the ⌃⌥⌘ namespace already holds
M, L, V, R, T). For section 9 discoverability, the official [HSKeybindings Spoon](https://github.com/Hammerspoon/Spoons/tree/master/Source/HSKeybindings.spoon)
already shows every Hammerspoon hotkey that has a description, so a cheat-sheet overlay is mostly free once
bindings carry descriptions. Note a registry can't see Raycast, Keyboard Maestro or system shortcuts.

---

### Rules in one place

The same app rules now live in four places: project instructions, `.rules/core_safety.md`,
`~/.claude/CLAUDE.md` and `ARCHITECTURE.md`. Today's terracotta ban and ship-ready change each had to be
mirrored by hand, with the coordinator asking the drafting thread to sync them. Proposal: `ARCHITECTURE.md` is
the one source for how apps are built; the others keep a one-line pointer plus the hard bans (banned colours,
input queue, slots).

---

### Smaller notes

- Shared JSON files have no `"version"` field; add one before a format change breaks older builds.
- Remembered positions are absolute and keyed by slot only, not by screen arrangement; a spot set on the
  laptop can land oddly after plugging in a display (it does fall back to the slot when off-screen).
- `Tweaks.register` and `HUDPositions.save` do read-modify-write from several processes; a rare lost write,
  self-healing on next launch. Fine for now.
- The plan should carry a short conformance table (which apps follow which section, what's known drift), so
  agents can tell legacy from a new violation.

---

### How to undo

Nothing to undo: this review changed no code or plan text. Only this details file was added.
