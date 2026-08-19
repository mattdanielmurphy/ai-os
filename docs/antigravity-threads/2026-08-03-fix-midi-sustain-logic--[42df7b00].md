---
title: "Fix Midi Sustain Logic"
date: "2026-08-03"
conversation_id: "42df7b00-c394-4513-bdf5-a80783650043"
source: "antigravity"
---

# Fix Midi Sustain Logic

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua around line 1171-1188, fix cleanupSustainPitches() so that it checks kInfo.pitches (a table of pitches) when checking if a pitch is currently physically held down in state.pressedKeys.

Change lines 1172-1188 in /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua from:
```lua
  local function cleanupSustainPitches()
    if state.sustainedPitches then
      for pitch, item in pairs(state.sustainedPitches) do
        local channel = type(item) == "table" and item.channel or 0
        local isCurrentlyHeld = false
        for _, kInfo in pairs(state.pressedKeys) do
          if type(kInfo) == "table" and kInfo.pitch == pitch then
            isCurrentlyHeld = true
            break
          end
        end
        if not isCurrentlyHeld then
          midi.sendMidiNote("noteOff", pitch, 0, channel)
        end
      end
      state.sustainedPitches = {}
    end
  end
```

To:
```lua
  local function cleanupSustainPitches()
    if state.sustainedPitches then
      for pitch, item in pairs(state.sustainedPitches) do
        local channel = type(item) == "table" and item.channel or 0
        local isCurrentlyHeld = false
        for _, kInfo in pairs(state.pressedKeys) do
          if type(kInfo) == "table" then
            local pList = kInfo.pitches or { kInfo.pitch }
            for _, p in ipairs(pList) do
              if p == pitch then
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
      state.sustainedPitches = {}
    end
  end
```
Also edit /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua line 633-641 where retroactive sustain is added when sustain key is pressed, so it handles `keyInfo.pitches`:
From:
```lua
    -- Retroactively sustain all non-arp notes currently being physically held down
    for code, keyInfo in pairs(state.pressedKeys) do
      if type(keyInfo) == "table" then
        keyInfo.isSustainedNote = true
        if not keyInfo.isArpNote and keyInfo.pitch then
          state.sustainedPitches = state.sustainedPitches or {}
          state.sustainedPitches[keyInfo.pitch] = true
        end
      end
    end
```
To:
```lua
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
Apply these edits using replace_file_content or multi_replace_file_content.

---

## Assistant

Created At: 2026-08-02T20:57:09-06:00
Completed At: 2026-08-02T20:57:16-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -633,9 +633,15 @@
     for code, keyInfo in pairs(state.pressedKeys) do
       if type(keyInfo) == "table" then
         keyInfo.isSustainedNote = true
-        if not keyInfo.isArpNote and keyInfo.pitch then
-          state.sustainedPitches = state.sustainedPitches or {}
-          state.sustainedPitches[keyInfo.pitch] = true
+        if not keyInfo.isArpNote then
+          local pitches = keyInfo.pitches or { keyInfo.pitch }
+          local ch = keyInfo.channel or 0
+          for _, p in ipairs(pitches) do
+            if p then
+              state.sustainedPitches = state.sustainedPitches or {}
+              state.sustainedPitches[p] = { channel = ch }
+            end
+          end
         end
       end
     end
@@ -1170,16 +1170,23 @@
 
   local function cleanupSustainPitches()
     if state.sustainedPitches then
-      for pitch in pairs(state.sustainedPitches) do
+      for pitch, item in pairs(state.sustainedPitches) do
+        local channel = type(item) == "table" and item.channel or 0
         local isCurrentlyHeld = false
         for _, kInfo in pairs(state.pressedKeys) do
-          if type(kInfo) == "table" and kInfo.pitch == pitch then
-            isCurrentlyHeld = true
-            break
+          if type(kInfo) == "table" then
+            local pList = kInfo.pitches or { kInfo.pitch }
+            for _, p in ipairs(pList) do
+              if p == pitch then
+                isCurrentlyHeld = true
+                break
+              end
+            end
+            if isCurrentlyHeld then break end
           end
         end
         if not isCurrentlyHeld then
-          midi.sendMidiNote("noteOff", pitch, 0)
+          midi.sendMidiNote("noteOff", pitch, 0, channel)
         end
       end
       state.sustainedPitches = {}
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-02T20:57:17-06:00
Completed At: 2026-08-02T20:57:17-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

The updates to `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` have been completed successfully. The sustain logic now correctly handles `keyInfo.pitches` in both the retroactive sustain function and `cleanupSustainPitches`.

---
