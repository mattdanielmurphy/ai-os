---
title: "Debugging Qwerty-Midi Key Event Leaks"
date: "2026-08-01"
conversation_id: "976fe245-7449-4c4c-8f0c-7ef6b7531a7b"
source: "antigravity"
---

# Debugging Qwerty-Midi Key Event Leaks

## User

Let's check and modify `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`.

Wait, let's carefully trace:
When key down event happens in `src/controls.lua`:
`handleKeyDown(code)`:
```lua
local function handleKeyDown(code)
  if state.pressedKeys[code] then return true end
  ...
```
If key is already in `state.pressedKeys[code]`, it returns `true` (which swallows autorepeat).

Wait! What about the VERY FIRST key press (when `state.pressedKeys[code]` is nil)?
Let's trace:
1. `handleKeyDown(code)` runs for KeyPress 1 (KeyDown).
2. Is key mapped?
Suppose `code` is 12 (`Q`, a note key).
`noteKey` is found (`Q`, baseNote=72).
`state.pressedKeys[code] = { pitch = ..., ... }`.
`hud.updateWebviewHud()` is called.
`handleKeyDown` returns `true`!

Wait! `handleKeyDown` returned `true`.
What happens in `init.lua`?
`init.lua` line 221:
```lua
if isDown then
  local ok, status = xpcall(function() return controls.handleKeyDown(code) end, ...)
  if not ok then ... return false end
  return status
```
`status` is `true`. So `midiKeyTap` callback in `init.lua` returns `true`.
In macOS eventtap, returning `true` SWALLOWS the event (does NOT pass to app behind).

Now, what happens next?
User holds key down or releases key!
When user releases key: KeyUp event arrives!
In `init.lua`: `isDown` is `false`.
Calls `controls.handleKeyUp(code)`.
In `src/controls.lua`: `handleKeyUp(code)`:
Line 960: `local noteKey = config.getNoteKey(code)` -> `noteKey` is found (`Q`).
Line 962: `local keyInfo = state.pressedKeys[code]` -> `keyInfo` is found (`{ pitch = ... }`).
`state.pressedKeys[code] = nil` -> `state.pressedKeys[code]` is set to `nil`!
`hud.updateWebviewHud()` is called.
`handleKeyUp` returns `true`!
In `init.lua`: `status` is `true`. `midiKeyTap` callback returns `true`.
So KeyUp is swallowed!

Now, user presses `Q` AGAIN (KeyPress 2, KeyDown):
`state.pressedKeys[code]` is `nil`.
`handleKeyDown(code)` runs:
`local noteKey = config.getNoteKey(code)` -> `noteKey` is found (`Q`).
`state.pressedKeys[code] = { pitch = ..., ... }`.
Returns `true`!

Wait! Why did the user say: "every second press of each key leaks out of the controller and into the app behind it; fix that"?

WHY WOULD EVERY SECOND PRESS LEAK?!

Wait! Let's check `_G.activeWatchers.midiKeyTap` or webview IPC or eventtap state or `state.pressedKeys`!
Wait! Is there somewhere else where `state.pressedKeys[code]` or `state.midiActive` or eventtap is affected?
Wait! Let's search the ENTIRE repository for `pressedKeys` or `handleKeyDown` or `postMessage` or `midiKeyTap` or `eventtap`!

Subagent, use `grep_search` to search for `pressedKeys` in `/Users/matt/projects/qwerty-midi-hammerspoon/src` and `/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua`. Also search for `handleKeyDown` or `postMessage` across all files!
Report all findings back.

---

