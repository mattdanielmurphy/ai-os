# Multi-line claude-control banner (2026-10-22)

## 18:50 Banner text wraps; Stop recoloured

What Matt asked (via coordinator): banner title wraps to as many lines as needed, banner grows; keep click/Esc/Stop/snooze and the HUD slot map; fix the terracotta-looking Stop.

---

### Title wraps, banner grows

- `~/.hammerspoon/modules/claude_control.lua`: light pill title and full-banner reason use `wordWrap` instead of `truncateTail`.
- `fitText()` counts lines with a greedy word wrap measured by `hs.drawing.getTextDrawingSize` (6px narrower than the box, so AppKit never needs more lines than counted; very long words break by character). The wrapping element grows; elements below it move down; the canvas grows.
- Light pill keeps its top edge (top-right slot); full banner stays centred.
- Recomputed on every render, so the countdown digits can't break it.
- Rejected: `canvas:minimumTextSize` (single-line size only).
- Tested: 4-line pill (108px tall) and 3-line full banner both rendered fully; screenshots checked. `hud_layout_test.lua` passes (slot map unchanged).

---

### Pill can overlap notify toasts

- A tall pill extends past its 62px slot and can cover the top of the claude_notify toasts (slot starts at dy 84) while both are up. Slots never move at runtime per the HUD rule, so I left it. Untested together.

---

### Stop no longer terracotta

- Was `#B3401E` (clay red-brown, terracotta family). The palette isn't picked yet and the rule says add no new colours, so Stop now reuses the banner's own orange `#FF7A1A` (glow/rim) with the banner's dark text `#3B2A12` (contrast ~7:1; white on that orange would be ~2.6:1).
- Banner is still light-only (no dark-mode variant); not in scope.

---

### Try it and undo

- Link: `hammerspoon://claude-control-demo?tier=light&text=...` (new `text` param).
- claude_notify toasts are a separate module and still truncate; not touched.
- Undo: revert commit f52142c in ~/.hammerspoon.
