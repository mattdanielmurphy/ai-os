---
title: "Refactor MIDI Key Handling"
date: "2026-08-03"
conversation_id: "298d0dc0-2ab9-4156-9597-6171a11aa006"
source: "antigravity"
---

# Refactor MIDI Key Handling

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua:

1. Update `handleKeyUp` (lines 1147-1187) so `state.pressedKeys[code]` is checked FIRST (as ground truth) before `config.getNoteKey(code)`:

Replace lines 1147 to 1187:
```lua
  local noteKey = config.getNoteKey(code)
  if noteKey then
    local keyInfo = state.pressedKeys[code]
    if keyInfo then
      local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
      local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
      local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote

      local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
      if isArpNote then
        for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
      else
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
            table.insert(state.sustainedPitches, { pitch = playedPitch, channel = keyChannel })
          else
            midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
          end
        end
      end
      state.pressedKeys[code] = nil
    else
      -- Failsafe: keyInfo was missing from state.pressedKeys, calculate pitch & send noteOff directly
      local isTop = noteKey.isTop
      local fallbackPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
      local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
      midi.sendMidiNote("noteOff", fallbackPitch, 0, ch)
    end
    hud.updateSingleKeyState(code, false, false)
    hud.updateWebviewHud()
    return true
  end
```

With:
```lua
  local keyInfo = state.
<truncated 3108 bytes>
p == pitch and (kInfo.channel or 0) == channel then
                  isCurrentlyHeld = true
                  break
                end
              end
              if isCurrentlyHeld then break end
            end
          end
          if not isCurrentlyHeld then
            midi.sendMidiNote("noteOff", pitch, 0, channel)
          end
        end
      end
      state.sustainedPitches = {}
    end
  end
```

3. Update `handleKeyUp` for `act == "sustain"` to use `midi.sendSustainCC` (lines 1235-1277):

Replace lines 1235 to 1277:
```lua
        if (wasSustain or act == "sustain") and not state.sustainActive then
          midi.sendMidiCC(64, 0)
          cleanupSustainPitches()
        elseif not wasSustain and state.sustainActive then
          midi.sendMidiCC(64, 127)
        end
```
and:
```lua
    if act == "sustain" then
      if state.sustainWasActiveOnPress then
        state.sustainActive = false
        midi.sendMidiCC(64, 0)
        cleanupSustainPitches()
      else
        state.sustainActive = true
        midi.sendMidiCC(64, 127)
        -- Retroactively sustain all non-arp notes currently being physically held down
        for c, keyInfo in pairs(state.pressedKeys) do
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
      end
```

With `midi.sendSustainCC(...)` and `table.insert(state.sustainedPitches, { pitch = p, channel = ch })`.

Apply these edits using multi_replace_file_content.

---

## Assistant

Created At: 2026-08-03T02:04:18-06:00
Completed At: 2026-08-03T02:04:18-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1322
Total Bytes: 46256
Showing lines 1140 to 1300
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1140:       for _, heldCode in ipairs(keysToRelease) do
1141:         handleKeyUp(heldCode)
1142:       end
1143:     end
1144:     hud.updateWebviewHud()
1145:     return true
1146:   end
1147: 
1148:   local noteKey = config.getNoteKey(code)
1149:   if noteKey then
1150:     local keyInfo = state.pressedKeys[code]
1151:     if keyInfo then
1152:       local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
1153:       local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
1154:       local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote
1155: 
1156:       local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
1157:       if isArpNote then
1158:         for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
1159:       else
1160:         local sustainPedalHeld = false
1161:         for c, info in pairs(state.pressedKeys) do
1162:           if type(info) == "table" and info.isControl and info.action == "sustain" then
1163:             sustainPedalHeld = true
1164:             break
1165:           end
1166:         end
1167:         for _, playedPitch in ipairs(pitches) do
1168:           if isSustainedNote and (state.sustainActive or sustainPedalHeld) then
1169:             state.sustainedPitches = state.sustainedPitches or {}
1170:             state.sustainedPitches[playedPitch] = { channel = keyChannel }
1171:           else
1172:             midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
1173:           end
1174:         end
1175:       end
1176: 
<truncated 3602 bytes>
e
1259:         state.sustainActive = true
1260:         midi.sendMidiCC(64, 127)
1261:         -- Retroactively sustain all non-arp notes currently being physically held down
1262:         for c, keyInfo in pairs(state.pressedKeys) do
1263:           if type(keyInfo) == "table" and not keyInfo.isControl then
1264:             keyInfo.isSustainedNote = true
1265:             if not keyInfo.isArpNote then
1266:               local pitches = keyInfo.pitches or { keyInfo.pitch }
1267:               local ch = keyInfo.channel or 0
1268:               for _, p in ipairs(pitches) do
1269:                 if p then
1270:                   state.sustainedPitches = state.sustainedPitches or {}
1271:                   state.sustainedPitches[p] = { channel = ch }
1272:                 end
1273:               end
1274:             end
1275:           end
1276:         end
1277:       end
1278: 
1279:       local spot = {
1280:         title = "SUSTAIN (CC #64)",
1281:         value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
1282:         subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
1283:         targetId = "key-48",
1284:         color = state.sustainActive and "#d4a359" or "#b5aba0"
1285:       }
1286:       hud.updateWebviewHud(spot)
1287:     elseif act == "chordToggle" then
1288:       if state.chordWasActiveOnPress then
1289:         state.chordModeActive = false
1290:       else
1291:         state.chordModeActive = true
1292:       end
1293:       
1294:       local spot = {
1295:         title = "CHORD MODE",
1296:         value = state.chordModeActive and "ON" or "OFF",
1297:         subtext = "Chord mode: " .. (state.chordModeActive and "Enabled" or "Disabled"),
1298:         targetId = "header",
1299:         color = state.chordModeActive and "#d4a359" or "#b5aba0"
1300:       }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T02:04:24-06:00
Completed At: 2026-08-03T02:04:24-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1145,42 +1145,45 @@
     return true
   end
 