## Assistant

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:13-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua","LineNumber":101,"LineContent":"  pressedKeys = {},"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":524,"LineContent":"    state.pressedKeys = {}"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":598,"LineContent":"    for code, keyInfo in pairs(state.pressedKeys) do"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":880,"LineContent":"  if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":887,"LineContent":"      state.pressedKeys[code] = { isControl = true, action = k.shiftAction }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":895,"LineContent":"          if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":912,"LineContent":"    state.pressedKeys[code] = { isControl = true, action = k.action }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":920,"LineContent":"        if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":944,"LineContent":"    state.pressedKeys[code] = { pitch = transposedPitch, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":957,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":964,"LineContent":"    local keyInfo = state.pressedKeys[code]"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":981,"LineContent":"      state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":990,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":998,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1020,"LineContent":"            for _, keyInfo in pairs(state.pressedKeys) do"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1049,"LineContent":"  if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1050,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua","LineNumber":141,"LineContent":"      pressed = (state.pressedKeys[code] ~= nil),"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua","LineNumber":160,"LineContent":"    local isPressed = (state.pressedKeys[code] ~= nil)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua","LineNumber":191,"LineContent":"      pressed = (state.pressedKeys[code] ~= nil),"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":52,"LineContent":"    state.pressedKeys = {}"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":143,"LineContent":"      if state and state.pressedKeys then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":145,"LineContent":"        if code then state.pressedKeys[code] = nil end"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":290,"LineContent":"      state.pressedKeys = {}"}

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:13-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":158,"LineContent":"      pressed = (state.pressedKeys[code] ~= nil),"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":177,"LineContent":"    local isPressed = (state.pressedKeys[code] ~= nil)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":208,"LineContent":"      pressed = (state.pressedKeys[code] ~= nil),"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":729,"LineContent":"    state.pressedKeys = {}"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":820,"LineContent":"      if state and state.pressedKeys then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":822,"LineContent":"        if code then state.pressedKeys[code] = nil end"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":967,"LineContent":"      state.pressedKeys = {}"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":6045,"LineContent":"  pressedKeys = {},"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7149,"LineContent":"    state.pressedKeys = {}"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7223,"LineContent":"    for code, keyInfo in pairs(state.pressedKeys) do"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7505,"LineContent":"  if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7512,"LineContent":"      state.pressedKeys[code] = { isControl = true, action = k.shiftAction }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7520,"LineContent":"          if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7537,"LineContent":"    state.pressedKeys[code] = { isControl = true, action = k.action }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7545,"LineContent":"        if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7569,"LineContent":"    state.pressedKeys[code] = { pitch = transposedPitch, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7582,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7589,"LineContent":"    local keyInfo = state.pressedKeys[code]"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7606,"LineContent":"      state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7615,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7623,"LineContent":"    state.pressedKeys[code] = nil"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7645,"LineContent":"            for _, keyInfo in pairs(state.pressedKeys) do"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7674,"LineContent":"  if state.pressedKeys[code] then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7675,"LineContent":"    state.pressedKeys[code] = nil"}

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:13-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":879,"LineContent":"local function handleKeyDown(code)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1058,"LineContent":"  handleKeyDown = handleKeyDown,"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua","LineNumber":312,"LineContent":"      if controlsModule then controlsModule.handleKeyDown(body.code) end"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":221,"LineContent":"        local ok, status = xpcall(function() return controls.handleKeyDown(code) end, function(err) print('QWERTY MIDI: handleKeyDown error: '..tostring(err)); print(debug.traceback()); return false end)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":223,"LineContent":"          print(\"QWERTY MIDI: handleKeyDown error: \" .. tostring(status))"}

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:13-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":329,"LineContent":"      if controlsModule then controlsModule.handleKeyDown(body.code) end"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":898,"LineContent":"        local ok, status = xpcall(function() return controls.handleKeyDown(code) end, function(err) print('QWERTY MIDI: handleKeyDown error: '..tostring(err)); print(debug.traceback()); return false end)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":900,"LineContent":"          print(\"QWERTY MIDI: handleKeyDown error: \" .. tostring(status))"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7504,"LineContent":"local function handleKeyDown(code)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":7683,"LineContent":"  handleKeyDown = handleKeyDown,"}

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:14-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua","LineNumber":357,"LineContent":"      window.webkit.messageHandlers.settingsUserContent.postMessage({ type: type, value: value });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":1724,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":1772,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'textInputFocus', focused: focused });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":1877,"LineContent":"              window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'keyDown', code: k.code });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":1885,"LineContent":"                window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'keyUp', code: k.code });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":2129,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'getLayoutConfig' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":2150,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'toggleEditMode', active: true });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":2174,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'toggleEditMode', active: false });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":2309,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":2410,"LineContent":"      window.webkit.messag
<truncated 3840 bytes>
.lua","LineNumber":3048,"LineContent":"            window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3097,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3154,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3173,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'resetLayout' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3179,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'getLayoutConfig' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3249,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3267,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3283,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3302,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'dragWindow', dx: dx, dy: dy2 });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3606,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'log', message: 'initGrid took ' + (t1 - t0) + ' ms' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua","LineNumber":3612,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'heartbeat' });"}

