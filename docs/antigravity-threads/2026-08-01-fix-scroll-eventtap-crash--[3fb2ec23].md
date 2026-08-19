---
title: "Fix Scroll Eventtap Crash"
date: "2026-08-01"
conversation_id: "3fb2ec23-9626-4090-bb30-95c79bb0b370"
source: "antigravity"
---

# Fix Scroll Eventtap Crash

## User

Fix crash in scroll eventtap!
The exponentiation math `absDelta ^ (accel - 1.0)` was causing NaN or Inf values when `accel` was high or negative or when trackpad reported large point deltas, causing Hammerspoon to crash during scroll!

Fix:
Replace complex exponential power math with a safe, simple linear sensitivity + threshold-boosted velocity clamp:

```lua
    local deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventDeltaAxis1) or 0
    if deltaY == 0 then
      deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventPointDeltaAxis1) or 0
    end

    local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
    local sens = state.scrollSensitivity or 0.15
    local accel = state.scrollAcceleration or 1.0

    -- Clamp deltaY to prevent extreme spikes
    deltaY = math.max(-100, math.min(100, deltaY))

    -- Safe acceleration factor
    local scaledDelta = deltaY * sens * accel

    if phase ~= 0 then
      local decay = state.scrollFrictionalDecay or 0.85
      if decay == 0 then
        return true
      end
      scaledDelta = scaledDelta * decay
    end

    deltaY = scaledDelta
```

Modify `src/init.lua` with this safe, bulletproof code and execute `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

---

## Assistant

Created At: 2026-08-01T12:58:07-06:00
Completed At: 2026-08-01T12:58:07-06:00
{"name":".DS_Store","sizeBytes":"8196"}
{"name":".claude","isDir":true}
{"name":".devtool","isDir":true}
{"name":".git","isDir":true}
{"name":".gitignore","sizeBytes":"324"}
{"name":"AG_CONTEXT.md","sizeBytes":"1983"}
{"name":"DEVELOPMENT_JOURNAL.md","sizeBytes":"14031"}
{"name":"FEATURES.md","sizeBytes":"7352"}
{"name":"README.md","sizeBytes":"860"}
{"name":"agent-logs","isDir":true}
{"name":"bin","isDir":true}
{"name":"dist","isDir":true}
{"name":"fix_css.py","sizeBytes":"1814"}
{"name":"fix_css2.py","sizeBytes":"870"}
{"name":"install.sh","sizeBytes":"263"}
{"name":"layouts","isDir":true}
{"name":"node_modules","isDir":true}
{"name":"plans","isDir":true}
{"name":"qwerty_midi.lua","sizeBytes":"295003"}
{"name":"src","isDir":true}
{"name":"src-tauri","isDir":true}
{"name":"test_logic_ui.scpt","sizeBytes":"2306"}
{"name":"test_profile.lua","sizeBytes":"297"}
{"name":"test_set_bpm.lua","sizeBytes":"1932"}
{"name":"tmp","isDir":true}
{"name":"tmp_test_applescript.scpt","sizeBytes":"331"}
{"name":"vite.config.js","sizeBytes":"213"}

Summary: This directory contains 12 subdirectories and 15 files.

Created At: 2026-08-01T12:58:08-06:00
Completed At: 2026-08-01T12:58:08-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"32581"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"12045"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"17244"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T12:58:08-06:00
Completed At: 2026-08-01T12:58:08-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua","LineNumber":64,"LineContent":"    local deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventDeltaAxis1) or 0"}

Created At: 2026-08-01T12:58:09-06:00
Completed At: 2026-08-01T12:58:09-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 334
Total Bytes: 12045
Showing lines 60 to 100
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
60: _G.activeWatchers.midiScrollTap = hs.eventtap.new({ hs.eventtap.event.types.scrollWheel }, function(event)
61:   if not state.midiActive then return false end
62: 
63:   local ok, result = xpcall(function()
64:     local deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventDeltaAxis1) or 0
65:     if deltaY == 0 then
66:       deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventPointDeltaAxis1) or 0
67:     end
68: 
69:     -- Scroll handling
70:     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
71:     local sens = state.scrollSensitivity or 0.15
72:     local accel = state.scrollAcceleration or 1.0
73: 
74:     -- Apply non-linear acceleration curve based on gesture magnitude
75:     local absDelta = math.abs(deltaY)
76:     local accelFactor = (absDelta > 1) and (absDelta ^ (accel - 1.0)) or 1.0
77:     local scaledDelta = deltaY * sens * accelFactor
78: 
79:     if phase ~= 0 then
80:       local decay = state.scrollFrictionalDecay or 0.85
81:       if decay == 0 then
82:         return true
83:       end
84:       scaledDelta = scaledDelta * decay
85:     end
86: 
87:     deltaY = scaledDelta
88: 
89:     -- Allow native webview scrolling only when cursor is specifically over a scrollable pane in the HUD
90:     if _G.activeWatchers.isHoveringScrollable then
91:       return false
92:     end
93: 
94:     if deltaY ~= 0 then
95:       if state.shiftHeld then
96:         local avgVol = (state.topRowVolume + state.bottomRowVolume) / 2
97:         _G.activeWatchers.volAccumulator = _G.activeWatchers.volAccumulator or avgVol
98:         -- Adjusting volume with new scroll mechanics
99:         _G.activeWatchers.volAccumulator = math.max(0, math.min(127, _G.activeWatchers.volAccumulator - deltaY))
100:         local newVol = math.floor(_G.activeWatchers.volAccumulator + 0.5)
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-01T12:58:12-06:00
Completed At: 2026-08-01T12:58:12-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -71,10 +71,11 @@
     local sens = state.scrollSensitivity or 0.15
     local accel = state.scrollAcceleration or 1.0
 
-    -- Apply non-linear acceleration curve based on gesture magnitude
-    local absDelta = math.abs(deltaY)
-    local accelFactor = (absDelta > 1) and (absDelta ^ (accel - 1.0)) or 1.0
-    local scaledDelta = deltaY * sens * accelFactor
+    -- Clamp deltaY to prevent extreme spikes
+    deltaY = math.max(-100, math.min(100, deltaY))
+
+    -- Safe acceleration factor
+    local scaledDelta = deltaY * sens * accel
 
     if phase ~= 0 then
       local decay = state.scrollFrictionalDecay or 0.85
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:58:13-06:00
Completed At: 2026-08-01T12:58:13-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T12:58:14-06:00
Completed At: 2026-08-01T12:58:14-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

The scroll eventtap crash in `src/init.lua` has been resolved by replacing the exponentiation logic with a safe linear sensitivity and velocity clamp. The changes were applied, and `bin/bundle_and_reload.sh` was executed successfully.

---
