---
title: "Update Sustain Logic Code"
date: "2026-08-03"
conversation_id: "ed8f5330-6502-465b-a65b-93bd241ddb26"
source: "antigravity"
---

# Update Sustain Logic Code

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua, update `executeControlAction` for `sustain` around line 627 so that pressing/holding `Tab` stores `state.sustainWasActiveOnPress = state.sustainActive` BEFORE overriding `state.sustainActive = true`. When `sustainWasActiveOnPress` was `false` (sustain was disabled prior to press), `state.sustainActive` remains `false` during the hold so notes played while holding `Tab` are NOT tagged as sustained notes (`isSustainedNote = false`).

Specifically, update lines 626 to 646 in /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua:
From:
```lua
  elseif act == "sustain" then
    state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
    state.sustainWasActiveOnPress = state.sustainActive
    state.sustainActive = true
    midi.sendMidiCC(64, 127)

    -- Retroactively sustain all non-arp notes currently being physically held down
    for code, keyInfo in pairs(state.pressedKeys) do
      if type(keyInfo) == "table" then
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

To:
```lua
  elseif act == "sustain" then
    state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
    state.sustainWasActiveOnPress = state.sustainActive
    midi.sendMidiCC(64, 127)

    -- Retroactively sustain all non-arp notes currently being physically held down
    for code, keyInfo in pairs(state.pressedKeys) do
      if type(keyInfo) == "table" then
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

And in `handleKeyUp` for `ctrlKey` when `act == "sustain"` (around lines 1239-1250):
From:
```lua
    if act == "sustain" then
      if state.sustainWasActiveOnPress then
        state.sustainActive = false
        midi.sendMidiCC(64, 0)
        cleanupSustainPitches()
      else
        state.sustainActive = true
        midi.sendMidiCC(64, 127)
      end
```

To:
```lua
    if act == "sustain" then
      if state.sustainWasActiveOnPress then
        state.sustainActive = false
        midi.sendMidiCC(64, 0)
        cleanupSustainPitches()
      else
        state.sustainActive = not state.sustainWasActiveOnPress
        if not state.sustainActive then
          midi.sendMidiCC(64, 0)
          cleanupSustainPitches()
        else
          midi.sendMidiCC(64, 127)
        end
      end
```

Apply these edits using multi_replace_file_content.

---

## Assistant

Created At: 2026-08-03T01:51:48-06:00
Completed At: 2026-08-03T01:51:48-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -626,7 +626,6 @@
   elseif act == "sustain" then
     state.sustainKeyDownTime = hs.timer.secondsSinceEpoch()
     state.sustainWasActiveOnPress = state.sustainActive
-    state.sustainActive = true
     midi.sendMidiCC(64, 127)
 
     -- Retroactively sustain all non-arp notes currently being physically held down
@@ -1241,8 +1241,13 @@
         midi.sendMidiCC(64, 0)
         cleanupSustainPitches()
       else
-        state.sustainActive = true
-        midi.sendMidiCC(64, 127)
+        state.sustainActive = not state.sustainWasActiveOnPress
+        if not state.sustainActive then
+          midi.sendMidiCC(64, 0)
+          cleanupSustainPitches()
+        else
+          midi.sendMidiCC(64, 127)
+        end
       end
 
       local spot = {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T01:51:49-06:00
Completed At: 2026-08-03T01:51:49-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

OK. I have updated `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` with the requested sustain logic changes. I have also notified the parent agent.

---
