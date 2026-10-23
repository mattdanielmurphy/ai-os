# Matt's apps: shared constraints

Status: **DRAFT (2026-10-22), not yet a rule.** Matt's 👍 adopts it everywhere; the rule line at the bottom then
goes into `.rules/core_safety.md`.

Covers every app and utility agents build for Matt on his Mac: the MDMA Appothecary Hammerspoon modules
(`~/.hammerspoon`, public copy `mac-utilities`), trackpad-mixer, lidstay, hud-kit, the launcher, and the planned
Utilities app. Goal: they feel like one suite, share code instead of copying it, and never fight each other for
screen space, keys or input.

It builds on (does not replace): the UI and HUD sections of `.rules/core_safety.md`, the HUD slot map, hud-kit,
the live-tweaks layer, and the palette proposal in the "Personal design system and palette" thread.

---

## 1. Pick the platform by job

| Job | Built as | Why |
|---|---|---|
| Glue: hotkeys, watchers, small automations, menu toggles | Hammerspoon module in `~/.hammerspoon/modules/`, registered in the suite | Hot-reloads per module, ships to Tyler via `suite.lua` |
| Any new floating HUD, panel or overlay | Small standalone Swift/AppKit app (`swiftc` + `build.sh`, no Xcode project) that compiles hud-kit in | A crash or edit in one never touches the others (decided 2026-10-22, "Mac app platform choice") |
| A real window with forms/lists (only when needed) | Swift/AppKit first; a web UI only if it must run off the Mac (then Bun + Mantine, CSS Modules) | One native look; web only earns its place when the phone or Vercel needs it |
| Menu bar presence | An item in the suite's ⚙︎ menu, not a new menu bar icon | His menu bar is full; new icons vanish into Bartender |

Existing Hammerspoon HUDs stay where they are unless Matt asks to move them.

---

## 2. Two kits, one behaviour

- **hud-kit** (`~/projects/hud-kit/Sources`) is the Swift kit; **`~/.hammerspoon/modules`** is the Lua kit.
- Any behaviour a second app could use (window handling, toasts, tweaks, slots, input queue, settings) is built
  once in a kit and imported. Copy-paste between apps is a bug.
- When a behaviour exists in one kit only and a second-language app needs it, port it to the other kit with the
  **same file format and the same feel** (same tweak names, same snapping, same timings), not a lookalike.
- Each kit piece has its own test (`hud-kit/tests/run.sh`, `~/.hammerspoon/tests/*.lua`).

---

## 3. Shared registries ("air traffic control")

Apps never hard-code a shared resource. They claim it from one JSON registry that every app reads, and each
registry has a test that fails on a clash.

| Resource | Registry | Read via | Clash test |
|---|---|---|---|
| Screen space | `~/.hammerspoon/hud_slots.json` | `hud_layout.rect()` / `Slots.swift` | `tests/hud_layout_test.lua` |
| Remembered HUD spots | `~/.hammerspoon/hud_positions.json` | `HUDWindow.swift` | n/a |
| Feel knobs | each app's `tweaks.json` + `~/.hammerspoon/tweaks_registry.json` | `Tweaks.swift` / `tweaks.lua` | bad JSON keeps last good values |
| Synthetic input | `claude-control` queue | `claudeControl.withInput()` / `claude-control lock` | one holder at a time |
| Hotkeys | `~/.hammerspoon/hotkeys.json` (planned, IDEAS.md) | shared module, both kits | to be written with it |

New kinds of shared resource (audio devices, the clipboard, notification corners) get a registry of the same
shape when the second app needs one.

---

## 4. Every HUD is a normal macOS window

- Drag anywhere, snap to the screen centre, resize from edges (Option = symmetric), remember the spot
  (`HUDWindow.swift`; the Lua kit gets the same behaviour, same positions file).
- The slot is only the default spot. One HUD changing size never moves another.
- Every modal, drawer, popover and dropdown closes on Escape and on an outside click.
- Routine events (saved, reloaded, synced) get a small corner indicator that fades. Centre toasts only for
  things that matter (`CenterToast.swift`).

---

## 5. Feel lives in tweaks

- Timings, curves, sizes, opacities and colours are tweak knobs (default, min, max, step, note), never bare
  constants. All of them show in the ⌃⌥⌘T Tweaks panel.
- When Matt wants to tune something, move it into tweaks and tell him the knob's name.

---

## 6. One look

No colours are picked yet. This plan deliberately names none; the palette and brand come from the "Personal
design system and palette" and "MDMA Appothecary logo" threads. What is fixed is the system:

