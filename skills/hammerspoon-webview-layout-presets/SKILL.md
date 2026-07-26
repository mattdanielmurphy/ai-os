---
name: hammerspoon-webview-layout-presets
description: Use when building Hammerspoon layout preset managers, drawer-based editors, keyboard UIs, and WKWebview IPC patterns for qwerty-midi-hammerspoon or similar projects.
---

# Hammerspoon Webview Layout Presets & IPC Architecture

Patterns and guidelines for building layout preset managers, slide-out drawers, key-selection UIs, view reflow, and UI editors in Hammerspoon/Lua projects with HTML/JS webview HUDs (e.g. `qwerty-midi-hammerspoon`).

## 1. Dual Persistence Model for Layouts & Presets
- Store presets as a dictionary/map in user settings (`hs.settings.set("qwertyMidi_layoutPresets", presetsMap)`).
- Maintain an active preset ID (`qwertyMidi_activePresetId`).
- Always supply a default built-in preset (`id: "default"`, `isBuiltin: true`) that cannot be deleted.
- Mirror active preset layout data to `hs.settings.get("qwertyMidi_customKeyLayout")` for backwards compatibility.

```lua
local function getPresetsList()
  local map = getPresetsMap()
  local list = {}
  for id, p in pairs(map) do
    table.insert(list, {
      id = p.id or id,
      name = p.name or "Untitled Preset",
      isBuiltin = (p.isBuiltin == true or id == "default"),
      data = p.data or {}
    })
  end
  table.sort(list, function(a, b)
    if a.isBuiltin ~= b.isBuiltin then return a.isBuiltin end
    return a.name < b.name
  end)
  return list
end
```

## 2. IPC Message Protocol
Establish standard bidirectional IPC handlers between Lua and Webview:
- `getLayoutConfig`: Returns active layout, preset list (`presets`), and `activePresetId`.
- `selectPreset`: Switches active preset ID, applies layout data, and broadcasts refreshed state to webview (`onLayoutConfigLoaded`).
- `savePreset` / `saveCustomLayout`: Updates layout data for active preset or creates a new named preset.
- `renamePreset`: Updates preset display name.
- `duplicatePreset`: Deep-copies layout data into a new preset entry and selects it.
- `deletePreset`: Removes user preset (if `isBuiltin` is false).
- `updateKeyMapping`: Applies a per-key action/note binding change and triggers HUD re-render.
- `resetLayout`: Clears active preset's custom data and reverts to factory defaults.

### Text Input Focus IPC (textInputFocus)
WKWebView input fields (search inputs, modal prompts) need keystroke passthrough from the Lua event tap. Without this, the global key tap intercepts typing.

**HTML/JS side:** Post focus/blur events to the Lua host:
```js
function postTextInputFocus(focused) {
  if (window.webkit && window.webkit.messageHandlers &&
      window.webkit.messageHandlers.midiControllerUC) {
    window.webkit.messageHandlers.midiControllerUC.postMessage({
      type: 'textInputFocus', focused: focused
    });
  }
}
```
Wire on each `<input>` element:
```js
el.addEventListener('focus', () => postTextInputFocus(true));
el.addEventListener('blur', () => postTextInputFocus(false));
```

**Lua side (hud.lua):** Register the IPC handler:
```lua
elseif body.type == "textInputFocus" then
  state.textInputActive = (body.focused == true)
end
```

**Lua side (init.lua):** Check before intercepting in the event tap:
```lua
if state.textInputActive then
  return false  -- let keystrokes reach the input field natively
end
```

## 3. Webview UI Patterns

### Preset Toolbar
- Group dropdown selector, Save As (`+ Save`), Rename (`✏️`), Duplicate (`📋`), and Delete (`🗑️`) controls inside drawer panel.
- **Built-in Protection**: Disable Rename and Delete controls whenever an un-editable/default preset is active.
- **Unsaved Changes Badge**: Display a visual badge (`• Modified`) whenever local working layout snapshot differs from persisted state.
- **In-Webview Modal Prompts**: Use dark-themed overlay cards with auto-focused inputs for naming/renaming/duplicating presets instead of native OS dialogs.
- **Save Guard**: Automatically redirect "Save" clicks on built-in presets to "Save As" modal prompt to prevent clobbering factory defaults.
- **Ultra-Compact Layout**: Use reduced padding (3px/4px), smaller font sizes (8-9px), and tighter gaps (2-3px) for the preset bar inside a 270px drawer panel. Every pixel counts.

### Drawer / Keyboard View Reflow
When a slide-out drawer opens, the keyboard grid must shrink to avoid hidden overlap:

