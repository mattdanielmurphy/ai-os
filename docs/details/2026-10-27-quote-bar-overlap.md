# Quote queue bar covering typed text (2026-10-27)

## 12:32 Bar moved above the message box

Matt: the comment queuer (the "❝ N queued · Queue ⏎ · Send all" bar from the ⌥R quote tool) was drawn on top of the text he was typing in Claude's message box.

---

### Why it overlapped

The bar in `~/.hammerspoon/modules/quote_comment.lua` was placed a fixed 130 px up from the bottom of Claude's window. An empty message box's top sits about 141 px up, so the bar just cleared it; as soon as the box grew taller with typed or dictated text (it grows upward), the box slid under the bar.

---

### The bar now rides above the box

The bar now reads the message box's position through Accessibility and sits 8 px above its top edge, right-aligned with it. While the bar shows, a light timer (every 0.25 s) re-reads the box and moves the bar as the box grows or shrinks; the timer stops when the bar hides. It never goes above the window's title area. If the box can't be found, it falls back to the old fixed spot.

Rejected: putting the bar beside the box (no room in a narrow pane) and hooking AX value-changed notifications (Claude re-creates the box element often, so a poll is more reliable and cheap).

---

### Knobs

Tweaks panel (⌃⌥⌘T) → "Quote comments (⌥R)": `bar.lift` (gap above the box), `bar.inset` (in from the box's right edge), `bar.follow` (check interval). `bar.right` / `bar.bottom` are now only the fallback.

---

### Tested and untested

Tested: the computed spot with Claude's real box (bar ends 8 px above the box top, flush with its right edge), render, reload. Not tested live: watching it follow a growing box, since that needs typing in Matt's box.

Undo: `git -C ~/.hammerspoon revert HEAD`.
