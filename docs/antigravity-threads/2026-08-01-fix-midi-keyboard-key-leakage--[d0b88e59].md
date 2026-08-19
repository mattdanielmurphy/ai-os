---
title: "Fix MIDI Keyboard Key Leakage"
date: "2026-08-01"
conversation_id: "d0b88e59-448a-4bb3-865a-cb44ec13772a"
source: "antigravity"
---

# Fix MIDI Keyboard Key Leakage

## User

Let's fix the issue where unmapped/unhandled keys (or keys that return `false`) leak every second press or leak to background apps, OR where unmapped keys during active MIDI controller mode pass through to the app behind it.

Wait! When `state.midiActive` is true, should EVERY key press on the physical keyboard be swallowed by the controller so keys NEVER leak into the application behind it?
Wait! Let's check `src/init.lua`:
```lua
_G.activeWatchers.midiKeyTap = hs.eventtap.new({ hs.eventtap.event.types.keyDown, hs.eventtap.event.types.keyUp, hs.eventtap.event.types.flagsChanged }, function(event)
  if not state.midiActive then return false end
...
```
When `state.midiActive` is true, the user is using their QWERTY keyboard AS A MIDI CONTROLLER!
If a key is pressed while `midiActive` is true:
1. System hotkeys (Cmd, Alt/Opt, Ctrl, CapsLock) -> lines 203-205:
`if flags.cmd or flags.alt or flags.ctrl or flags.capslock then return false end`
These SHOULD pass through to OS so hotkeys like `Cmd+C`, `Cmd+V`, `Cmd+Shift+4` work!
2. DevTools/Inspector focused -> lines 169-175:
`if string.find(title, "Inspector") or string.find(title, "DevTools") then return false end`
3. Text input active -> lines 154-156:
`if state.textInputActive then return false end`
4. Backspace/Delete (51, 117) in webview edit mode -> lines 161-166.
5. `flagsChanged` (Shift, etc.) -> line 214: `return false` (lets modifier key state register).

