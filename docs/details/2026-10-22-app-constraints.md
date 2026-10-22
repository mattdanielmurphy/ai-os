# App constraints (shared architecture for Matt's apps)

## 14:30 Draft constraints doc

Asked (via coordinator): one well-described set of constraints so all his apps (MDMA Hammerspoon modules,
trackpad-mixer, lidstay, hud-kit, mac-utilities, launcher, planned Utilities app) stay consistent, share
modules and look cohesive. Draft until Matt's 👍.

Read: the palette thread (proposal only, no 👍 yet), the Mac app platform thread (new HUDs = standalone
Swift apps), the HUD slots thread, hud-kit README/AG_CONTEXT, `brand.lua`, `suite.lua`, UTILITIES.md, the
mixer's `Palette`, the take-control banner colours, IDEAS.md (hotkey registry).

---

### Doc location

`docs/ARCHITECTURE.md` in ai-os. Rule line is written at the bottom of the doc but NOT yet in `.rules/`, because
the brief said the draft is theoretical until 👍. On 👍: paste it into `.rules/core_safety.md`, run
`scripts/build_rules.py`, add to `~/.claude/CLAUDE.md`, push.

---

### Platform by job

Hammerspoon for glue; standalone Swift apps on hud-kit for new HUDs (Matt's earlier decision); web only when it
must run off the Mac. New: "prefer the ⚙︎ menu over new menu bar icons", inferred from the Bartender problem.

---

### Two kits rule

hud-kit and ~/.hammerspoon/modules are the only places shared behaviour lives; ports keep the same file format
and feel. Rejected: one cross-language kit (no clean way to share code between Lua and Swift; shared JSON files
already do the job).

---

### Registries rule

Generalises hud_slots.json to every contended resource; lists the existing ones plus the planned hotkeys.json.

---

### Interim house style

No palette is adopted yet, so the draft codifies what already ships (mixer's terracotta + warm neutrals) and
requires colour-by-role, so swapping in the palette thread's tokens later changes values only. Flagged drift:
take-control banner's separate orange.

---

### Untested and risky

Nothing executable changed. Undo: `git rm docs/ARCHITECTURE.md`.
