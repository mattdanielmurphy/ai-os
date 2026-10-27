# Shared UI library (Slub UI)

## 08:45 Kit built, three looks to pick from

What Matt asked: a new shared UI library all his apps use, built on a strong foundation, with good sliders, inputs and a jump menu for the Tweaks panel. Then (08:15): don't worry about colour; it should look good with any colour, using saturation/brightness/opacity modifiers.

---

### Foundation: Web Awesome

Web Awesome 3.14 (MIT, the successor to Shoelace) is free, accessible web components themed entirely by CSS tokens. It works in plain HTML, in the Hammerspoon webview (no React needed), and in React (it ships wrappers). Rejected: Mantine, because it is React-only, and the Tweaks panel, Knobs, UI Mixer and pages are all plain JS, so Mantine would force a React rewrite of each. Swift apps keep hud-kit.

The kit lives in `~/projects/ui-mixer/kit/` next to Knobs, not in a new repo, because of the project freeze. `bun kit/build.ts` makes one offline bundle (`dist/slub-ui.js`, 368 KB) plus one CSS file per look.

---

### Jump menu

`<slub-jump>` is a small composite on Web Awesome's popup and input: a button showing the current app, ⌘J to open, type to filter, grouped list (Apps / Background utilities), arrow keys, Enter, Esc or a click outside to close. Its keys are printed in its footer (discoverable rule).

---

### Any colour works

`kit/seed.css` derives every shade from `--slub-accent`, using OKLCH relative colours. Lightness per step is fixed to Web Awesome's own scale, so text contrast stays the same whatever the colour. `--slub-vivid` scales saturation, and `--slub-tint` sets how much the accent tints the greys. The trade-off is that the seed's own brightness is ignored: a bright yellow comes out olive, because yellow text on white can't be read. Tested with teal, yellow, magenta and near-black, light and dark.

---

### Three looks, made separately

Per the options-first rule, three separate agents each made one look from their own brief: **hairline** (lab instrument: hairlines, tick thumb, mono digits), **prairie** (soft: rounded type, pill fields, big round thumbs) and **synth** (hardware faceplate: condensed caps, fader caps, LED switch). Plain is Web Awesome untouched, for reference.

---

### Knobs uses it automatically

When the kit is loaded, Knobs rows use the kit's slider, number field, switch, colour picker, chips and search. Without the kit they fall back to plain inputs. The UI Mixer check still passes.

---

### Untested

- Nothing has been checked in the real Hammerspoon webview yet. The screenshots come from Chrome. The Tweaks thread will see it there first.
- The Tweaks panel itself is unchanged until that thread adopts the kit.

Undo: `git revert` the two Slub UI commits in ui-mixer.

## 17:52 Plain is the default look

Matt: it's between plain and hairline; plain is good enough for now, and it can change later.

---

### Plain is now the default

`build.ts` writes `dist/slub-ui.css` from `DEFAULT_LOOK = 'plain'`. Hosts load that one file, so switching later (for example to hairline) is a one-word change and a rebuild. All looks stay in `looks/`. The Tweaks thread was told to use `slub-ui.css`.

## 17:58 Steppers on number-only fields

Matt: with plain, the Offset field should have increment and decrement buttons.

---

### Steppers when there's no slider

Knobs now shows Web Awesome's − / + steppers on a number field when the knob has no slider (no min and max). Knobs that have a slider keep a compact field without steppers, because the slider already does that job. The field is 150 px wide so the value isn't clipped. The look picker page is updated.
