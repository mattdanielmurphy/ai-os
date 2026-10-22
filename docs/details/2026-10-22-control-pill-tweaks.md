# Control pill tweaks (2026-10-22)

## 17:50 Pill feedback: position, size, snooze, click-to-thread

Matt's asks: (1) pill top right not top left, (2) more opaque + 20% bigger with same text size, (3) Esc/Esc Esc wording (he finds the UX unclear), (4) click to go to the asking thread + snooze presets.

---

### Top right slot

`claude_control_light` slot moved to topRight (dx 16, dy 14, 432x62). The Claude notify chips already lived top right, so their slot moved down to dy 84 and shrank to 3 chips (276px) to stay clear of the piano card on a laptop-only screen. `claude_notify.lua` now reads its top from the slot map instead of a hard-coded margin. Rejected: placing the pill left of the notify column (lands mid-screen). `hud_layout` overlap check passes.

---

### Bigger and opaquer

360x52 -> 432x62, fill alpha 0.88 -> 0.98, text sizes unchanged (13 / 11).

---

### Snooze chips

Row 2 has `Snooze 30s 1m 5m`. `claudeControl.snooze(secs)`: the holder steps aside (the next agent gets its turn), then rejoins the front of the queue. `state` reports `snoozed:S`; the CLI keeps waiting and extends its deadline. Tested live: ask -> snooze 4s -> granted.

---

### Click opens thread

`claude-control ask ... --thread cmsg_…` builds `claude://claude.ai/epitaxy/project/<chan>?thread=<cmsg>` (format seen in the Claude app's logs); `--link <url>` for anything else. Clicking the pill body opens it; with no link a body click still means "not now". The hint line becomes "Click: open thread · Esc not now". Untested: the actual click (opening the app is Matt's call). Rules updated: `.rules/core_safety.md`, `~/.claude/CLAUDE.md`.

---

### Controls proposal

Not built yet. Options: (1) Esc = dismiss, Stop only by its button (recommended: one key, one meaning; a hard stop stays a deliberate click); (2) Esc = dismiss, Shift-Esc = stop; (3) keep keys, clearer labels.

Undo: `git revert aa1cbd5` in ~/.hammerspoon, `git revert 61e5af04` in ai-os.
