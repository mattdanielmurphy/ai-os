---
title: "Implement Sustain Pedal Logic"
date: "2026-08-03"
conversation_id: "9723eeaf-9562-4302-be3e-3b6432e98c86"
source: "antigravity"
---

# Implement Sustain Pedal Logic

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua:

1. In `handleKeyDown` (around line 1099-1107):
   Compute `sustainPedalHeld`:
   ```lua
   local sustainPedalHeld = false
   for c, info in pairs(state.pressedKeys) do
     if type(info) == "table" and info.isControl and info.action == "sustain" then
       sustainPedalHeld = true
       break
     end
   end
   local effectiveSustain = (state.shiftHeld and (not (state.sustainActive or sustainPedalHeld))) or ((not state.shiftHeld) and (state.sustainActive or sustainPedalHeld))
   state.pressedKeys[code] = { pitches = chordPitches, isArpNote = isArpNote, isSustainedNote = effectiveSustain, channel = ch }
   ```

2. In `handleKeyUp` for note keys (around line 1153-1160):
   Update the condition:
   ```lua
   local sustainPedalHeld = false
   for c, info in pairs(state.pressedKeys) do
     if type(info) == "table" and info.isControl and info.action == "sustain" then
       sustainPedalHeld = true
       break
     end
   end
   for _, playedPitch in ipairs(pitches) do
     if isSustainedNote and (state.sustainActive or sustainPedalHeld) then
       state.sustainedPitches = state.sustainedPitches or {}
       state.sustainedPitches[playedPitch] = { channel = keyChannel }
     else
       midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
     end
   end
   ```

3. In `executeControlAction` for `sustain` (around line 626-646):
   Keep `state.sustainWasActiveOnPress = state.sustainActive`. Send `midi.sendMidiCC(64, 127)`. Retroactively tag held notes:
   ```lua
   elseif act == "sustain" then
     state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
     state.sustainWasActiveOnPress = state.sustainActive
     midi.sendMidiCC(64, 127)

     -- Retroactively sustain all non-arp notes currently being physically held down
     for code, keyInfo in pairs(state.pressedKeys) do
       if type(keyInfo) == "table" and not keyInfo.isControl then
         keyInfo.isSustainedNote = true
         if not keyInfo.isArpNote then
           local pitches = keyInfo.pitches or { keyInfo.pitch }
           local ch = keyInfo.channel or 0
           for _, p in ipairs(pitches) do
             if p then
               state.sustainedPitches = state.sustainedPitches or {}
               state.sustainedPitches[p] = { channel = ch }
             end
           end
         end
       end
     end
   ```

4. In `handleKeyUp` for `ctrlKey` when `act == "sustain"`:
   ```lua
   if act == "sustain" then
     state.sustainActive = not state.sustainWasActiveOnPress
     midi.sendMidiCC(64, 0)
     cleanupSustainPitches()
   ```

Apply these edits using multi_replace_file_content.

---

## Assistant

Created At: 2026-08-03T01:53:05-06:00
Completed At: 2026-08-03T01:53:05-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1296
Total Bytes: 45100
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
<truncated 28211 bytes>
   color = "#d4a359"
759:     }
760:     hud.updateWebviewHud(spot)
761:   elseif act == "volDown" then
762:     state.topRowVolume = math.max(0, state.topRowVolume - 4)
763:     state.bottomRowVolume = math.max(0, state.bottomRowVolume - 4)
764:     local spot = {
765:       title = "ROW VOLUMES",
766:       value = "TOP " .. math.floor((state.topRowVolume / 127) * 100) .. "% | BOT " .. math.floor((state.bottomRowVolume / 127) * 100) .. "%",
767:       subtext = "Dual Row Volume Level",
768:       targetId = "header",
769:       color = "#d4a359"
770:     }
771:     hud.updateWebviewHud(spot)
772:   elseif act == "volUp" or act == "volume" then
773:     state.topRowVolume = math.min(127, state.topRowVolume + 4)
774:     state.bottomRowVolume = math.min(127, state.bottomRowVolume + 4)
775:     local spot = {
776:       title = "ROW VOLUMES",
777:       value = "TOP " .. math.floor((state.topRowVolume / 127) * 100) .. "% | BOT " .. math.floor((state.bottomRowVolume / 127) * 100) .. "%",
778:       subtext = "Dual Row Volume Level",
779:       targetId = "header",
780:       color = "#d4a359"
781:     }
782:     hud.updateWebviewHud(spot)
783:   elseif act == "arpTopToggle" then
784:     state.arpTopEnabled = not state.arpTopEnabled
785:     if not state.arpTopEnabled then
786:       for code in pairs(state.arpHeldNotes) do
787:         local noteKey = config.getNoteKey(code)
788:         if noteKey and noteKey.isTop then
789:           state.arpHeldNotes[code] = nil
790:           state.arpKeysCurrentlyHeld[code] = nil
791:         end
792:       end
793:     end
794:     local spot = {
795:       title = "TOP ROW ARP",
796:       value = state.arpTopEnabled and "TOP ARP: ON" or "TOP ARP: OFF",
797:       subtext = arpeggiator.getArpRowTargetSubtext(),
798:       targetId = "arp-top-toggle",
799:       color = "#d4a359"
800:     }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:53:06-06:00
Completed At: 2026-08-03T01:53:06-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":992,"LineContent":"local function handleKeyDown(code)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1292,"LineContent":"  handleKeyDown = handleKeyDown,"}