Created At: 2026-07-31T20:50:13-06:00
Completed At: 2026-07-31T20:50:14-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3516,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3564,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'textInputFocus', focused: focused });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3669,"LineContent":"              window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'keyDown', code: k.code });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3677,"LineContent":"                window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'keyUp', code: k.code });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3921,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'getLayoutConfig' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3942,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'toggleEditMode', active: true });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":3966,"LineContent":"        window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'toggleEditMode', active: false });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4101,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4202,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4258,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMess
<truncated 3837 bytes>
ineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4946,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4965,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'resetLayout' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":4971,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'getLayoutConfig' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5041,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5059,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5075,"LineContent":"          window.webkit.messageHandlers.midiControllerUC.postMessage({"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5094,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'dragWindow', dx: dx, dy: dy2 });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5398,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'log', message: 'initGrid took ' + (t1 - t0) + ' ms' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5404,"LineContent":"      window.webkit.messageHandlers.midiControllerUC.postMessage({ type: 'heartbeat' });"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua","LineNumber":5774,"LineContent":"      window.webkit.messageHandlers.settingsUserContent.postMessage({ type: type, value: value });"}

Created At: 2026-07-31T20:50:14-06:00
Completed At: 2026-07-31T20:50:14-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1062
Total Bytes: 36538
Showing lines 870 to 970
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
870:       targetId = "bpm-value",
871:       color = "#d4a359"
872:     }
873:     hud.updateWebviewHud(spot)
874:   end
875: 
876:   config.saveSettings()
877: end
878: 
879: local function handleKeyDown(code)
880:   if state.pressedKeys[code] then
881:     return true
882:   end
883: 
884:   if state.shiftHeld then
885:     local k = config.getNumberControlKey(code) or config.getControlKey(code)
886:     if k and k.shiftAction and k.shiftAction ~= "" and k.shiftAction ~= "none" then
887:       state.pressedKeys[code] = { isControl = true, action = k.shiftAction }
888:       executeControlAction(k.shiftAction, code)
889:       if k.shiftAction ~= "sustain" then
890:         stopControlRepeat(code)
891:         local entry = {}
892:         controlRepeatTimers[code] = entry
893:         entry.timer = hs.timer.doAfter(0.35, function()
894:           if not controlRepeatTimers[code] then return end
895:           if state.pressedKeys[code] then
896:             entry.interval = hs.timer.doEvery(0.08, function()
897:               if not controlRepeatTimers[code] then return end
898:               local savedFn = pushStateSnapshot
899:               pushStateSnapshot = function() end
900:               pcall(executeControlAction, k.shiftAction, code)
901:               pushStateSnapshot = savedFn
902:             end)
903:           end
904:         end)
905:       end
906:       return true
907:     end
908:   end
909: 
910:   local k = config.getNumberControlKey(code) or config.getControlKey(code)
911:   if k and k.action and k.action ~= "" and k.action ~= "
<truncated 797 bytes>
    end)