**CSS approach:**
```css
#hud-container.edit-mode-active #performance-view,
#hud-container.edit-mode-active .keyboard-grid {
  max-width: calc(980px - 272px);  /* container minus drawer width + border */
  transition: max-width 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
```
Shrink key-pad dimensions proportionally:
```css
#hud-container.edit-mode-active .key-pad {
  width: 48px;   /* down from 58px */
  height: 38px;  /* down from 44px */
}
#hud-container.edit-mode-active .key-pad .key-code { font-size: 10px; }
#hud-container.edit-mode-active .key-pad .key-note { font-size: 8px; }
```

### Key Selection & Multi-Select (Edit Mode)
Implement click-to-select, shift-click range select, cmd/ctrl-click toggle, and marquee drag-to-select:

**State:** `let selectedKeys = new Set()`

**Click handlers on key pads (edit mode):**
```js
pad.addEventListener('mousedown', (e) => {
  if (!isEditMode) { /* regular key-down */ return; }
  if (e.shiftKey && e.button === 0) {
    selectKeysInRange(lastSelected, k.code);
  } else if (e.button === 0) {
    selectKey(k.code, e.metaKey || e.ctrlKey);  // toggle with modifier
  }
});
```

**Marquee box selection:** Track mousedown on empty area, compute overlap in mousemove:
```js
allKeys.forEach(k => {
  const el = document.getElementById('key-' + k.code);
  const r = el.getBoundingClientRect();
  if (r.left < left + w && r.right > left && r.top < top + h && r.bottom > top) {
    selectedKeys.add(k.code);
    el.classList.add('selected-key');
  }
});
```
In mouseup: `isMarqueeSelecting = false` and reset selection-box dimensions.

**CSS for selected state:**
```css
.key-pad.selected-key {
  outline: 2.5px solid #5ea2eb !important;
  border-color: #5ea2eb !important;
  box-shadow: 0 0 12px rgba(94, 162, 235, 0.6) !important;
  z-index: 100;
}
```
Also render a visible `#selection-marquee` div (absolute positioned, blue border/transparent fill) during the drag.

### Delete / Backspace Revert
When edit mode is active and `selectedKeys.size > 0`, intercept Delete/Backspace:
```js
window.addEventListener('keydown', (e) => {
  if (!isEditMode) return;
  if (e.key === 'Delete' || e.key === 'Backspace') {
    if (selectedKeys.size > 0 && !e.target.closest('input, textarea')) {
      revertSelectedKeysToNotes();
    }
  }
});
```
The revert sends `{ action: 'none' }` via `updateKeyMapping` IPC for each selected key, clears the entry from `currentWorkingLayout`, resets the pad CSS class, and records an undo snapshot.

### Right-Click Context Menu
Show a floating menu at cursor position for selected keys:
```js
function showContextMenu(e) {
  menu.style.left = mx + 'px';
  menu.style.top = my + 'px';
  menu.style.display = 'block';
}
```
Menu items: "Revert to Note (Clear Action)", separator, "Deselect All". Use `data-action` attributes on `.ctx-item` elements and a container click handler to dispatch.

### Key Grid Layout Data
Define an ordered key layout array in JS (`LAYOUT_DATA`) with per-key objects:
```js
{ code: 12, keyLabel: "Q" }                        // note key
{ code: 48, keyLabel: "Tab", isControl: true, width: 85 }  // wide control key
{ code: 57, keyLabel: "Caps", isDummy: true, width: 95 }   // spacing placeholder
```
`initGrid()` generates all `.key-pad` divs from this data, attaching event handlers for mousedown/mouseup/mouseleave, dragstart/dragend/dragover/dragleave/drop, plus keyboard click simulation via IPC.

## 4. Edit Mode Lifecycle

**Entry** (`setEditMode(true)`):
1. Add `edit-mode-active` class to `#hud-container` (triggers CSS reflow + key-pad size)
2. Set all non-dummy pads to `draggable="true"`
3. Show drawer panel (`transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)`)
4. Request layout config via `getLayoutConfig` IPC
5. Render action catalog categories in drawer

**Exit** (`setEditMode(false)`):
1. Remove `edit-mode-active` class → keyboard grid expands back to full width
2. Set all pads to `draggable="false"`
3. Reset shift mode if active
4. Hide drawer panel
5. Clear drag-over-target / dragging-source visual states

## 5. Background Reload Focus Guard
Never auto-show webview windows (`wv:show()`) or start global key taps (`_G.toggleMidiMode(true)`) automatically on module import (`init.lua`). Auto-showing windows on reload steals focus from the user while background agents work.

## 6. HMR / Bundling Sync
Keep `src/web/index.html` in sync with offline `ui_html.lua` using `bin/bundle_and_reload.sh` (`hs-bundler`).

## Related Context & References
- [`references/thread-bloat-and-rule-sync.md`](file:///Users/matt/.hermes/skills/software-development/hammerspoon-webview-layout-presets/references/thread-bloat-and-rule-sync.md): Details the economic thread bloat reset formula and multi-engine rule synchronization.