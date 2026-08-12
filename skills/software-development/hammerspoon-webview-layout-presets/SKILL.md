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

> **CRITICAL PITFALL — Webview IPC Handler Completeness**: Every message type posted via `postMessage` from JS (such as `savePreset`, `selectPreset`, `renamePreset`, `duplicatePreset`, `deletePreset`) MUST have an explicit matching handler branch in `src/hud.lua`. If JS sends an IPC message type that Lua ignores, UI buttons will appear completely broken/non-responsive despite sending valid webview messages. Always broadcast `onLayoutConfigLoaded` back to JS after preset state mutations so the UI updates instantly.

### Text Input Focus & Selection Pitfalls in WKWebView
WKWebView elements and Hammerspoon global event taps have two major failure modes that disable search/modal inputs:

1. **CSS User Selection Blocking Input Focus**: A global CSS reset like `* { user-select: none; -webkit-user-select: none; }` prevents `<input>` fields and `<textarea>` elements from gaining text selection/caret focus in WKWebView.
   - **Fix**: ALWAYS include an explicit input override in CSS:
     ```css
     input, textarea, [contenteditable] {
       user-select: auto !important;
       -webkit-user-select: auto !important;
     }
     ```

2. **Event Tap Keystroke Trapping**: WKWebView input fields (search inputs, modal prompts) need keystroke passthrough from the Lua event tap. Without this, the global key tap intercepts typing.

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

### Context Menu & Modal Overlay Event Capture
- **Document-Level Dispatching**: Context menu actions and modal overlay dismissals should attach event listeners to `document` rather than parent container divs. Container mousedown handlers used for window dragging can suppress event propagation if attached to parent elements.
- **Async Focus**: Wrap `.focus()` on modal inputs in `requestAnimationFrame()` when opening modals so WebKit renders the DOM element before attempting focus.

### Shift Mode Label Display
When toggling Shift Mode in the layout editor, `renderHud()` (running on a fast tick from Lua) will overwrite key labels with unshifted note data unless JS explicitly checks `shiftModeActive` and resolves `shiftName || shiftAction || name` when rendering labels. Always trigger a `getLayoutConfig` message when shift mode is toggled to force Lua to re-render all non-customized key labels.

## 3. Webview UI Patterns

### Viewport Padding, Transform Origin & Window Framing Pitfalls
In webviews where CSS transforms (`transform: scale(...)`) are applied to flexbox children (e.g., `#hud-container` inside `body`), `transform-origin` and container alignment interact heavily with the native window dimensions:

1. **Transform Origin Overflow (`transform-origin: center center`)**:
   When an element aligned at the bottom of a container (`justify-content: flex-end`) uses `transform-origin: center center`, scaling by $S$ (e.g., $1.4\times$) causes the visual bounds to expand downward past the bottom of its DOM box by $\frac{\text{height} \times (S - 1)}{2}$ (e.g., $330\text{px} \times 0.2 = 66\text{px}$).
   - **Symptom**: The bottom border and box-shadow get clipped/cut off by the webview viewport bottom edge.
   - **Wrong Fix**: Adding large `padding-bottom` (e.g., `4.2rem` / ~66px) on `body` lifts the DOM box to pull the visual bottom back into view, but creates an awkwardly large empty gap below the content inside the webview frame.
   - **Correct Fix**: Set `transform-origin: bottom center` (or `center bottom`) on the scaled child. The scale then anchors to the bottom edge and expands upward, preventing downward overflow entirely while requiring only a small, snug `padding-bottom` (e.g., `6px`–`8px` or `0.5rem`) on `body` for clean border/shadow rendering.

2. **Webview Frame Size Calculation Discrepancy**:
   Ensure native window height calculations in Lua are consistent across initial window creation (`createMidiWebview`) and live update passes (`performWebviewHudUpdate`). If live updates compute height as `baseH * scale` without including top/bottom band offsets (like `#notification-zone`'s `NOTIF_BAND`), the webview window frame will unexpectedly shrink during updates, clipping the scaled webview content.

3. **Excess Fixed Height & Dead Space Below Layout**:
   When a webview container has a hardcoded CSS height (e.g. `height: 330px`) and matching Lua window dimensions (`baseH = 330`), but the inner DOM components (header + keyboard grid) only sum to a smaller vertical footprint (`280px`), the unused space manifests as dead empty space between the content and the bottom border.
   - **Symptom**: Unexplained large vertical gap between the bottom row of keys and the bottom border of the HUD container.
   - **Fix**: Sum the exact vertical layout budget (e.g. 12px top padding + 48px header + 12px margin + 194px 4-row grid + 14px bottom padding = 280px), and synchronize CSS `#hud-container { height: 280px; }` with the Lua webview dimensions `baseH = 280` in both window creation and resize methods.

```css
html, body {
  background: transparent;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  border-radius: 14px;
  padding-bottom: 6px;
}

#hud-container {
  width: 980px;
  height: 330px;
  transform-origin: bottom center; /* Anchors bottom edge; prevents downward scale overflow */
  transform: scale(1.4);
}
```

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

## 7. Arpeggiator Row Routing (Config Defaults)

qwerty-midi-hammerspoon has independent arpeggiator enable flags for top row (QWERTYUIOP[]) and bottom row (ZXCVBNM,./'):

- `arpTopEnabled` — controls whether top-row notes are arpeggiated with gate length
- `arpBottomEnabled` — controls whether bottom-row notes are arpeggiated with gate length

**Default state**: Both default to `true` so both rows consistently receive gate-length control. If one defaults to `true` and the other to `false`, top-row notes bypass the arpeggiator entirely and play as direct MIDI noteOn.

**Routing logic** (in `controls.lua handleKeyDown()`):
```lua
local arpEnabledForRow = isTop and state.arpTopEnabled or (not isTop and state.arpBottomEnabled)
if isArpNote then
  arpeggiator.arpAddNote(code, transposedPitch)
else
  midi.sendMidiNote("noteOn", transposedPitch, transposer.getEffectiveRowVelocity(isTop))
end
```

**Critical**: When changing a row arp default, you MUST update BOTH:
1. The initial default in `config.lua`
2. The factory reset path (resetAll) in `controls.lua` — these are often in different files and can diverge

**User controls**: Backtick toggle arp engine, `1` toggles top row arp, `2` toggles bottom row arp, `7`/`8` adjust gate percent (5–150%).

## Related Context & References
- [`references/thread-bloat-and-rule-sync.md`](file:///Users/matt/.hermes/skills/software-development/hammerspoon-webview-layout-presets/references/thread-bloat-and-rule-sync.md): Details the economic thread bloat reset formula and multi-engine rule synchronization.
- [`references/qwerty-midi-arp-gate-consistency.md`](file:///Users/matt/.hermes/skills/software-development/hammerspoon-webview-layout-presets/references/qwerty-midi-arp-gate-consistency.md): Arpeggiator gate-length fix session — how top/bottom row arp routing works, why `arpTopEnabled` default was `false`, and the lesson about fixing both the initial default AND the reset-to-defaults code path.