928:         end
929:       end)
930:     end
931:     return true
932:   end
933: 
934:   local noteKey = config.getNoteKey(code)
935:   if noteKey then
936:     local isTop = noteKey.isTop
937:     local transposedPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
938:     local arpEnabledForRow = isTop and state.arpTopEnabled or (not isTop and state.arpBottomEnabled)
939:     local arpActive = state.arpEnabled and arpEnabledForRow
940:     local sustainActive = state.sustainActive
941:     local isArpNote = state.shiftHeld and (not arpActive) or arpActive
942:     local isSustainedNote = state.shiftHeld and (not sustainActive) or sustainActive
943:     local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
944:     state.pressedKeys[code] = { pitch = transposedPitch, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }
945:     if isArpNote then arpeggiator.arpAddNote(code, transposedPitch)
946:     else midi.sendMidiNote("noteOn", transposedPitch, transposer.getEffectiveRowVelocity(isTop), ch)
947:     end
948:     hud.updateWebviewHud()
949:     return true
950:   end
951: 
952:   return false
953: end
954: 
955: local function handleKeyUp(code)
956:   if code == 50 then -- Backtick
957:     state.pressedKeys[code] = nil
958:     hud.updateWebviewHud()
959:     return true
960:   end
961: 
962:   local noteKey = config.getNoteKey(code)
963:   if noteKey then
964:     local keyInfo = state.pressedKeys[code]
965:     if keyInfo then
966:       local playedPitch = type(keyInfo) == "table" and keyInfo.pitch or keyInfo
967:       local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
968:       local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote
969: 
970:       local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:15-06:00
Completed At: 2026-07-31T20:50:15-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1062
Total Bytes: 36538
Showing lines 971 to 1050
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
971:       if isArpNote then
972:         arpeggiator.arpRemoveNote(code)
973:       else
974:         if isSustainedNote and state.sustainActive then
975:           state.sustainedPitches = state.sustainedPitches or {}
976:           state.sustainedPitches[playedPitch] = { channel = keyChannel }
977:         else
978:           midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
979:         end
980:       end
981:       state.pressedKeys[code] = nil
982:     end
983:     hud.updateWebviewHud()
984:     return true
985:   end
986: 
987:   local numCtrlKey = config.getNumberControlKey(code)
988:   if numCtrlKey then
989:     stopControlRepeat(code)
990:     state.pressedKeys[code] = nil
991:     hud.updateWebviewHud()
992:     return true
993:   end
994: 
995:   local ctrlKey = config.getControlKey(code)
996:   if ctrlKey then
997:     stopControlRepeat(code)
998:     state.pressedKeys[code] = nil
999:     local act = state.shiftHeld and ctrlKey.shiftAction or ctrlKey.action
1000:     if act == "sustain" then
1001:       local holdDuration = state.sustainKeyDownTime and (hs.timer.secondsSinceEpoch() - state.sustainKeyDownTime) or 0
1002:       if holdDuration > 0.25 then
1003:         state.sustainActive = false
1004:         midi.sendMidiCC(64, 0)
1005:       else
1006:         if state.sustainWasActiveOnPress then
1007:           state.sustainActive = false
1008:           midi.sendMidiCC(64, 0)
1009:         else
1010:           state.sustainActive = true
1011:           midi.sendMidiCC(64, 127)
1012:         end
1013:       end
1014: 
1015:       if not state.sustainActive then
1016:         midi.sendMidiCC(64, 0)
1017:         if state.sustainedPitches then
1018:           for pitch in pairs(state.sustainedPitches) do
1019:             local isCurrentlyHeld = false
1020:             for _, keyInfo in pairs(state.pressedKeys) do
1021:               if type(keyInfo) == "table" and keyInfo.pitch == pitch then
1022:                 isCurrentlyHeld = true
1023:                 break
1024:               end
1025:             end
1026:             if not isCurrentlyHeld then
1027:               midi.sendMidiNote("noteOff", pitch, 0)
1028:             end
1029:           end
1030:           state.sustainedPitches = {}
1031:         end
1032:       end
1033: 
1034:       local spot = {
1035:         title = "SUSTAIN (CC #64)",
1036:         value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
1037:         subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
1038:         targetId = "key-48",
1039:         color = state.sustainActive and "#d4a359" or "#b5aba0"
1040:       }
1041:       hud.updateWebviewHud(spot)
1042:     else
1043:       hud.updateWebviewHud()
1044:     end
1045:     return true
1046:   end
1047: 
1048:   -- Fallback cleanup for unmapped or ignored keys
1049:   if state.pressedKeys[code] then
1050:     state.pressedKeys[code] = nil
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:16-06:00
Completed At: 2026-07-31T20:50:16-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 358
Total Bytes: 12782
Showing lines 200 to 250
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
200:         return true
201:       end
202: 
203:       if flags.cmd or flags.alt or flags.ctrl or flags.capslock then
204:         return false
205:       end
206: 
207:       local isShiftNow = flags.shift
208:       if isShiftNow ~= state.shiftHeld then
209:         state.shiftHeld = isShiftNow
210:         hud.updateWebviewHud()
211:       end
212: 
213:       if event:getType() == hs.eventtap.event.types.flagsChanged then
214:         return false
215:       end
216: 
217:       local code = event:getProperty(hs.eventtap.event.properties.keyboardEventKeycode)
218:       local isDown = (event:getType() == hs.eventtap.event.types.keyDown)
219: 
220:       if isDown then
221:         local ok, status = xpcall(function() return controls.handleKeyDown(code) end, function(err) print('QWERTY MIDI: handleKeyDown error: '..tostring(err)); print(debug.traceback()); return false end)
222:         if not ok then
223:           print("QWERTY MIDI: handleKeyDown error: " .. tostring(status))
224:           return false
225:         end
226:         return status
227:       else
228:         local ok, status = xpcall(function() return controls.handleKeyUp(code) end, function(err) print('QWERTY MIDI: handleKeyUp error: '..tostring(err)); print(debug.traceback()); return false end)
229:         if not ok then
230:           print("QWERTY MIDI: handleKeyUp error: " .. tostring(status))
231:           return false
232:         end
233:         return status
234:       end
235: 
236:   end, errorHandler)
237: 
238:   if not ok then
239:     return false
240:   end
241:   return result
242: end)
243: 
244: -- Watchdog timer: if the key eventtap stops silently (e.g. uncaught pcall error), restart it
245: -- Also checks webview liveness via JS heartbeat — if no heartbeat for 6s, web process is dead
246: _G.activeWatchers.keyTapWatchdog = hs.timer.doEvery(3.0, function()
247:   if state.midiActive then
248:     if _G.activeWatchers.midiKeyTap and not _G.activeWatchers.midiKeyTap:isEnabled() then
249:       print("QWERTY MIDI: Watchdog detected dead keyTap, restarting...")
250:       _G.activeWatchers.midiKeyTap:start()
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:18-06:00
Completed At: 2026-07-31T20:50:18-06:00
Message sent to "41f79905-6dba-47e7-b964-324bdb5f4fb2".

I have completed the requested analysis.

I traced the `handleKeyDown` and `handleKeyUp` logic in `src/controls.lua` and confirmed that they correctly set/unset `state.pressedKeys[code]` and return `true` to swallow events in `init.lua`. The event handling flow appears logically sound for a standard key press/release cycle.

I suspect the reported "leak" on every second press might be related to:
1. **Error handling**: If `controls.handleKeyDown` or `controls.handleKeyUp` fails, `init.lua`'s `xpcall` returns `false`, which allows the event to leak.
2. **Event tap state**: Potential race conditions or missing events where `pressedKeys` gets out of sync with the actual keyboard state.

I have sent a summary of these findings to the parent agent, including questions about the observed behavior to help narrow down whether this is an error-related leak or a more subtle synchronization issue.

---
