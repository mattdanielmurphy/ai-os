# Live-tweak config layer (idea exploration)

## 14:05 Options for a live-tweak layer

**Asked:** every app agents build should expose tunable params (esp. UI/UX feel) in one obvious
place, hot-reloaded, no side effects. Confirm it makes sense, sketch 2–3 options, propose rule wording.
Not a build: nothing is made until 👍.

---

### Why it makes sense

Motivating case: trackpad-mixer's fade feel lives as Swift constants (`Fade.loudWeight` in
`Sources/Mixer.swift`, ~1s + 0.12s/dB, rises ×1.3, 1–8s clamp). Each tweak = edit code, rebuild,
restart (restart even mutes output during the gap). That loop is why tuning the fade curve today
took agent round-trips. With the knobs in a file, Matt edits a number and hears it on the next fade.

Existing tools checked: web has Tweakpane / lil-gui / Leva (slider panels); Swift has InjectionIII
(code hot-reload, rejected: needs reading code and can re-run side effects) and the archived
FBTweaks (iOS only). Hammerspoon already uses `hs.pathwatcher` for reloads. Nothing Mac-wide exists
for "every app's knobs in one place", but the parts do.

---

### Option A: tweaks.json + file watch (recommended first step)

- Each app has `tweaks.json` at its repo root: `{ "fade.loudWeight": {"value": 2.2, "min": 1, "max": 4, "note": "..."} }`.
- Shared loaders, written once: `hud-kit/Sources/Tweaks.swift` (DispatchSource file watch,
  `Tweaks.double("fade.loudWeight", default: 2.2)`) and `~/.hammerspoon/modules/tweaks.lua`
  (`hs.pathwatcher`). JS apps: a tiny watcher in the same shape.
- Read on use, not cached at launch, so a save applies on the next frame/fade. Reload only swaps
  values: never restarts, re-registers hotkeys or touches state. Bad JSON → keep last good values,
  small corner indicator.
- Edit in VS Code. Cost: ~1 small module per runtime plus moving each app's constants as it's touched.

---

### Option B: A + one shared Tweaks panel

- A Hammerspoon webview (or local page) with Tweakpane that lists every `tweaks.json` it finds
  (registry in `~/.hammerspoon/tweaks_registry.json`) and draws sliders/colour pickers from min/max.
- Dragging a slider writes the file; Option A's watcher applies it live. Apps need nothing extra.
- Takes a HUD slot, behaves like a standard window. Do after A has 2–3 apps using it.

---

### Option C: standing rule only

- Rule says "put feel constants in one config block at the top of the main file". No hot reload.
- Cheapest, but still a rebuild per tweak; rejected as the main answer, fine as fallback for throwaways.

---

### Proposed rule wording

For `~/projects/ai-os/.rules/` (new `tweaks.md` or `ui_web.md`), ~/.claude/CLAUDE.md and project instructions:

> **Live tweaks (2026-10-22):** every app or module you build for Matt keeps its feel knobs (timings,
> fade curves, sizes, colours, thresholds) in one `tweaks.json` at the repo root, each with value,
> min, max and a one-line note, loaded through the shared Tweaks module (hud-kit `Tweaks.swift`,
> Hammerspoon `modules/tweaks.lua`). Read values on use so a save applies live; reloading only swaps
> values (no restarts, re-registering or side effects); bad JSON keeps the last good values. When
> Matt asks to tune a feel, change `tweaks.json`, not code.

---

### Untested / risky

- Nothing built. Swift apps read values in hot paths (per-frame); a dictionary lookup is cheap but
  should be benchmarked in the mixer.
- Undo: delete the IDEAS.md entry; no rules changed yet.
