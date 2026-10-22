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