-  local noteKey = config.getNoteKey(code)
-  if noteKey then
-    local keyInfo = state.pressedKeys[code]
-    if keyInfo then
-      local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
-      local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
-      local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote
-
-      local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
-      if isArpNote then
-        for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
-      else
-        local sustainPedalHeld = false
-        for c, info in pairs(state.pressedKeys) do
-          if type(info) == "table" and info.isControl and info.action == "sustain" then
-            sustainPedalHeld = true
-            break
-          end
-        end
-        for _, playedPitch in ipairs(pitches) do
-          if isSustainedNote and (state.sustainActive or sustainPedalHeld) then
-            state.sustainedPitches = state.sustainedPitches or {}
-            state.sustainedPitches[playedPitch] = { channel = keyChannel }
-          else
-            midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
-          end
-        end
-      end
-      state.pressedKeys[code] = nil
-    else
-      -- Failsafe: keyInfo was missing from state.pressedKeys, calculate pitch & send noteOff directly
-      local isTop = noteKey.isTop
-      local fallbackPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
-      local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
-      midi.sendMidiNote("noteOff", fallbackPitch, 0, ch)
<truncated 3007 bytes>
rue
+                  break
+                end
+              end
+              if isCurrentlyHeld then break end
+            end
+          end
+          if not isCurrentlyHeld then
+            midi.sendMidiNote("noteOff", pitch, 0, channel)
+          end
         end
       end
       state.sustainedPitches = {}
@@ -1231,10 +1231,10 @@
         local wasSustain = state.sustainActive
         applyStateSnapshot(state.controlKeyDownSnapshots[code])
         if (wasSustain or act == "sustain") and not state.sustainActive then
-          midi.sendMidiCC(64, 0)
+          midi.sendSustainCC(0)
           cleanupSustainPitches()
         elseif not wasSustain and state.sustainActive then
-          midi.sendMidiCC(64, 127)
+          midi.sendSustainCC(127)
         end
         local spot = act == "sustain" and {
           title = "SUSTAIN (CC #64)",
@@ -1250,11 +1250,11 @@
     if act == "sustain" then
       if state.sustainWasActiveOnPress then
         state.sustainActive = false
-        midi.sendMidiCC(64, 0)
+        midi.sendSustainCC(0)
         cleanupSustainPitches()
       else
         state.sustainActive = true
-        midi.sendMidiCC(64, 127)
+        midi.sendSustainCC(127)
         -- Retroactively sustain all non-arp notes currently being physically held down
         for c, keyInfo in pairs(state.pressedKeys) do
           if type(keyInfo) == "table" and not keyInfo.isControl then
@@ -1264,7 +1264,7 @@
               for _, p in ipairs(pitches) do
                 if p then
                   state.sustainedPitches = state.sustainedPitches or {}
-                  state.sustainedPitches[p] = { channel = ch }
+                  table.insert(state.sustainedPitches, { pitch = p, channel = ch })
                 end
               end
             end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T02:04:25-06:00
Completed At: 2026-08-03T02:04:25-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The requested updates to `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` have been completed successfully.

- **`handleKeyUp`** now prioritizes `state.pressedKeys[code]` as the ground truth.
- **`cleanupSustainPitches`** has been refactored to iterate over an array of pitch/channel objects.
- Sustain pedal logic now consistently uses `midi.sendSustainCC` and properly manages `state.sustainedPitches` as an array.

---
