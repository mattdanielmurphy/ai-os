---
title: "Fix Arpeggiator Chord Logic"
date: "2026-08-01"
conversation_id: "60fe2b9b-1e64-46fd-a2fe-5b854d1c07a0"
source: "antigravity"
---

# Fix Arpeggiator Chord Logic

## User

Edit /Users/matt/projects/qwerty-midi-hammerspoon/src/arpeggiator.lua.

Replace the `updateLatchedArpNotes` function (lines 338-347) with a version that correctly handles chord-mode compound keys.

The bug: when chord mode was used to build the arp latch (e.g. pressing one key that generates 3 entries like `"45_60"`, `"45_64"`, `"45_67"`), the current function calls `getTransposedPitch` for all three entries using the same base keycode. This sets all three to the same root pitch, collapsing the chord to a single note.

The fix: detect if any compound keys exist (strings containing `_`). If so, do a full chord rebuild using `getChordPitches` (two-pass, safe). If not, do the original simple single-pitch update.

TargetContent (StartLine=338, EndLine=347):
```lua
local function updateLatchedArpNotes()
  if not state.arpEnabled or next(state.arpHeldNotes) == nil then return end
  for code, _ in pairs(state.arpHeldNotes) do
    local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
    local noteKey = rawCode and config.getNoteKey(rawCode)
    if noteKey then
      state.arpHeldNotes[code] = transposer.getTransposedPitch(noteKey.baseNote, noteKey.isTop)
    end
  end
end
```

ReplacementContent:
```lua
local function updateLatchedArpNotes()
  if not state.arpEnabled or next(state.arpHeldNotes) == nil then return end

  -- Detect if any chord-mode compound keys exist (e.g. "45_60", "45_64", "45_67").
  -- Simple single-note entries are plain integers or strings without "_".
  local hasCompoundKeys = false
  for code, _ in pairs(state.arpHeldNotes) do
    if type(code) == "string" and code:find("_", 1, true) then
      hasCompoundKeys = true
      break
    end
  end

  if hasCompoundKeys then
    -- Chord mode: rebuild all compound entries with fresh chord pitches for the new transposition.
    -- Must be two-pass to avoid modifying the table while iterating.
    local uniqueBaseCodes = {}
    local keysToRemove = {}
    for code, _ in pairs(state.arpHeldNotes) do
      local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
      if rawCode then
        uniqueBaseCodes[rawCode] = true
        table.insert(keysToRemove, code)
      end
    end
    for _, code in ipairs(keysToRemove) do
      state.arpHeldNotes[code] = nil
    end
    for rawCode, _ in pairs(uniqueBaseCodes) do
      local noteKey = config.getNoteKey(rawCode)
      if noteKey then
        local newPitches = transposer.getChordPitches(noteKey.baseNote, noteKey.isTop)
        for _, p in ipairs(newPitches) do
          state.arpHeldNotes[tostring(rawCode) .. "_" .. tostring(p)] = p
        end
      end
    end
  else
    -- Simple single-note mode: just update each pitch value in place.
    for code, _ in pairs(state.arpHeldNotes) do
      local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
      local noteKey = rawCode and config.getNoteKey(rawCode)
      if noteKey then
        state.arpHeldNotes[code] = transposer.getTransposedPitch(noteKey.baseNote, noteKey.isTop)
      end
    end
  end
end
```

Report when done.

---

## Assistant

Created At: 2026-08-01T00:39:46-06:00
Completed At: 2026-08-01T00:39:46-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/arpeggiator.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -337,11 +337,49 @@
 
 local function updateLatchedArpNotes()
   if not state.arpEnabled or next(state.arpHeldNotes) == nil then return end
-  for code, _ in pairs(state.arpHeldNotes) do
-    local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
-    local noteKey = rawCode and config.getNoteKey(rawCode)
-    if noteKey then
-      state.arpHeldNotes[code] = transposer.getTransposedPitch(noteKey.baseNote, noteKey.isTop)
+
+  -- Detect if any chord-mode compound keys exist (e.g. "45_60", "45_64", "45_67").
+  -- Simple single-note entries are plain integers or strings without "_".
+  local hasCompoundKeys = false
+  for code, _ in pairs(state.arpHeldNotes) do
+    if type(code) == "string" and code:find("_", 1, true) then
+      hasCompoundKeys = true
+      break
+    end
+  end
+
+  if hasCompoundKeys then
+    -- Chord mode: rebuild all compound entries with fresh chord pitches for the new transposition.
+    -- Must be two-pass to avoid modifying the table while iterating.
+    local uniqueBaseCodes = {}
+    local keysToRemove = {}
+    for code, _ in pairs(state.arpHeldNotes) do
+      local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
+      if rawCode then
+        uniqueBaseCodes[rawCode] = true
+        table.insert(keysToRemove, code)
+      end
+    end
+    for _, code in ipairs(keysToRemove) do
+      state.arpHeldNotes[code] = nil
+    end
+    for rawCode, _ in pairs(uniqueBaseCodes) do
+      local noteKey = config.getNoteKey(rawCode)
+      if noteKey then
+        local newPitches = transposer.getChordPitches(noteKey.baseNote, noteKey.isTop)
+        for _, p in ipairs(newPitches) do
+          state.arpHeldNotes[tostring(rawCode) .. "_" .. tostring(p)] = p
+        end
+      end
+    end
+  else
+    -- Simple single-note mode: just update each pitch value in place.
+    for code, _ in pairs(state.arpHeldNotes) do
+      local rawCode = type(code) == "string" and tonumber(code:match("^(%d+)")) or tonumber(code)
+      local noteKey = rawCode and config.getNoteKey(rawCode)
+      if noteKey then
+        state.arpHeldNotes[code] = transposer.getTransposedPitch(noteKey.baseNote, noteKey.isTop)
+      end
     end
   end
 end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T00:39:47-06:00
Completed At: 2026-08-01T00:39:47-06:00
Message sent to "5e25d519-6c76-4c04-9b6a-10e28871245e".

The file `/Users/matt/projects/qwerty-midi-hammerspoon/src/arpeggiator.lua` has been updated. The `updateLatchedArpNotes` function now correctly handles chord-mode compound keys by performing a two-pass chord rebuild when necessary, while maintaining original functionality for single-note entries.

---
