# Tweaks-first projects (2026-10-27)

## 08:05 Where Tweaks stands, and should projects be built around it

**Asked:** Matt, thinking out loud (no build, freeze on): where are we on Tweaks and on building new projects around it? Will it distract agents and make them worse? Idea: deterministic Python scripts make everything a tweak, and Claude only prunes ("a developer would never change this") and organises.

---

### Tweaks status today

- Live: the ⌃⌥⌘T panel runs on the shared **Knobs** component (option A from the 2026-10-24 design, `~/projects/ui-mixer/knobs/`), with the likely set, folds, search, copy name, presets, Apply + rebuild. 11 Hammerspoon modules have tweaks files; hud-kit apps use `Tweaks.swift`.
- Rule 1g already tells agents to declare feel knobs as they write code.
- Not built: the scanner (`tweaks scan`), the Sonnet cleanup pass, the element picker, hover-to-highlight (parked idea), and the UI Mixer rail move onto Knobs ([UI Mixer onto Knobs](#cmsg_01CUPXyY9oUwKVDFREVDpYDr2LydtyRWx3KJfNEhQAUFst) is waiting for review).
- Sources: `docs/details/2026-10-24-tweaks-one-panel-design.md`, `IDEAS.md`.

---

### Does it burden agents

Mildly, and only if the rule asks for judgement on every literal. Today's rule asks agents to decide what's a feel value while coding, which is a small extra thought per number. The real risk is not "worse at the job" but drift: some agents forget, others over-knob. Moving the bulk of it to a script removes most of that cost. Agents then only write values as named constants at the top of a file (normal good practice anyway), and the tooling does the rest.

---

### Matt's idea matches the planned design

The 2026-10-24 design already had three layers: agent rule, dumb scanner, Sonnet cleanup. Matt's version shifts the weight onto the scanner, which is better: deterministic, free, repeatable, and runs as a hook or nightly job (systems over one-offs).

How the scanner would work: parse each source file (Lua, Swift, JS) for numeric, colour, bool and duration literals and top-level constants; skip obvious non-knobs (0, 1, array indexes, loop bounds, API constants, version numbers); write candidates to the tweaks file marked `candidate`. The cleanup pass (Sonnet, cheap) reads candidates and marks each keep / hide / drop with a reason, names and groups the keepers, writes notes. One diff per app for review. Drop decisions are remembered so they never come back.

Hard part: turning a literal into a knob means editing the code to read the tweak. That rewrite should be the script's job for named constants (mechanical), and the agent's only for inline literals.

---

### Options

1. **Recommended: scanner + prune pass, agents just name constants.** Change the rule to "put feel values in named constants at the top"; a script wires constants to Tweaks; Sonnet prunes and organises. Least agent burden, most coverage.
2. **Keep today's rule, add the scanner only for old code.** Smaller build; agents keep deciding while coding.
3. **Opt-in per project.** Only apps Matt actually tunes (HUDs, reels, mixers) get Tweaks; everything else skips it. Lowest effort, least magic.

Rejected: "everything is a tweak, no pruning" (panel becomes a wall of 200 sliders; it fights the likely-set design).

**Untested:** all of this is design; nothing built. **Undo:** nothing to undo.

## 08:05 Freeze means no new projects

**Asked:** Matt clarified the freeze: no new projects and lean toward simplifying until he and Tyler start merging their Claude setups. Tweaks work is fine, "a no-brainer good thing to have working well". He also asked how to say "Tyler and I's merge".

**Did:** saved the rule as core_safety 1p (rebuilt rules) and in memory. Grammar: "the merge of Tyler's and my setups", or "our merge". Didn't start the build: he hadn't given the 👍 on the offer yet, and it's a few hours of work, so one 👍 is cheap insurance.

---

### Scanner build plan

The recommended option: a script turns named constants into tweaks, then Sonnet prunes and organises. It lives inside the existing Tweaks module, so it adds no new project. It starts on the Hammerspoon modules.

## 08:20 Panel docks beside its app: logic check before building

**Asked:** Matt: the Tweaks panel should be summoned per app, dock on the left, push the app over, not float on top, not follow cmd-tab, toggle closed and restore the app; a jump menu at the top for background utilities, which turns the panel into its own Dock app. Restyle it using a new shared UI library built by a separate agent. He also 👍'd the scanner.

**Did:** asked the coordinator to start a separate thread for the shared UI library, quoting his request and pointing it at the design threads and UI rules, and to message this thread when it's ready. Restated the panel logic back to him before building (rule: restate complex logic first). Started the scanner, which was approved.

---

### Panel logic as understood

1. Pressing ⌃⌥⌘T in an app that has tweaks opens the panel on the left edge of that app's screen, already set to that app. Apps whose Hammerspoon helpers attach to them count too: Claude shows Cmd-K, Quote comments and Thread queue.
2. If the app's window filled the screen, it shrinks to fill the space that's left. Otherwise it just slides right until it clears the panel. Its original position is remembered.
3. The panel is an ordinary window, not always on top. It doesn't follow focus or cmd-tab.
4. Pressing ⌃⌥⌘T again closes the panel and puts the app's window back where it was.
5. In an app with no tweaks (a system app), the panel opens with a picker that asks which app or utility to tweak.
6. If the jump menu switches the panel to a background utility, the app goes back to where it was, and the panel becomes its own Dock icon you can cmd-tab to. Panels tied to an app never get a Dock icon.

---

### Open questions on the panel

- Jump to another app that has a window: I assume the first app is restored and the panel docks beside the new one instead.
- Dock icon: Hammerspoon windows can't have their own Dock icon. Detached mode needs a small native wrapper app (hud-kit Swift around the same page). It's the main extra cost.
- Width: fixed at about 400 px, with its own tweak.
- If you move or resize the app while the panel is open, closing still restores the original frame unless you moved it a lot. I'd keep your new position then.

## 08:50 Scanner built, panel restyled with Slub UI

**Asked:** Matt 👍'd the scanner. The shared UI library thread finished the "Slub UI" kit (`~/projects/ui-mixer/kit`, built on Web Awesome) and asked this thread to use it in the panel.

---

### Scanner and prune results

`~/.hammerspoon/bin/tweaks scan` reads every Hammerspoon module without AI. It picks up top-level constants (`local HOLD = 1.2`), named numeric fields (`alpha = 0.8`) and timer delays. It skips values that are already knobs, 0/1, hex marks, and names like PORT, VERSION and PATH. That found 457 candidates. `tweaks prune` asks Sonnet, per module and without tools, whether a developer would ever turn each value. Keepers get a key, a note and a slider range. Sonnet kept 149 and dropped 308, all with a short reason. Every decision is stored in `~/.hammerspoon/tweaks/candidates/<module>.json`, keyed by the surrounding code rather than the line number, so a decision is never asked twice. `tweaks report` lists the keepers. Spot check: claude_notify kept font sizes, radii, opacity and timings, and dropped icon geometry and hit areas. Tests: `tests/tweaks_scan_test.py`.

Not done: wiring the 149 keepers into the modules' code (replacing each literal with `T("key")` plus a declaration). That's a per-module edit an agent should do and check, so I left it as the next step. Rule 1g now says to put feel values in named constants and lets the scanner find the rest.

---

### Panel now uses Slub UI

The panel inlines `vendor/slub-ui/slub-ui.js` and the chosen look's CSS (synced by `ui-mixer/knobs/sync.sh`, which now builds the kit too). The jump menu is `<slub-jump>`: ⌘J opens it, you type to filter, and it's grouped into Apps (the ones with focus bundle IDs) and Background utilities, each showing a knob count. Sliders, number fields, switches, colours, chips, search, preset fields and buttons all come from the kit. The panel's own hard-coded colours are gone; every colour comes from the look. The panel has its own tweaks entry, "Tweaks panel" › `look.style` (Hairline, Prairie or Synth chips), and changing it reopens the panel in the new look. Small fix in `tweaks.lua`: `choices` declared in code now get seeded into the file. The headless WebKit test passes all 23 checks in every look, light and dark. Hammerspoon reloaded fine.

Untested: I didn't open the real panel on your screen; you'll see it with ⌃⌥⌘T. The docking behaviour isn't built yet; it's still waiting for your 👍 on the logic.

**Undo:** revert commit 729afa6 in ~/.hammerspoon and 70181b4 in ui-mixer.

## 12:05 Plain look in the panel, and 119 knobs wired into the code

**Asked:** Matt picked the "plain" Slub UI look for now (hairline is the runner-up), so the panel doesn't need a look setting. His 👍 on the 08:50 reply was the go to wire the kept knobs in.

---

### Plain look, no look setting

The panel now inlines `vendor/slub-ui/slub-ui.css`, the suite stylesheet, which is plain by default. The "Tweaks panel › look.style" knob and its file are gone. `sync.sh` copies only that one stylesheet now. The UI test passes, and Hammerspoon reloaded fine.

Mistake: my `git commit -a` in ui-mixer (739e57b) also swept in another session's unfinished edits to `dist/reel-player.html`, `kit/entry.js` and `knobs/knobs.js` under my commit message. Nothing was lost; those edits are pushed as they were. If that session wanted them committed separately, the commit can be split.

---

### How the knobs got wired

There's a new step, `bin/tweaks wire [--dry] [module]`, and it's mechanical: no AI. For each knob Sonnet kept, it does one of three things. A top-level constant (`local STALE = 3 * 24 * 3600`) is deleted, and every place that used it now reads `T("queue.staleSeconds")`, so the value is live. An inline field (`alpha = 0.95`) or a timer delay (`doAfter(0.3, …)`) has its number replaced with `T("key")`. Matching `xRadius` and `yRadius` values share one knob. Declarations go into the module's existing knobs table, or into a new `TWEAKS` block at the top that opens Tweaks only inside real Hammerspoon, so test fakes just get the defaults. Every rewritten file is checked with `luac -p` before it's written, and comments are left alone.

Result: 119 of the 149 keepers are wired across 26 modules. Every Lua test passes, and Hammerspoon reloaded with "all modules started" and no errors. 39 apps are now in the Tweaks panel.

---

### Problems caught and fixed

- **Symlinks:** qwerty_midi, ps5_dashboard and ui_recorder are symlinks into their own repos (qwerty_midi is a generated bundle). The first run replaced those links with files. I restored them from git, checked that the target repos weren't touched, and `wire` now skips symlinks.
- **Test fakes:** some tests fake `hs`, so the guard is `type(hs.reload) == "function"`. thread_queue's test stub now returns each knob's default.
- **Knobs declared before use:** fields in a table that comes before the module's own tweaks block (song_key's CFG) are skipped, not wired.
- **Two tweaks blocks in one file:** otp_copy and tv_resync open Tweaks inside a function, so I merged their new knobs into the existing tables by hand. `wire` now skips modules like that and says so.
- **Sonnet slips:** otp_copy's "pill height" was really the width, so it's now `look.pillWidth` with a sensible range. claude_warm's lead time was read as 10 instead of 10 * 60; that's fixed, and the scanner now reads whole arithmetic. A value outside its slider range now widens the range.

---

### Not wired yet

30 keepers: the three symlinked modules (they need wiring in their own repos), song_key's 6 CFG values, and 12 in eye_breaks (constants used before its tweaks block). These are small hand jobs per module.

**Untested:** I didn't drag any of the new knobs live on screen. The modules load and the tests pass, but you're the first to turn them.

**Undo:** revert 70ba67e (wiring) and e98f3a1 (plain look) in ~/.hammerspoon.