- **One unified palette, never an agent's own colour.** Agents never invent, eyeball or copy a colour. Every
  colour comes from the shared palette by role.
- **Large master palette, small active subset.** The master palette is big enough for ~100 apps. The suite uses a
  small subset of it; a new app that needs a new colour expands the subset with the next fitting colour from the
  master palette (recorded with the app that claimed it), never a random pick and never a colour outside it.
- **Colour by role, not by hex.** Code names roles (for example `ink`, `paper`, `accent`, `track`, `muted`), each
  with a light and a dark value. Values live in one palette file per system, generated from the master palette,
  and nowhere else.
- **Banned (Matt):** terracotta (the LLM-default clay brown-orange; orange in general is fine); purple/pink or neon gradients;
  default indigo; glassmorphism for its own sake.
- **Light and dark for everything (Matt, 2026-10-22).** Every app ships light and dark and follows the system
  appearance (light when there's no preference). Every palette role, screen, HUD and icon is designed and
  contrast-checked in both modes before it's done.
- **Type:** the system font; monospaced digits for anything that counts or moves. No web fonts in native apps.
- **Icons:** SF Symbols, tinted by role.
- **HUD panels:** rounded corners, no drop shadows.
- **Until the palette lands:** don't add new hard-coded colours; reuse what an app already has, and expect every
  existing hard-coded colour to move to roles when the palette is adopted.

---

## 7. One suite, one name

- The suite's name comes from `~/.hammerspoon/modules/brand.lua` (MDMA, "Matt Daniel Murphy's Appothecary").
  Standalone apps use it in About text and alerts; nothing hard-codes the name.
- Bundle ids and launchd labels: `ca.mattmurphy.<app>`.
- Each app is its own private repo in `~/projects/<app>` with `README.md`, `AG_CONTEXT.md`, `build.sh`, a test
  script and `tweaks.json`. Installed apps run from a launchd agent, managed with `la`.

---

## 8. Ship-ready by default, polish by potential

- Every app could become a public product, so each one gets the cheap last 10%: self-contained (no hard-coded
  Matt paths, one-step setup), a settings screen (Matt uses them too), first-run onboarding, a README.
- Each app's README says on line 1 whether it's **just for Matt** or **for the world**. Agents make that call;
  only "for the world" apps get the heavy work (distribution, polish for strangers, support).
- Ship-ready means finishing what's built, not adding features for imagined users.
- Look for an existing app or library before building, and prefer the smallest step.

---

## 9. Discoverable by design

- How it works must be self-apparent: visible controls over hidden gestures, a visible hint for every
  shortcut, modifier or gesture (hover tips, labels, keycaps), clear empty states.
- Nothing should only work if you already know it exists.

---

## New app checklist

1. Right platform for the job (section 1)?
2. What does it reuse from a kit, and what does it add to one?
3. Slot claimed, hotkeys claimed (once the registry exists), input goes through `claude-control`.
4. Window behaviour from the kit; Escape and outside click close.
5. Feel knobs in `tweaks.json`.
6. Colours by role from the palette; SF Symbols; designed and checked in light and dark.
7. Repo, `AG_CONTEXT.md`, `build.sh`, tests, `ca.mattmurphy.*`.
8. Just for Matt or for the world? Settings, onboarding, README; every shortcut and gesture has a visible hint.
9. Checked against [EXEMPLARS.md](EXEMPLARS.md) (Low-Tech Guys, Rogue Amoeba, Panic and others): name what it misses.

---

## Open decisions (not part of the draft rule)

- Adopt the master palette from the "Personal design system and palette" thread (waiting on Matt's 👍).
- Build the hotkey registry (IDEAS.md, waiting on Matt's 👍).
- Shape of the Utilities app: a Swift host for the suite's HUDs, or a front end for the Hammerspoon suite.

---

## Rule line (goes into `.rules/core_safety.md` on Matt's 👍)

> **App constraints (Matt, 2026-10-22):** every app or utility built for Matt follows
> `~/projects/ai-os/docs/ARCHITECTURE.md`: pick the platform by job (Hammerspoon glue, standalone Swift HUDs on
> hud-kit), build shared behaviour once in hud-kit or the Lua modules, claim screen space/keys/input from the
> shared registries, keep feel in tweaks, colour by role from the one shared palette (never an agent's own colour), name things from
> `brand.lua`, ship-ready by default, and make every interface self-explanatory. Read it before starting or restructuring any app.
