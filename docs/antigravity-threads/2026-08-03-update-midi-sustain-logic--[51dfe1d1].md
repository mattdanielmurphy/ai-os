---
title: "Update MIDI Sustain Logic"
date: "2026-08-03"
conversation_id: "51dfe1d1-cc83-4c04-9a50-c804df4f0908"
source: "antigravity"
---

# Update MIDI Sustain Logic

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua, update `executeControlAction` for `sustain` (lines 626-646) and `handleKeyUp` for `act == "sustain"` (lines 1251-1256):

1. `executeControlAction`:
```lua
  elseif act == "sustain" then
    state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
    state.sustainWasActiveOnPress = state.sustainActive
    if state.sustainActive then
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
    end
```

2. `handleKeyUp` for `act == "sustain"`:
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

Apply these edits using multi_replace_file_content.

---

## Assistant

Created At: 2026-08-03T01:59:21-06:00
Completed At: 2026-08-03T01:59:21-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1299
Total Bytes: 45376
Showing lines 620 to 1260
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
620:       value = math.floor(state.zoomLevel * 100) .. "%",
621:       subtext = "Scale Factor",
622:       targetId = "header",
623:       color = "#d4a359"
624:     }
625:     hud.updateWebviewHud(spot)
626:   elseif act == "sustain" then
627:     state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
628:     state.sustainWasActiveOnPress = state.sustainActive
629:     midi.sendMidiCC(64, 127)
630: 
631:     -- Retroactively sustain all non-arp notes currently being physically held down
632:     for code, keyInfo in pairs(state.pressedKeys) do
633:       if type(keyInfo) == "table" and not keyInfo.isControl then
634:         keyInfo.isSustainedNote = true
635:         if not keyInfo.isArpNote then
636:           local pitches = keyInfo.pitches or { keyInfo.pitch }
637:           local ch = keyInfo.channel or 0
638:           for _, p in ipairs(pitches) do
639:             if p then
640:               state.sustainedPitches = state.sustainedPitches or {}
641:               state.sustainedPitches[p] = { channel = ch }
642:             end
643:           end
644:         end
645:       end
646:     end
647: 
648:     local spot = {
649:       title = "SUSTAIN (CC #64)",
650:       value = "SUSTAIN ON",
651:       subtext = "Notes held across release",
652:       targetId = code and ("key-" .. code) or "key-48",
653:       color = "#d4a359"
654:     }
655:     hud.updateWebviewHud(spot)
656:   elseif act == "arpToggle" then
657:     arpeggiator.toggleArpPower()
658:   elseif act == "chordToggle" then
659:     state.chordKeyDownTime = hs.timer.secondsSinceE
<truncated 23040 bytes>
1225:     hud.updateSingleKeyState(code, false, false)
1226:     local act = state.shiftHeld and ctrlKey.shiftAction or ctrlKey.action
1227:     
1228:     local holdDuration = state.controlKeyDownTime and state.controlKeyDownTime[code] and (hs.timer.secondsSinceEpoch() - state.controlKeyDownTime[code]) or 0
1229:     if holdDuration > 0.25 and not shouldRepeat(act) and act ~= "bpmEdit" then
1230:       if state.controlKeyDownSnapshots and state.controlKeyDownSnapshots[code] then
1231:         local wasSustain = state.sustainActive
1232:         applyStateSnapshot(state.controlKeyDownSnapshots[code])
1233:         if (wasSustain or act == "sustain") and not state.sustainActive then
1234:           midi.sendMidiCC(64, 0)
1235:           cleanupSustainPitches()
1236:         elseif not wasSustain and state.sustainActive then
1237:           midi.sendMidiCC(64, 127)
1238:         end
1239:         local spot = act == "sustain" and {
1240:           title = "SUSTAIN (CC #64)",
1241:           value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
1242:           subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
1243:           targetId = "key-48",
1244:           color = state.sustainActive and "#d4a359" or "#b5aba0"
1245:         } or nil
1246:         hud.updateWebviewHud(spot)
1247:         return true
1248:       end
1249:     end
1250: 
1251:     if act == "sustain" then
1252:       state.sustainActive = not state.sustainWasActiveOnPress
1253:       midi.sendMidiCC(64, 0)
1254:       cleanupSustainPitches()
1255: 
1256:       local spot = {
1257:         title = "SUSTAIN (CC #64)",
1258:         value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
1259:         subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
1260:         targetId = "key-48",
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-03T01:59:24-06:00
Completed At: 2026-08-03T01:59:24-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -626,19 +626,21 @@
   elseif act == "sustain" then
     state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
     state.sustainWasActiveOnPress = state.sustainActive
-    midi.sendMidiCC(64, 127)
-
-    -- Retroactively sustain all non-arp notes currently being physically held down
-    for code, keyInfo in pairs(state.pressedKeys) do
-      if type(keyInfo) == "table" and not keyInfo.isControl then
-        keyInfo.isSustainedNote = true
-        if not keyInfo.isArpNote then
-          local pitches = keyInfo.pitches or { keyInfo.pitch }
-          local ch = keyInfo.channel or 0
-          for _, p in ipairs(pitches) do
-            if p then
-              state.sustainedPitches = state.sustainedPitches or {}
-              state.sustainedPitches[p] = { channel = ch }
+    if state.sustainActive then
+      midi.sendMidiCC(64, 127)
+
+      -- Retroactively sustain all non-arp notes currently being physically held down
+      for code, keyInfo in pairs(state.pressedKeys) do
+        if type(keyInfo) == "table" and not keyInfo.isControl then
+          keyInfo.isSustainedNote = true
+          if not keyInfo.isArpNote then
+            local pitches = keyInfo.pitches or { keyInfo.pitch }
+            local ch = keyInfo.channel or 0
+            for _, p in ipairs(pitches) do
+              if p then
+                state.sustainedPitches = state.sustainedPitches or {}
+                state.sustainedPitches[p] = { channel = ch }
+              end
             end
           end
         end
@@ -1248,15 +1248,30 @@
     end
 
     if act == "sustain" then
-      state.sustainActive = not state.sustainWasActiveOnPress
-      midi.sendMidiCC(64, 0)
-      cleanupSustainPitches()
-
-      local spot = {
-        title = "SUSTAIN (CC #64)",
-        value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
-        subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
-        targetId = "key-48",
+      if state.sustainWasActiveOnPress then
+        state.sustainActive = false
+        midi.sendMidiCC(64, 0)
+        cleanupSustainPitches()
+      else
+        state.sustainActive = true
+        midi.sendMidiCC(64, 127)
+        -- Retroactively sustain all non-arp notes currently being physically held down
+        for c, keyInfo in pairs(state.pressedKeys) do
+          if type(keyInfo) == "table" and not keyInfo.isControl then
+            keyInfo.isSustainedNote = true
+            if not keyInfo.isArpNote then
+              local pitches = keyInfo.pitches or { keyInfo.pitch }
+              local ch = keyInfo.channel or 0
+              for _, p in ipairs(pitches) do
+                if p then
+                  state.sustainedPitches = state.sustainedPitches or {}
+                  state.sustainedPitches[p] = { channel = ch }
+                end
+              end
+            end
+          end
+        end
+      end
         color = state.sustainActive and "#d4a359" or "#b5aba0"
       }
       hud.updateWebviewHud(spot)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T01:59:24-06:00
Completed At: 2026-08-03T01:59:24-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The sustain logic has been updated in `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` as requested.

---
