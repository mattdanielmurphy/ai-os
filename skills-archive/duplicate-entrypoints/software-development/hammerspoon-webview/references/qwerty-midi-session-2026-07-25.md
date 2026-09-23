# qwerty-midi-hammerspoon Bug Fix Session

## Date: 2026-07-25

## Project: qwerty-midi-hammerspoon

Location: `/Users/matt/projects/qwerty-midi-hammerspoon`

## 5 Bugs Fixed

### Bug 1: Search input click/focus doesn't work
**Root Cause**: `* { user-select: none; }` in CSS prevents WebKit webview inputs from gaining focus on click.
**Fix**: Added `input, textarea, [contenteditable] { user-select: auto; }`.

### Bug 2: Dialog modal (preset name) typing doesn't work
**Root Cause**: Same CSS issue as Bug 1. Also, `input.focus()` called synchronously after removing `display: none` may fail.
**Fix**: Same CSS fix + wrapped focus/select in `requestAnimationFrame`.

### Bug 3: Preset "Save Layout" doesn't add to dropdown / switch
**Root Cause**: Not a code logic bug — the IPC flow was correct. The root cause was the input fields not working (Bug 1/2), preventing the user from typing a preset name and hitting Save.
**Fix**: CSS + requestAnimationFrame fixes enabled the Save flow to work correctly.

### Bug 4: Shift mode button doesn't display shift layout
**Root Cause**: `updateAllKeyLabels()` set `noteEl.textContent = ''` when shift mode was active but no shift action was assigned to a key, clearing labels for keys that just had normal actions.
**Fix**: Chain fallbacks: `binding.shiftName || binding.shiftAction || binding.name || ''`. Also added `getLayoutConfig()` call after toggling to refresh labels from Lua.

### Bug 5: Right-click context menu items don't respond / Delete key doesn't revert selected keys
**Root Cause**: Two independent issues:
1. **Context menu**: `#key-context-menu` is a sibling of `#hud-container`, so `container.addEventListener('click', ...)` never fires for menu item clicks.
2. **Delete key**: Hammerspoon eventtap intercepts Delete/Backspace before webview JS can handle them.
**Fix**: `container.addEventListener('click')` → `document.addEventListener('click')`. Added explicit pass-through for keycodes 51/117 in the eventtap.

## Architecture Notes

- **Source of truth** for HTML/JS/CSS: `src/web/index.html`
- Bundler copies it into `src/ui_html.lua` on every bundle run
- Lua modules are in `src/` — bundled into `qwerty_midi.lua`
- `bin/bundle_and_reload.sh` runs the bundler and triggers `hs.reload()`
- The webview uses `hs.webview.usercontent` for JS→Lua IPC (`webkit.messageHandlers.midiControllerUC.postMessage()`)
- Lua→JS is via `wv:evaluateJavaScript()`

## Key Files

- `src/init.lua` — eventtap + MIDI mode toggle
- `src/hud.lua` — webview creation + IPC callback handler
- `src/controls.lua` — keyboard event handling + MIDI note/control dispatch
- `src/config.lua` — state, key mappings, presets
- `src/web/index.html` — HTML/JS/CSS for the HUD webview