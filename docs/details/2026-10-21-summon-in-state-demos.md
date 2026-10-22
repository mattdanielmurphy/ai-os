# Summon-in-a-state demos

## 20:58 Idea recorded + convention proposal

Matt asked (via the coordinator, from the "Tiered Mac-control banner" thread): whenever an agent builds something visible, give him a button to summon it in a given state, like agents do when testing. Record it, check existing patterns, propose the smallest convention plus a rule. Wait for his OK before building or changing rules.

Recorded in `IDEAS.md` at the ai-os root (new file; ai-os had no IDEAS.md).

---

### Existing patterns found

- `~/.hammerspoon/modules/claude_control.lua` already has `M.demo(tier)` bound to `hammerspoon://claude-control-demo?tier=light|full`. Opens the real banner with no agent behind it, auto-releases after 8s. This is exactly the idea, for one module.
- `turn_swap.lua` uses a URL event too (`ai-os-turn`), so URL routes are the house style.
- `menu_bar.lua` has a ⚙︎ "AI-OS Controls" menu: the natural home for the buttons.
- `claude-palette` / `pf` is search only today (stage 1), so it's a later surface, not the first.
- Outside tools: Storybook (web) and SwiftUI Previews do this per component, but neither covers Hammerspoon HUDs or a running Mac. Not worth adopting for this.

---

### Proposed convention

- One route: `hammerspoon://demo?id=<thing>&state=<state>`.
- A tiny registry `modules/demos.lua`: each module calls `demos.register(id, {states...}, fn)`.
- The ⚙︎ menu gets a "Demos" submenu built from the registry: thing → state.
- Swift apps (trackpad-mixer etc.) accept `--demo <state>`; the registry entry just launches that.
- Demos never need the take-control banner: Matt triggers them himself.
- Migrate `claude-control-demo` into it as the first entry.

### Proposed rule

"Anything visible you build (HUD, overlay, menu, banner) ships a demo entry for each state you tested, registered in `modules/demos.lua`." Agents already create those states to test; this just keeps them as buttons.

Rejected: a separate demo app/launcher (bigger build), per-module ad hoc URLs (no single list to browse).

Untested: nothing built yet. Undo: delete the IDEAS.md entry.
