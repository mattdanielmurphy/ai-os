# Take-control banner tiers (2026-10-21)

## 20:58 Light tier + softer full banner

**Asked:** (via coordinator) a small audio restart showed the full intense banner. Full glow + big banner only when Matt must keep hands off keyboard/mouse; lighter treatment for low-impact actions; smaller banner and softer glow overall. Keep Esc/Stop and the queue.

---

### Two tiers

- **Full (default, plain `ask`)**: centre banner + edge glow. For typing, clicking, dragging, moving the mouse.
- **Light (`ask "<what>" 3 --light`)**: 360×52 translucent pill, top-left, no glow. Title "Claude, in 3: <reason>" then "Claude: <reason>"; small Stop button; clicking the pill = Not now. For opening/revealing files or apps, focusing windows, play/pause, volume, restarting audio.
- Same queue, same countdown, same Esc (not now) / Esc Esc (stop) / Stop behaviour, same 2h block on Stop.
- Default stays full on purpose: an agent that forgets the flag errs on the loud side, never the quiet side. Rejected: making light the default with `--hands-off` for full.

---

### Softer full banner

- Banner 820×170 → 560×118, text 26/15 → 19/13 pt, buttons smaller.
- Glow inset 15% → 8% of each screen edge, edge alpha 0.85 → 0.5, rim 10px → 4px, pulse slower and shallower (0.85±0.15).

---

### Files

- `~/.hammerspoon/modules/claude_control.lua`: `ask(..., light)`, `lightCanvas()` / `fullCanvas()`, glow numbers.
- `~/.hammerspoon/bin/claude-control`: flags parsed anywhere (`--light`, `--urgent`); `lock` ignores `--light`.
- `~/.hammerspoon/hud_slots.json`: new `claude_control_light` slot (topLeft, primary screen). Overlap test passes.
- Rules: `.rules/core_safety.md` (Two tiers bullet), `~/.claude/CLAUDE.md`, input guard deny message now suggests `--light`.

---

### Tested / untested

- Tested: Lua and zsh syntax, HUD overlap test, hot reload picked up the new `ask` (7 params), quiet `lock`/`done` queue round-trip.
- **Untested: the visuals.** I didn't draw either banner; Matt should look.
- Coordinator-owned project instructions ("Working on Matt's Mac") don't mention `--light` yet.

### Undo

`git revert` the commit in `~/.hammerspoon` and the one in ai-os.

## 21:00 Preview links + Hammerspoon crash

**Asked:** Matt wants to summon things in a given state himself. Coordinator scoped this thread to the banner tiers only; the general version is another thread.

---

### Preview links

- `hammerspoon://claude-control-demo?tier=light` and `?tier=full` (bound in `claude_control.lua` `M.start`). Each shows the real banner with no agent behind it, then releases after 8 s. Esc / Stop work as usual (Stop blocks nobody, there's no agent).
- From a terminal: `open -g "hammerspoon://claude-control-demo?tier=light"`.
- Untested: Hammerspoon crashed before I could confirm the reload.

---

### Crash

- Hammerspoon crashed at 20:57:38 (`Hammerspoon-2026-10-21-205738.ips`): SIGTRAP inside `hs.ipc` `ipc_sendMessage`, during an `hs -c` callback. That is an IPC reply to a command-line client that had gone away, not the banner code.
- Most likely trigger: my own `hs -c` checks, killed by a 5 s watchdog right after the hot reload, possibly together with the other thread's testing. My code change itself isn't on the stack.
- I didn't relaunch Hammerspoon (coordinator asked Matt).
- Possible fix for later: avoid `hs -c` straight after a reload, or make the CLI wrapper wait for reload to settle.

## 21:14 Links failed; mods question

- `hammerspoon://` links in a thread reply didn't work (the app likely doesn't open custom URL schemes). Terminal fallback: `open -g "hammerspoon://claude-control-demo?tier=light"`.
- Mods: per the code-project-parity memory (verified 2026-10-20), mod hooks (prompt.submit etc.) DO run in project threads, coordinator-spawned included; only what a mod draws (band, pane, toast) and the `/` menu don't show on the project page.
- Action-button idea recorded in ai-os `IDEAS.md`; asked the coordinator to give it its own thread.