Created At: 2026-08-03T01:53:07-06:00
Completed At: 2026-08-03T01:53:07-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1296
Total Bytes: 45100
Showing lines 1080 to 1120
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1080:             pcall(executeControlAction, k.action, code)
1081:             pushStateSnapshot = savedFn
1082:           end)
1083:         end
1084:       end)
1085:     else
1086:       stopControlRepeat(code)
1087:     end
1088:     return true
1089:   end
1090: 
1091:   local noteKey = config.getNoteKey(code)
1092:   if noteKey then
1093:     local isTop = noteKey.isTop
1094:     local transposedPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
1095:     local chordPitches = (state.quoteHeld or state.chordModeActive) and transposer.getChordPitches(noteKey.baseNote, isTop) or { transposedPitch }
1096:     local arpEnabledForRow = isTop and state.arpTopEnabled or (not isTop and state.arpBottomEnabled)
1097:     local arpActive = state.arpEnabled and arpEnabledForRow
1098:     local sustainActive = state.sustainActive
1099:     local isArpNote = arpActive
1100:     if state.shiftHeld then
1101:       isArpNote = not arpActive
1102:     end
1103:     local isSustainedNote = state.shiftHeld and (not sustainActive) or ((not state.shiftHeld) and sustainActive)
1104:     local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
1105:     
1106:     state.pressedKeys[code] = { pitches = chordPitches, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }
1107:     
1108:     if isArpNote then 
1109:       for _, p in ipairs(chordPitches) do arpeggiator.arpAddNote(code .. "_" .. p, p) end
1110:     else 
1111:       for _, p in ipairs(chordPitches) do
1112:         midi.sendMidiNote("noteOn", p, transposer.getEffectiveRowVelocity(isTop), ch)
1113:       end
1114:     end
1115:     hud.updateWebviewHud()
1116:     return true
1117:   end
1118: 
1119:   return true
1120: end
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:53:07-06:00
Completed At: 2026-08-03T01:53:07-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1296
Total Bytes: 45100
Showing lines 1140 to 1170
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1140:   local noteKey = config.getNoteKey(code)
1141:   if noteKey then
1142:     local keyInfo = state.pressedKeys[code]
1143:     if keyInfo then
1144:       local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
1145:       local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
1146:       local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote
1147: 
1148:       local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
1149:       if isArpNote then
1150:         for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
1151:       else
1152:         for _, playedPitch in ipairs(pitches) do
1153:           if isSustainedNote and state.sustainActive then
1154:             state.sustainedPitches = state.sustainedPitches or {}
1155:             state.sustainedPitches[playedPitch] = { channel = keyChannel }
1156:           else
1157:             midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
1158:           end
1159:         end
1160:       end
1161:       state.pressedKeys[code] = nil
1162:     else
1163:       -- Failsafe: keyInfo was missing from state.pressedKeys, calculate pitch & send noteOff directly
1164:       local isTop = noteKey.isTop
1165:       local fallbackPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
1166:       local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
1167:       midi.sendMidiNote("noteOff", fallbackPitch, 0, ch)
1168:     end
1169:     hud.updateSingleKeyState(code, false, false)
1170:     hud.updateWebviewHud()
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:53:08-06:00
Completed At: 2026-08-03T01:53:08-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1296
Total Bytes: 45100
Showing lines 1170 to 1190
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1170:     hud.updateWebviewHud()
1171:     return true
1172:   end
1173: 
1174:   local numCtrlKey = config.getNumberControlKey(code)
1175:   if numCtrlKey then
1176:     stopControlRepeat(code)
1177:       state.pressedKeys[code] = nil
1178:       hud.updateSingleKeyState(code, false, false)
1179:       hud.updateWebviewHud()
1180:       return true
1181:   end
1182: 
1183:   local function cleanupSustainPitches()
1184:     if state.sustainedPitches then
1185:       for pitch, item in pairs(state.sustainedPitches) do
1186:         local channel = type(item) == "table" and item.channel or 0
1187:         local isCurrentlyHeld = false
1188:         for _, kInfo in pairs(state.pressedKeys) do
1189:           if type(kInfo) == "table" then
1190:             local pList = kInfo.pitches or { kInfo.pitch }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:53:09-06:00
Completed At: 2026-08-03T01:53:09-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":626,"LineContent":"  elseif act == \"sustain\" then"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1238,"LineContent":"    if act == \"sustain\" then"}

