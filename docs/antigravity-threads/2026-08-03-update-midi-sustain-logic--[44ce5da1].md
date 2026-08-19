---
title: "Update MIDI Sustain Logic"
date: "2026-08-03"
conversation_id: "44ce5da1-b946-4cf8-b615-1c8037462a74"
source: "antigravity"
---

# Update MIDI Sustain Logic

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua, update `handleKeyUp` for `ctrlKey` (around lines 1216-1245) so that momentary hold duration releases sustain cleanly.

Specifically:
1. When `holdDuration > 0.25`:
   - It restores the pre-press snapshot (`applyStateSnapshot(state.controlKeyDownSnapshots[code])`).
   - If `wasSustain` was true and `state.sustainActive` is now false, OR if `act == "sustain"`, ensure `midi.sendMidiCC(64, 0)` is sent and `cleanupSustainPitches()` is called.
   - Dispatches `hud.updateWebviewHud(spot)` to update the HUD indicator showing `SUSTAIN OFF`.

2. When `act == "sustain"` on tap (`holdDuration <= 0.25`):
   - Toggle logic: if `state.sustainWasActiveOnPress` was true, set `state.sustainActive = false`, send `midi.sendMidiCC(64, 0)`, and call `cleanupSustainPitches()`. If false, set `state.sustainActive = true` and send `midi.sendMidiCC(64, 127)`.

Replace lines 1216 to 1253 in /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua:
```lua
    local holdDuration = state.controlKeyDownTime and state.controlKeyDownTime[code] and (hs.timer.secondsSinceEpoch() - state.controlKeyDownTime[code]) or 0
    if holdDuration > 0.25 and not shouldRepeat(act) and act ~= "bpmEdit" then
      if state.controlKeyDownSnapshots and state.controlKeyDownSnapshots[code] then
        local wasSustain = state.sustainActive
        applyStateSnapshot(state.controlKeyDownSnapshots[code])
        if wasSustain and not state.sustainActive then
          midi.sendMidiCC(64, 0)
          cleanupSustainPitches()
        elseif not wasSustain and state.sustainActive then
          midi.sendMidiCC(64, 127)
        end
        hud.updateWebviewHud()
        return true
      end
    end

    if act == "sustain" then
      if state.sustainWasActiveOnPress then
        state.sustainActive = false
        midi.sendMidiCC(64, 0)
      else
        state.sustainActive = true
        midi.sendMidiCC(64, 127)
      end

      if not state.sustainActive then
        midi.sendMidiCC
<truncated 270 bytes>

        targetId = "key-48",
        color = state.sustainActive and "#d4a359" or "#b5aba0"
      }
      hud.updateWebviewHud(spot)
```

With:
```lua
    local holdDuration = state.controlKeyDownTime and state.controlKeyDownTime[code] and (hs.timer.secondsSinceEpoch() - state.controlKeyDownTime[code]) or 0
    if holdDuration > 0.25 and not shouldRepeat(act) and act ~= "bpmEdit" then
      if state.controlKeyDownSnapshots and state.controlKeyDownSnapshots[code] then
        local wasSustain = state.sustainActive
        applyStateSnapshot(state.controlKeyDownSnapshots[code])
        if (wasSustain or act == "sustain") and not state.sustainActive then
          midi.sendMidiCC(64, 0)
          cleanupSustainPitches()
        elseif not wasSustain and state.sustainActive then
          midi.sendMidiCC(64, 127)
        end
        local spot = act == "sustain" and {
          title = "SUSTAIN (CC #64)",
          value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
          subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
          targetId = "key-48",
          color = state.sustainActive and "#d4a359" or "#b5aba0"
        } or nil
        hud.updateWebviewHud(spot)
        return true
      end
    end

    if act == "sustain" then
      if state.sustainWasActiveOnPress then
        state.sustainActive = false
        midi.sendMidiCC(64, 0)
        cleanupSustainPitches()
      else
        state.sustainActive = true
        midi.sendMidiCC(64, 127)
      end

      local spot = {
        title = "SUSTAIN (CC #64)",
        value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
        subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
        targetId = "key-48",
        color = state.sustainActive and "#d4a359" or "#b5aba0"
      }
      hud.updateWebviewHud(spot)
```

Apply this edit using replace_file_content.

---

## Assistant

Created At: 2026-08-02T21:09:28-06:00
Completed At: 2026-08-02T21:09:28-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1218,7 +1218,7 @@
       if state.controlKeyDownSnapshots and state.controlKeyDownSnapshots[code] then
         local wasSustain = state.sustainActive
         applyStateSnapshot(state.controlKeyDownSnapshots[code])
-        if wasSustain and not state.sustainActive then
+        if (wasSustain or act == "sustain") and not state.sustainActive then
           midi.sendMidiCC(64, 0)
           cleanupSustainPitches()
         elseif not wasSustain and state.sustainActive then
@@ -1225,5 +1225,12 @@
         end
-        hud.updateWebviewHud()
+        local spot = act == "sustain" and {
+          title = "SUSTAIN (CC #64)",
+          value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
+          subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
+          targetId = "key-48",
+          color = state.sustainActive and "#d4a359" or "#b5aba0"
+        } or nil
+        hud.updateWebviewHud(spot)
         return true
       end
     end
@@ -1231,6 +1231,7 @@
       if state.sustainWasActiveOnPress then
         state.sustainActive = false
         midi.sendMidiCC(64, 0)
+        cleanupSustainPitches()
       else
         state.sustainActive = true
         midi.sendMidiCC(64, 127)
@@ -1237,9 +1237,4 @@
 
-      if not state.sustainActive then
-        midi.sendMidiCC(64, 0)
-        cleanupSustainPitches()
-      end
-
       local spot = {
         title = "SUSTAIN (CC #64)",
         value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-02T21:09:29-06:00
Completed At: 2026-08-02T21:09:29-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The requested updates to `handleKeyUp` in `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` have been applied.

- **Momentary Hold (`holdDuration > 0.25`)**: The logic now cleans up sustain properly if the action was `"sustain"` or if sustain was active, and provides visual feedback to the HUD.
- **Tap (`holdDuration <= 0.25`)**: The sustain toggle logic has been corrected to handle the state transition and cleanup accurately.

I have notified the parent agent.

---
