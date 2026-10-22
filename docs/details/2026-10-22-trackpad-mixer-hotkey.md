# Trackpad mixer hotkey (2026-10-22)

## 12:20 Hotkey summons the mixer on the built-in trackpad

Asked: a hotkey that summons the mixer one-shot on the MacBook's built-in trackpad; when the mixer dismisses, the pad returns to normal.

---

### Hotkey choice

⌃⌥⌘V ("volume"). Checked every live Hammerspoon binding (⌃⌥⌘ M, L, R taken) and Keyboard Maestro's macros (⌃⌥⌘ A, T, M, I taken). V is free in both. Raycast/Alfred hotkeys weren't checked (not easily readable); if ⌃⌥⌘V does something else, that's why.

---

### How it works

- Hammerspoon `modules/trackpad_mixer_summon.lua` binds ⌃⌥⌘V and posts the distributed notification `ca.mattmurphy.trackpad-mixer.summon`.
- The mixer sets `Pads.builtInSummoned`, so built-in pad frames count as mixer frames (cursor blocked while touching, like the old pad), and shows the full HUD. Strip touches act live right away (no preview ring, since the HUD is already up).
- When the HUD hides (4s idle, Esc, click outside) or collapses to the fades strip, `HUD.onDismiss` ends it; a finger still down is released so the cursor never stays blocked.
- Pressing ⌃⌥⌘V again while it's up closes it.
- Works with the old Magic Trackpad unplugged (it was unplugged during the test): the built-in pad is registered on demand.

---

### Tested / untested

Tested: build, safe restart, summon + close via the notification (log shows both). Not tested: actual finger use on the built-in pad, and the real keypress (agents can't touch the pad). Pinning the HUD keeps the pad as the mixer until you close it.

---

### Undo

Revert the commits in trackpad-mixer ("Hotkey summons the mixer…") and ~/.hammerspoon ("Add ⌃⌥⌘V…"), rebuild, `scripts/restart-mixer`.
