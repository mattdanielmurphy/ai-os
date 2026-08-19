---
title: "Update MIDI KeyUp Failsafe"
date: "2026-08-03"
conversation_id: "00afa909-7153-4846-8a74-93ff39341ba1"
source: "antigravity"
---

# Update MIDI KeyUp Failsafe

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua, update handleKeyUp for noteKey around lines 1143-1166 so that if keyInfo is nil (not present in state.pressedKeys[code]), it executes a failsafe noteOff calculation and updates the single key UI state.

Replace lines 1143 to 1166 in /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua:
```lua
    local keyInfo = state.pressedKeys[code]
    if keyInfo then
      local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
      local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
      local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote

      local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
      if isArpNote then
        for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
      else
        for _, playedPitch in ipairs(pitches) do
          if isSustainedNote and state.sustainActive then
            state.sustainedPitches = state.sustainedPitches or {}
            state.sustainedPitches[playedPitch] = { channel = keyChannel }
          else
            midi.sendMidiNote("noteOff", playedPitch, 0, keyChannel)
          end
        end
      end
      state.pressedKeys[code] = nil
      hud.updateSingleKeyState(code, false, false)
    end
    hud.updateWebviewHud()
    return true
```

With:
```lua
    local keyInfo = state.pressedKeys[code]
    if keyInfo then
      local pitches = type(keyInfo) == "table" and keyInfo.pitches or { keyInfo.pitch }
      local isArpNote = type(keyInfo) == "table" and keyInfo.isArpNote
      local isSustainedNote = type(keyInfo) == "table" and keyInfo.isSustainedNote

      local keyChannel = type(keyInfo) == "table" and keyInfo.channel or 0
      if isArpNote then
        for _, p in ipairs(pitches) do arpeggiator.arpRemoveNote(code .. "_" .. p) end
      else
        for _, playedPitch in ipairs(pitches) do
          if isSustainedNote and state.sustainActive then
            state.sustainedPitches = state.sustainedPitches or {}
            state.sustainedPitches[playedPitch] = { channel = keyChannel }
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
```

Apply this edit using replace_file_content.

---

## Assistant

Created At: 2026-08-02T21:06:53-06:00
Completed At: 2026-08-02T21:06:53-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1160,8 +1160,14 @@
         end
       end
       state.pressedKeys[code] = nil
-      hud.updateSingleKeyState(code, false, false)
-    end
+    else
+      -- Failsafe: keyInfo was missing from state.pressedKeys, calculate pitch & send noteOff directly
+      local isTop = noteKey.isTop
+      local fallbackPitch = transposer.getTransposedPitch(noteKey.baseNote, isTop)
+      local ch = isTop and (state.topRowChannel or 0) or (state.bottomRowChannel or 0)
+      midi.sendMidiNote("noteOff", fallbackPitch, 0, ch)
+    end
+    hud.updateSingleKeyState(code, false, false)
     hud.updateWebviewHud()
     return true
   end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-02T21:06:54-06:00
Completed At: 2026-08-02T21:06:54-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The `handleKeyUp` function in `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` has been updated as requested. If a key is not found in `state.pressedKeys`, it now performs a fallback `noteOff` calculation using `noteKey.baseNote` and `transposer.getTransposedPitch`, followed by the UI state update.

---
