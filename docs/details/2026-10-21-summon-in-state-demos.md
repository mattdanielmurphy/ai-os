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

## 21:20 Chat action links + do mods work in coordinator threads

Matt (moved from the banner thread): the `hammerspoon://` preview links didn't work when tapped in chat. He wants custom links/buttons in chat wired to commands on his Mac. Also asked: are mods only available in Code threads not spawned by a coordinator?

---

### Mods in coordinator threads

Checked the plugin-authoring docs (this build): mods load in every Claude Code session on the Mac, including coordinator-started Remote Control threads like this one. Their hooks run (prompt.submit, tool.call, commands). What they draw only shows on the engine's drawing surfaces: terminal, desktop Code tab, VS Code, and the mobile Code app. The project page is not one of those, so bands/panes/toasts don't show there. The coordinator itself runs in the cloud, so it has no mods at all. Not tested: whether opening this same session in the desktop Code tab sidebar shows its drawings.

---

### Why the links failed

Inferred, not tested: the chat renderer only makes http(s) links clickable and drops custom schemes like `hammerspoon://`. Raycast (`raycast://`) and Keyboard Maestro URL schemes would fail the same way.

---

### Smallest fix: localhost http links

Hammerspoon already runs a local web server (`rcmd.lua`, `hs.httpserver` on localhost:3094). Add a second tiny one, e.g. `http://do.test/demo/banner-light` via puma-dev, that runs only whitelisted actions (the demos registry from the earlier proposal) and returns a page that says "done". Links in chat are plain http, so they should open.

Existing tools considered: Keyboard Maestro's built-in web server (lists macros as buttons at localhost:4490) does the same with no code, but each action needs a KM macro, and its URLs are uglier. Hammerspoon wins because demos live there already.

Limits: tapping opens a browser tab on the Mac (a small "done" page). Works only on the Mac, not the iPhone (it can't reach localhost). Phone would need the VPS or Tailscale: out of scope for now.

Plan: first one test link (banner light preview), Matt taps it from the thread. If the app opens it, build the registry. Nothing built yet; waiting for Matt's OK.

## 21:30 Test action link built

Matt 👍'd the test link and asked what "drawings" meant (mods' on-screen bits: the band above the prompt, side panes, toasts).

---

### What got built

- `~/.hammerspoon/modules/action_links.lua`: `hs.httpserver` on localhost:3095, a whitelist table of path → action. Unknown paths 404; `/` lists the actions as links. The result page says "✓ done" and tries to close its tab after 1.5s (browsers may refuse).
- `~/.puma-dev/do` = 3095, so `http://do.test/...` works.
- Registered in `init.lua` after claude_control; started live without a Hammerspoon reload (`hs -c`), so nothing on screen changed.
- First actions: `/demo/banner/light`, `/demo/banner/full` (call `claudeControl.demo`).
- Tested: curl to localhost and do.test lists the actions; unknown path 404. Not tested: the actual demo trigger (that's visible, Matt taps it) and whether the chat opens http links.
- Risk: any local web page could GET these URLs. Fine while actions are harmless previews; anything risky later needs a token or POST.
- Undo: remove the init.lua line, `mv modules/action_links.lua ~/.Trash/`, `mv ~/.puma-dev/do ~/.Trash/`.