BUT for regular key down / key up events (`keyDown`, `keyUp`) when no modifier keys (`cmd`, `alt`, `ctrl`, `capslock`) are down:
If `handleKeyDown(code)` returns `false` (because `code` is an unmapped or unassigned key on the keyboard, e.g. Spacebar, Tab, Enter, or keys with `action = "none"`), `init.lua` receives `status = false`, and `midiKeyTap` returns `false` to Hammerspoon eventtap!
Returning `false` tells macOS eventtap to PASS THE KEYSTROKE THROUGH to the active app behind Hammerspoon!
So if the user presses an unmapped key, or a key that resolves to `false`, it leaks through to the a
<truncated 4038 bytes>
.capslock` is true, or `state.textInputActive` is true, or DevTools is focused), then:
1. Mapped note keys: play MIDI notes, swallowed (`return true`).
2. Mapped control keys: execute control actions, swallowed (`return true`).
3. Unmapped keys / other keys: swallowed (`return true`).
4. Repeat events / second presses: swallowed (`return true`).

Let's check if there are any files we need to update:
`src/init.lua` AND `qwerty_midi.lua` (the bundled file)!
Remember the Post-Edit Reload Protocol rule in system rules:
"Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done."

Subagent, let's update `src/init.lua` and `src/controls.lua` so that:
1. In `src/controls.lua`:
- In `handleKeyDown(code)`: if `state.pressedKeys[code]` is already present, return `true`.
- Ensure `handleKeyDown(code)` returns `true` for note keys, control keys, AND unmapped keys when called during active MIDI mode (or return `true` as default at the end of `handleKeyDown` and `handleKeyUp`).
- In `handleKeyUp(code)`: ensure `handleKeyUp` always returns `true` (clearing `state.pressedKeys[code]` if present).

2. In `src/init.lua`:
- In `midiKeyTap`: after checking `state.textInputActive`, DevTools focus, `flags.cmd/alt/ctrl/capslock`, `bpmInputMode`, and `flagsChanged`, when `isDown` or `isUp` runs `controls.handleKeyDown` / `controls.handleKeyUp`, if status is not explicitly `false` due to an error, return `true`! In fact, returning `true` unconditionally for key events when `state.midiActive` is active ensures 100% of keystrokes are swallowed by the controller and never leak to background applications!

Please perform these edits using `replace_file_content` or `multi_replace_file_content`.

---

## Assistant

Created At: 2026-07-31T20:50:26-06:00
Completed At: 2026-07-31T20:50:26-06:00
{"name":"arpeggiator.lua","sizeBytes":"20989"}
{"name":"config.lua","sizeBytes":"31038"}
{"name":"controls.lua","sizeBytes":"36538"}
{"name":"hud.lua","sizeBytes":"25354"}
{"name":"init.lua","sizeBytes":"12782"}
{"name":"midi.lua","sizeBytes":"2467"}
{"name":"settings_ui.lua","sizeBytes":"15909"}
{"name":"transposer.lua","sizeBytes":"2302"}
{"name":"ui_html.lua","sizeBytes":"124298"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-07-31T20:50:27-06:00
Completed At: 2026-07-31T20:50:27-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 358
Total Bytes: 12782
Showing lines 1 to 358
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local config = require("config")
2: local midi = require("midi")
3: local transposer = require("transposer")
4: local arpeggiator = require("arpeggiator")
5: local hud = require("hud")
6: local controls = require("controls")
7: local settings_ui = require("settings_ui")
8: 
9: local function profileLog(msg)
10:   local f = io.open("/tmp/midi_startup.log", "a")
11:   if f then
12:     f:write(os.clock() .. ": " .. msg .. "\n")
13:     f:close()
14:   end
15: end
16: profileLog("Start init.lua")
17: 
18: local state = config.state
19: 
20: _G.activeWatchers = _G.activeWatchers or {}
21: 
22: arpeggiator.setHudModule(hud)
23: hud.setControlsModule(controls)
24: 
25: function _G.toggleMidiMode(newState)
26:   if newState == nil then
27:     state.midiActive = not state.midiActive
28:   else
29:     state.midiActive = newState
30:   end
31: 
32:   -- Persist window-open state so reload can auto-reopen if needed
33:   hs.settings.set("qwertyMidi_wasOpen", state.midiActive)
34: 
35:   if state.midiActive then
36:     profileLog("Starting midiActive logic")
37:     _G.activeWatchers.midiKeyTap:start()
38:     _G.activeWatchers.midiScrollTap:start()
39:     profileLog("Before createMidiWebview")
40:     local h = hud.createMidiWebview()
41:     profileLog("After createMidiWebview, before show")
42:     h:show()
43:     profileLog("After show")
44:   else
45:     -- Stop all key repeats before tearing down
46:     if controls.stopAllControlRepeats then
47:       controls.stopAllControlRepeats()
48:     end
49:     _G.activeWatchers.midiKeyTap:stop()
50:     _G.activeWatch
<truncated 10908 bytes>
tive: " .. tostring(state.midiActive))
302:   table.insert(logs, "Zoom Level: " .. tostring(state.zoomLevel))
303:   table.insert(logs, "Root Note: " .. tostring(state.rootNote))
304:   table.insert(logs, "Scale Idx: " .. tostring(state.scaleIdx))
305: 
306:   local f = io.open("/tmp/midi_startup.log", "r")
307:   if f then
308:     table.insert(logs, "\n--- Startup Log ---")
309:     table.insert(logs, f:read("*a"))
310:     f:close()
311:   end
312:   local fjs = io.open("/tmp/wv_js.log", "r")
313:   if fjs then
314:     table.insert(logs, "\n--- Webview JS Log ---")
315:     table.insert(logs, fjs:read("*a"))
316:     fjs:close()
317:   end
318: 
319:   local fullLogStr = table.concat(logs, "\n")
320:   hs.pasteboard.setContents(fullLogStr)
321: 
322:   -- 3. Display user notification & HUD overlay
323:   hs.alert.show("UI Rescued — Diagnostic Logs Copied to Clipboard", 2.0)
324:   hs.notify.new({
325:     title = "QWERTY MIDI",
326:     informativeText = "UI rescued and diagnostic logs copied to clipboard."
327:   }):send()
328: end)
329: 
330: if _G.activeWatchers.settingsHotkey then
331:   _G.activeWatchers.settingsHotkey:delete()
332:   _G.activeWatchers.settingsHotkey = nil
333: end
334: 
335: profileLog("Before panicAllChannels")
336: midi.panicAllChannels()
337: 
338: -- Auto-reopen window if it was open when the last reload occurred
339: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
340: if wasOpen then
341:   profileLog("Auto-reopening controller window (was open before reload)")
342:   hs.timer.doAfter(0.3, function()
343:     local ok, err = pcall(function()
344:       _G.toggleMidiMode(true)
345:     end)
346:     if not ok then
347:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
348:     end
349:   end)
350: end
351: 
352: profileLog("Init complete!")
353: 
354: return {
355:   toggleMidiMode = _G.toggleMidiMode,
356:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
357: }
358: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T20:50:28-06:00
Completed At: 2026-07-31T20:50:28-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1062
Total Bytes: 36538
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local config = require("config")
2: local midi = require("midi")
3: local transposer = require("transposer")
4: local arpeggiator = require("arpeggiator")
5: local hud = require("hud")
6: 
7: local state = config.state
8: local SCALES = config.SCALES
9: local NOTE_NAMES = config.NOTE_NAMES
10: 
11: _G.activeWatchers = _G.activeWatchers or {}
12: 
13: -- Clear any stale repeat timers from a previous module load (Hammerspoon reload safety)
14: if _G._qmidiRepeatTimers then
15:   for code, entry in pairs(_G._qmidiRepeatTimers) do
16:     pcall(function()
17:       if entry.timer then entry.timer:stop() end
18:       if entry.interval then entry.interval:stop() end
19:     end)
20:   end
21: end
22: _G._qmidiRepeatTimers = {}
23: local controlRepeatTimers = _G._qmidiRepeatTimers
24: 
25: local function stopControlRepeat(code)
26:   if code and controlRepeatTimers[code] then
27:     pcall(function()
28:       if controlRepeatTimers[code].timer then
29:         controlRepeatTimers[code].timer:stop()
30:       end
31:       if controlRepeatTimers[code].interval then
32:         controlRepeatTimers[code].interval:stop()
33:       end
34:     end)
35:     controlRepeatTimers[code] = nil
36:   end
37: end
38: 
39: local function stopAllControlRepeats()
40:   for code in pairs(controlRepeatTimers) do
41:     stopControlRepeat(code)
42:   end
43: end
44: 
45: local stateUndoStack = {}
46: local stateRedoStack = {}
47: local isRestoringControllerState = false
48: 
49: local function captureStateSnapshot(label)
50:   return {
51:     label = label or "State Change",
52: 
<truncated 28275 bytes>
WebviewHud(spot)
756:   elseif act == "arpDirUp" then
757:     state.arpDirectionIdx = (state.arpDirectionIdx % #state.ARP_DIRECTIONS) + 1
758:     local spot = {
759:       title = "ARP DIRECTION",
760:       value = state.ARP_DIRECTIONS[state.arpDirectionIdx],
761:       subtext = state.arpEnabled and "Active Pattern" or "Arp Disabled",
762:       targetId = "arp-dir-select",
763:       color = "#d4a359"
764:     }
765:     hud.updateWebviewHud(spot)
766:   elseif act == "arpRateDown" then
767:     state.arpRateIdx = math.max(1, state.arpRateIdx - 1)
768:     arpeggiator.applyBpmChange()
769:     local spot = {
770:       title = "ARP RATE",
771:       value = state.ARP_RATES[state.arpRateIdx].label,
772:       subtext = "Note Division",
773:       targetId = "arp-rate-select",
774:       color = "#d4a359"
775:     }
776:     hud.updateWebviewHud(spot)
777:   elseif act == "arpRateUp" then
778:     state.arpRateIdx = math.min(#state.ARP_RATES, state.arpRateIdx + 1)
779:     arpeggiator.applyBpmChange()
780:     local spot = {
781:       title = "ARP RATE",
782:       value = state.ARP_RATES[state.arpRateIdx].label,
783:       subtext = "Note Division",
784:       targetId = "arp-rate-select",
785:       color = "#d4a359"
786:     }
787:     hud.updateWebviewHud(spot)
788:   elseif act == "arpGateDown" then
789:     state.arpGatePercent = math.max(5.0, (state.arpGatePercent or 80.0) - 5.0)
790:     arpeggiator.applyGatePercentChange()
791:     local spot = {
792:       title = "ARP NOTE LENGTH",
793:       value = math.floor(state.arpGatePercent + 0.5) .. "%",
794:       subtext = "Gate Duration",
795:       targetId = "gate-value",
796:       color = "#d4a359"
797:     }
798:     hud.updateWebviewHud(spot)
799:   elseif act == "arpGateUp" then
800:     state.arpGatePercent = math.min(150.0, (state.arpGatePercent or 80.0) + 5.0)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:29-06:00
Completed At: 2026-07-31T20:50:29-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1062
Total Bytes: 36538
Showing lines 801 to 1062
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
801:     arpeggiator.applyGatePercentChange()
802:     local spot = {
803:       title = "ARP NOTE LENGTH",
804:       value = math.floor(state.arpGatePercent + 0.5) .. "%",
805:       subtext = "Gate Duration",
806:       targetId = "gate-value",
807:       color = "#d4a359"
808:     }
809:     hud.updateWebviewHud(spot)
810:   elseif act == "bpmDown" then
811:     local step = state.bpmStepSize or 10
812:     state.arpBpm = math.max(20.0, state.arpBpm - step)
813:     arpeggiator.applyBpmChange()
814:     arpeggiator.stepLogicBpm(-step)
815:     local spot = {
816:       title = "TEMPO / BPM",
817:       value = arpeggiator.formatBpm(state.arpBpm) .. " BPM",
818:       subtext = "Step: " .. step .. " BPM",
819:       targetId = "bpm-value",
820:       color = "#d4a359"
821:     }
822:     hud.updateWebviewHud(spot)
823:   elseif act == "bpmUp" then
824:     local step = state.bpmStepSize or 10
825:     state.arpBpm = math.min(300.0, state.arpBpm + step)
826:     arpeggiator.applyBpmChange()
827:     arpeggiator.stepLogicBpm(step)
828:     local spot = {
829:       title = "TEMPO / BPM",
830:       value = arpeggiator.formatBpm(state.arpBpm) .. " BPM",
831:       subtext = "Step: " .. step .. " BPM",
832:       targetId = "bpm-value",
833:       color = "#d4a359"
834:     }
835:     hud.updateWebviewHud(spot)
836:   elseif act == "relDown" or act == "releaseDown" then
837:     local currentVal = state.ccStates[72] or 64
838:     local newVal = math.max(0, currentVal - 4)
839:     state.ccStates[72] = newVal
840:     midi.sendMidiCC(72, newVal)
841:     loc
<truncated 6636 bytes>
         state.sustainActive = false
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
1051:   end
1052: 
1053:   return false
1054: end
1055: 
1056: return {
1057:   executeControlAction = executeControlAction,
1058:   handleKeyDown = handleKeyDown,
1059:   handleKeyUp = handleKeyUp,
1060:   stopAllControlRepeats = stopAllControlRepeats
1061: }
1062: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:37-06:00
Completed At: 2026-07-31T20:50:37-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1062
Total Bytes: 36536
Showing lines 879 to 1062
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
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
911:   if k and k.action and k.action ~= "" and k.action ~= "none" then
912:     state.pressedKeys[code] = { isControl = true, action = k.action }
913:     executeControlAction(k.action, code)
914:     if k.action ~= "sustain" then

<truncated 3836 bytes>
          state.sustainActive = false
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
1051:   end
1052: 
1053:   return true
1054: end
1055: 
1056: return {
1057:   executeControlAction = executeControlAction,
1058:   handleKeyDown = handleKeyDown,
1059:   handleKeyUp = handleKeyUp,
1060:   stopAllControlRepeats = stopAllControlRepeats
1061: }
1062: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-07-31T20:50:38-06:00
Completed At: 2026-07-31T20:50:38-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-07-31T20:50:39-06:00
Completed At: 2026-07-31T20:50:39-06:00
Message sent to "41f79905-6dba-47e7-b964-324bdb5f4fb2".

The task of fixing key leakage in `qwerty-midi-hammerspoon` has been completed.

### Summary of Changes

1.  **`src/init.lua`**: Modified `midiKeyTap` to unconditionally swallow key events while `midiActive` is `true`. Previously, it relied on the return values of `handleKeyDown` and `handleKeyUp`, which led to leaks when those functions returned `false`.
2.  **`src/controls.lua`**: Updated `handleKeyDown` and `handleKeyUp` to consistently return `true`. This guarantees that once a key event enters the QWERTY MIDI controller in MIDI mode, it is consumed and never passed on to the OS or background applications.
3.  **Post-flight**: Executed `/Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` to bundle the Lua modules and reload Hammerspoon.

These changes ensure that unmapped keys and repeated key presses are now correctly swallowed, resolving the reported leakage issues.

---