Created At: 2026-08-03T01:53:09-06:00
Completed At: 2026-08-03T01:53:10-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1296
Total Bytes: 45100
Showing lines 1230 to 1250
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1230:           targetId = "key-48",
1231:           color = state.sustainActive and "#d4a359" or "#b5aba0"
1232:         } or nil
1233:         hud.updateWebviewHud(spot)
1234:         return true
1235:       end
1236:     end
1237: 
1238:     if act == "sustain" then
1239:       if state.sustainWasActiveOnPress then
1240:         state.sustainActive = false
1241:         midi.sendMidiCC(64, 0)
1242:         cleanupSustainPitches()
1243:       else
1244:         state.sustainActive = not state.sustainWasActiveOnPress
1245:         if not state.sustainActive then
1246:           midi.sendMidiCC(64, 0)
1247:           cleanupSustainPitches()
1248:         else
1249:           midi.sendMidiCC(64, 127)
1250:         end
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:53:13-06:00
Completed At: 2026-08-03T01:53:13-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -630,7 +630,7 @@
 
     -- Retroactively sustain all non-arp notes currently being physically held down
     for code, keyInfo in pairs(state.pressedKeys) do
-      if type(keyInfo) == "table" then
+      if type(keyInfo) == "table" and not keyInfo.isControl then
         keyInfo.isSustainedNote = true
         if not keyInfo.isArpNote then
           local pitches = keyInfo.pitches or { keyInfo.pitch }
@@ -1094,15 +1094,16 @@
     local chordPitches = (state.quoteHeld or state.chordModeActive) and transposer.getChordPitches(noteKey.baseNote, isTop) or { transposedPitch }
     local arpEnabledForRow = isTop and state.arpTopEnabled or (not isTop and state.arpBottomEnabled)
     local arpActive = state.arpEnabled and arpEnabledForRow
-    local sustainActive = state.sustainActive
-    local isArpNote = arpActive
-    if state.shiftHeld then
-      isArpNote = not arpActive
-    end
-    local isSustainedNote = state.shiftHeld and (not sustainActive) or ((not state.shiftHeld) and sustainActive)
-    local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
-    
-    state.pressedKeys[code] = { pitches = chordPitches, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }
+    local sustainPedalHeld = false
+    for c, info in pairs(state.pressedKeys) do
+      if type(info) == "table" and info.isControl and info.action == "sustain" then
+        sustainPedalHeld = true
+        break
+      end
+    end
+    local effectiveSustain = (state.shiftHeld and (not (state.sustainActive or sustainPedalHeld))) or ((not state.shiftHeld) and (state.sustainActive or sustainPedalHeld))
+    
+    state.pressedKeys[code] = { pitches = chordPitches, isArpNote = isArpNote, isSustainedNote = effectiveSustain, channel = ch }
     
     if isArpNote then 
       for _, p in ipairs(chordPitches) do arpeggiator.arpAddNote(code .. "_" .. p, p) end
@@ -1147,8 +1147,15 @@
       if isArpNote then
         for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
       else
+        local sustainPedalHeld = false
+        for c, info in pairs(state.pressedKeys) do
+          if type(info) == "table" and info.isControl and info.action == "sustain" then
+            sustainPedalHeld = true
+            break
+          end
+        end
         for _, playedPitch in ipairs(pitches) do
-          if isSustainedNote and state.sustainActive then
+          if isSustainedNote and (state.sustainActive or sustainPedalHeld) then
             state.sustainedPitches = state.sustainedPitches or {}
             state.sustainedPitches[playedPitch] = { channel = keyChannel }
           else
@@ -1233,19 +1233,9 @@
     end
 
     if act == "sustain" then
-      if state.sustainWasActiveOnPress then
-        state.sustainActive = false
-        midi.sendMidiCC(64, 0)
-        cleanupSustainPitches()
-      else
-        state.sustainActive = not state.sustainWasActiveOnPress
-        if not state.sustainActive then
-          midi.sendMidiCC(64, 0)
-          cleanupSustainPitches()
-        else
-          midi.sendMidiCC(64, 127)
-        end
-      end
+      state.sustainActive = not state.sustainWasActiveOnPress
+      midi.sendMidiCC(64, 0)
+      cleanupSustainPitches()
 
       local spot = {
         title = "SUSTAIN (CC #64)",
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T01:53:15-06:00
Completed At: 2026-08-03T01:53:15-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The sustain pedal logic improvements have been successfully applied to `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`.

The updates were made to:
1. **`handleKeyDown`**: Now calculates `sustainPedalHeld` based on active control keys and incorporates it into the `effectiveSustain` calculation.
2. **`handleKeyUp` (notes)**: Now checks `sustainPedalHeld` alongside `state.sustainActive` to determine if notes should be sustained upon release.
3. **`executeControlAction` (`sustain`)**: Updated to ensure held note tagging correctly ignores control keys and properly retroactively tags notes.
4. **`handleKeyUp` (`ctrlKey` for `sustain`)**: Simplified the logic to toggle `state.sustainActive`, send CC 64 OFF, and clean up sustained pitches.

---
