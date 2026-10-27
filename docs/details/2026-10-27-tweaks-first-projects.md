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
