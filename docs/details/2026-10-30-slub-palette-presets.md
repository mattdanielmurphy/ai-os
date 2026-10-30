# Slub palette presets

## 13:30 Three palettes as switchable presets

Matt asked to keep all three palettes as presets he can switch between, starting on Apothecary glass with absinthe as the accent. That is done, and the Tweaks panel has a new "Slub palette" entry with a chip for each palette and an accent choice for each one.

---

### Accent picks

Absinthe is an exact hue on the board. Prairie light starts on aurora and Synth panel on VFD teal; those two are my picks and can be changed in the panel.

---

### What follows the palette

Only web UI built on the Slub UI kit follows it: the Tweaks panel, plus any page using the kit, which gets the default at build time. Hammerspoon HUDs and Swift apps still use their own colours.

---

### How absinthe looks

The kit derives readable shades from the accent, so buttons and sliders show a deep olive rather than the bright bottle green. Text on them stays legible in light and dark.

---

### Not tested

Switching was tested by changing the setting and confirming the new colours came out for all three palettes. Light and dark were checked on the kit gallery. The open panel repainting itself was not watched, because that needs a window on Matt's screen.

---

### Proposed rule wording

"Colours come from the Slub palette presets, by role; the default is Apothecary glass with absinthe. Add no colours outside the presets' palettes." This replaces "until the palette is picked". Sent to the rule-process thread rather than edited.

---

### Undo

Choose another preset in the panel, or revert the two commits in ui-mixer and .hammerspoon.
