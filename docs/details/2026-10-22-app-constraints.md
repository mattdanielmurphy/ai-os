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

## 14:35 Terracotta banned

Matt (via coordinator, his words): "Never ever make anything this color ever again." Swapped the interim accent
in ARCHITECTURE.md to sage (#4F8A6C / #7FB89A); sage was already the house second hue, and green isn't on any
banned list. Added the ban to `.rules/core_safety.md` (compiled), `.rules/web_design.md` (which used to *recommend*
terracotta `#c96442`) and `~/.claude/CLAUDE.md`. Not changed: the mixer's live accent `#C2502F` and the take-control
banner orange; both are listed as drift to recolour. Undo: revert the commit.

## 14:40 Ship-ready by default replaces "not an audience"

Matt's comment on ARCHITECTURE.md section 8 reversed the 2026-10-21 rule. New rule, global: every build gets the
cheap last 10% (self-contained, settings, onboarding, README, self-explanatory UI); agents judge per build whether
it's just for Matt or for the world and say so in one line; only real-potential builds get heavy shipping work.
Added "Discoverable by design" as its own rule (his bad memory + love of discovery): visible hints for every
shortcut/gesture/modifier, clear empty states.

Changed: ARCHITECTURE.md sections 8–9 + checklist + draft rule line; `.rules/core_safety.md` 1h/1i (compiled);
`~/.claude/CLAUDE.md` (old line replaced); memory `software-for-matt-not-audience` trashed, `ship-ready-by-default`
added. The project instructions still carry the old "software for HIM" lines; asked the coordinator to update them
(only it can). Kept "flag features for imagined users" so the rabbit-hole guard survives.

## 14:55 No colours in the plan

Matt (review thread): the plan must prescribe no colours, since the palette isn't picked; stress one unified
system; agents never invent a colour; large master palette with a small active subset that grows per app (~100
apps someday). Rewrote ARCHITECTURE.md section 6: no hex values, no named accent, no "warm ink/paper"; kept roles,
the banned list, light default, type, icons. Added "Never invent a colour" to core_safety.md (compiled) and
~/.claude/CLAUDE.md; memory no longer mentions sage. The review's top 4 (enforcement scripts, shared state folder,
share formats not behaviour, one palette.json) are NOT applied yet; they wait for Matt's 👍 in the review thread.

## 15:00 Light and dark for everything

Matt (review thread): light and dark mode are part of designing every app. ARCHITECTURE.md section 6 + checklist
now require both modes, checked; light default, dark via system appearance. Added to core_safety.md (compiled)
and ~/.claude/CLAUDE.md. Consistent with the old "light by default" rule; it only adds that dark must exist too.

## 15:05 web_design.md rewritten

Coordinator relayed the review's catch: `.rules/web_design.md` ordered a fresh random palette per project (via the
archived generate_design_brief.py) and prescribed specific colours, contradicting "never invent a colour". Rewrote
it: colour from the shared palette only, banned list kept, borrowed style-guide colours removed. Light/dark rule
now names the native mechanisms too (dynamic NSColor, Hammerspoon appearance watch), since ui_web.md only covered web.
