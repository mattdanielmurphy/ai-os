---
title: "Implement Scroll Configuration Sliders"
date: "2026-08-01"
conversation_id: "a60cb8b6-5a64-4a06-910a-f9f74557c100"
source: "antigravity"
---

# Implement Scroll Configuration Sliders

## User

Add a 3rd distinct slider for `scrollSensitivity` back alongside `scrollAcceleration` and `scrollFrictionalDecay`.

Here is the exact math breakdown for all 3:
- `Base Scroll Sensitivity` (`scrollSensitivity`, default 0.15): Base scaling multiplier for how much 1 tick/pixel of scroll moves the Mod Wheel value (0-127).
- `Scroll Acceleration` (`scrollAcceleration`, default 1.0, range 0.1 to 3.0): Dynamic velocity exponent/multiplier during fast finger movement (`effectiveDelta = (deltaY * sensitivity) * ((abs(deltaY) ^ (accel - 1)))`).
- `Post-Release Coasting` (`scrollFrictionalDecay`, default 0.85, range 0.00 to 0.98): Coasting multiplier during momentum phase (`phase ~= 0`).

Files to update:
1. `src/config.lua`:
   - `scrollSensitivity` (default 0.15)
   - `scrollAcceleration` (default 1.0, range 0.1 - 3.0)
   - `scrollFrictionalDecay` (default 0.85, range 0.0 - 0.98)
   - Update `saveSettings()` to save all 3.

2. `src/init.lua`:
   - Update scroll tap math:
   ```lua
    local deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventDeltaAxis1) or 0
    if deltaY == 0 then
      deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventPointDeltaAxis1) or 0
    end

    local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
    local sens = state.scrollSensitivity or 0.15
    local accel = state.scrollAcceleration or 1.0

    -- Apply non-linear acceleration curve based on gesture magnitude
    local absDelta = math.abs(deltaY)
    local accelFactor = (absDelta > 1) and (absDelta ^ (accel - 1.0)) or 1.0
    local scaledDelta = deltaY * sens * accelFactor

    if phase ~= 0 then
      local decay = state.scrollFrictionalDecay or 0.85
      if decay == 0 then
        return true
      end
      scaledDelta = scaledDelta * decay
    end

    deltaY = scaledDelta
   ```

3. `src/settings_ui.lua`:
   - Add all 3 sliders under "Trackpad / Scroll":
     1. **Mod Wheel Base Sensitivity** (`sensitivitySlider`, 0.02 to 0.50, step 0.01)
     2. **Velocity Acceleration** (`accelerationSlider`, 0.10 to 3.00, step 0.10)
     3. **Post-Release Coasting (Inertia Friction)** (`decaySlider`, 0.00 to 0.98, step 0.01)
   - Wire input handlers & `syncState` for all 3.

4. Run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

---

## Assistant

Created At: 2026-08-01T12:57:14-06:00
Completed At: 2026-08-01T12:57:14-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"32373"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"11819"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"15932"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T12:57:14-06:00
Completed At: 2026-08-01T12:57:14-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua`
Total Lines: 699
Total Bytes: 32373
Showing lines 1 to 699
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local function getSetting(key, default)
2:   local val = hs.settings.get("qwertyMidi_" .. key)
3:   if val == nil then return default end
4:   if type(default) == "number" then
5:     local num = tonumber(val)
6:     return num ~= nil and num or default
7:   elseif type(default) == "boolean" then
8:     if type(val) == "boolean" then return val end
9:     if type(val) == "number" then return val ~= 0 end
10:     if type(val) == "string" then return val == "true" or val == "1" end
11:   end
12:   return val
13: end
14: 
15: local state = {
16:   midiActive = false,
17:   currentRoot = getSetting("currentRoot", 0),            -- 0 = C (0..11)
18:   currentScaleIdx = getSetting("currentScaleIdx", 1),    -- 1 = Major / Ionian
19:   octaveShift = getSetting("octaveShift", 0),            -- Global Octave offset in semitones (-36 to +36)
20:   topRowOctaveOffset = getSetting("topRowOctaveOffset", 12), -- Independent Top Row Octave Offset
21:   bottomRowOctaveOffset = getSetting("bottomRowOctaveOffset", 0), -- Independent Bottom Row Octave Offset
22:   transposeShift = getSetting("transposeShift", 0),     -- Transpose offset in scale degrees (-12 to +12)
23:   sustainActive = false,      -- Sustain toggle state (CC64)
24:   sustainKeyDownTime = 0,     -- Timestamp when sustain key was pressed down
25:   sustainWasActiveOnPress = false,
26:   arpLatchActive = getSetting("arpLatchActive", false),  -- Arpeggiator Latch mode
27:   shiftHeld = false,          -- Shift key active state
28:   zoomLevel = getSetting("zoomLevel", 1.0),
29:   BASE_HUD_SCALE = 1.4,
30: 
31:   --
<truncated 32206 bytes>
d
654: 
655: local function getActiveControlKeysMap()
656:   if _cachedActiveControlKeysMap then return _cachedActiveControlKeysMap end
657:   local map = {}
658:   for code, k in pairs(homeRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
659:   for code, k in pairs(upperRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
660:   for code, k in pairs(lowerRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
661:   for code, k in pairs(numberRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
662:   _cachedActiveControlKeysMap = map
663:   return map
664: end
665: 
666: 
667: return {
668:   state = state,
669:   saveSettings = saveSettings,
670:   SCALES = SCALES,
671:   NOTE_NAMES = NOTE_NAMES,
672:   WHITE_KEY_INDEX = WHITE_KEY_INDEX,
673:   ACTION_CATALOG = ACTION_CATALOG,
674:   defaultNumberRowControls = defaultNumberRowControls,
675:   defaultUpperRowKeys = defaultUpperRowKeys,
676:   defaultLowerRowKeys = defaultLowerRowKeys,
677:   defaultHomeRowControls = defaultHomeRowControls,
678:   numberRowControls = numberRowControls,
679:   upperRowKeys = upperRowKeys,
680:   lowerRowKeys = lowerRowKeys,
681:   homeRowControls = homeRowControls,
682:   applyCustomLayout = applyCustomLayout,
683:   saveCustomLayout = saveCustomLayout,
684:   selectPreset = selectPreset,
685:   savePreset = savePreset,
686:   renamePreset = renamePreset,
687:   deletePreset = deletePreset,
688:   duplicatePreset = duplicatePreset,
689:   getPresetsList = getPresetsList,
690:   resetLayout = resetLayout,
691:   updateKeyMapping = updateKeyMapping,
692:   getLayoutConfig = getLayoutConfig,
693:   getNoteKey = getNoteKey,
694:   getControlKey = getControlKey,
695:   getNumberControlKey = getNumberControlKey,
696:   getActiveNoteKeysMap = getActiveNoteKeysMap,
697:   getActiveControlKeysMap = getActiveControlKeysMap
698: }
699: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:57:15-06:00
Completed At: 2026-08-01T12:57:15-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 328
Total Bytes: 11819
Showing lines 1 to 328
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
<truncated 9795 bytes>
:%M:%S") .. " [WATCHDOG]: " .. msg .. "\n"); f:close() end
275:         
276:         pcall(function()
277:           local h = hud.reloadMidiWebview()
278:           if h then h:show() end
279:           hs.alert.show("UI Auto-Recovered by Watchdog", 2.0)
280:         end)
281:       end
282:     end
283:   end
284: end)
285: 
286: _G.activeWatchers.midiToggleHotkey = hs.hotkey.bind({ "cmd", "alt" }, "M", function()
287:   _G.toggleMidiMode()
288: end)
289: 
290: _G.activeWatchers.midiRefreshHotkey = hs.hotkey.bind({ "cmd", "alt" }, "R", function()
291:   hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5)
292:   hs.notify.new({ title = "QWERTY MIDI", informativeText = "Executing full Hammerspoon hard reload..." }):send()
293:   hs.timer.doAfter(0.1, function() hs.reload() end)
294: end)
295: 
296: if _G.activeWatchers.settingsHotkey then
297:   _G.activeWatchers.settingsHotkey:delete()
298:   _G.activeWatchers.settingsHotkey = nil
299: end
300: 
301: profileLog("Before panicAllChannels")
302: midi.panicAllChannels()
303: 
304: -- Auto-reopen window if it was open when the last reload occurred
305: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
306: if wasOpen then
307:   profileLog("Auto-reopening controller window (was open before reload)")
308:   hs.timer.doAfter(0.3, function()
309:     local ok, err = pcall(function()
310:       _G.toggleMidiMode(true)
311:     end)
312:     if not ok then
313:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
314:     end
315:   end)
316: end
317: 
318: _G.pingController = function() return hud.pingController() end
319: _G.dumpMidiLogs = function() return hud.dumpMidiLogs() end
320: _G.hardResetController = function() hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5); hs.reload() end
321: 
322: profileLog("Init complete!")
323: 
324: return {
325:   toggleMidiMode = _G.toggleMidiMode,
326:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
327: }
328: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:57:16-06:00
Completed At: 2026-08-01T12:57:16-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua`
Total Lines: 524
Total Bytes: 15932
Showing lines 1 to 524
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local hsWebview = require("hs.webview")
2: local hsUsercontent = require("hs.webview.usercontent")
3: local config = require("config")
4: local state = config.state
5: 
6: local settingsWebview = nil
7: 
8: local function generateSettingsHTML()
9:   local bpmStep        = state.bpmStepSize or 10
10:   local logicSync      = state.logicSyncEnabled
11:   local gate           = state.arpGatePercent or 80
12:   local zoom           = state.zoomLevel or 1.0
13:   local acceleration  = state.scrollAcceleration or 0.15
14:   local decay         = state.scrollFrictionalDecay or 0.85
15: 
16:   -- Build BPM step selected states
17:   local bpmSel = { ["1"]="", ["5"]="", ["10"]="", ["25"]="" }
18:   bpmSel[tostring(bpmStep)] = "selected"
19: 
20:   -- Build zoom selected states
21:   local zoomSel = {}
22:   for _, v in ipairs({0.8, 1.0, 1.2, 1.4}) do
23:     zoomSel[tostring(v)] = math.abs(zoom - v) < 0.05 and "selected" or ""
24:   end
25: 
26:   -- Format floats nicely for slider defaults
27:   local accFmt     = string.format("%.2f", acceleration)
28:   local decayFmt   = string.format("%.2f", decay)
29: 
30:   return string.format([[
31: <!DOCTYPE html>
32: <html>
33: <head>
34:   <meta charset="utf-8"/>
35:   <style>
36:     * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
37: 
38:     body {
39:       font-family: Georgia, serif;
40:       background: #18140f;
41:       color: #e2d5c0;
42:       font-size: 15px;
43:       overflow: hidden;
44:       border-radius: 16px;
45:     }
46: 
47:     #panel {
48:    
<truncated 14895 bytes>
or(screen.y + (screen.h - h) / 2)
470: 
471:   local wv = hsWebview.new({ x = x, y = y, w = w, h = h }, { developerExtrasEnabled = true }, uc)
472:   wv:windowTitle("QWERTY MIDI Settings")
473:   -- Borderless floating panel that sits above the HUD webview
474:   wv:windowStyle({ "borderless", "nonactivating" })
475:   wv:level(hs.drawing.windowLevels.floating + 1)
476:   wv:allowTextEntry(true)
477:   wv:html(generateSettingsHTML())
478: 
479:   _G.activeWatchers.settingsWebview = wv
480:   return wv
481: end
482: 
483: local function syncStateToWebview()
484:   if not _G.activeWatchers.settingsWebview then return end
485:   local s = {
486:     bpmStepSize = state.bpmStepSize or 10,
487:     logicSyncEnabled = state.logicSyncEnabled,
488:     arpGatePercent = state.arpGatePercent or 80,
489:     zoomLevel = state.zoomLevel or 1.0,
490:     scrollAcceleration = state.scrollAcceleration or 0.15,
491:     scrollFrictionalDecay = state.scrollFrictionalDecay or 0.85
492:   }
493:   local jsonStr = hs.json.encode(s)
494:   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
495: end
496: 
497: local function toggleSettingsWindow()
498:   local wv = createSettingsWebview()
499: 
500:   if wv:isVisible() then
501:     wv:hide()
502:   else
503:     local screen = hs.screen.mainScreen():frame()
504:     local w, h = 528, 612
505:     local x = math.floor(screen.x + (screen.w - w) / 2)
506:     local y = math.floor(screen.y + (screen.h - h) / 2)
507:     wv:frame({ x = x, y = y, w = w, h = h })
508: 
509:     syncStateToWebview()
510:     wv:show()
511:   end
512: end
513: 
514: -- Cleanup old instance on reload and pre-warm new settings webview
515: if _G.activeWatchers.settingsWebview then
516:   _G.activeWatchers.settingsWebview:delete()
517:   _G.activeWatchers.settingsWebview = nil
518: end
519: createSettingsWebview()
520: 
521: return {
522:   toggleSettingsWindow = toggleSettingsWindow
523: }
524: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:57:18-06:00
Completed At: 2026-08-01T12:57:18-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -88,7 +88,8 @@
   logicSyncTimer = nil,
 
   -- Scroll / Trackpad
-  scrollAcceleration    = getSetting("scrollAcceleration", 0.15),
+  scrollSensitivity     = getSetting("scrollSensitivity", 0.15),
+  scrollAcceleration    = getSetting("scrollAcceleration", 1.0),
   scrollFrictionalDecay = getSetting("scrollFrictionalDecay", 0.85),
 
   DIGIT_KEYCODES = {
@@ -129,7 +129,8 @@
   state.arpGatePercent = tonumber(state.arpGatePercent) or 80.0
   state.arpBpm = tonumber(state.arpBpm) or 120.0
   state.bpmStepSize = tonumber(state.bpmStepSize) or 10
-  state.scrollAcceleration = tonumber(state.scrollAcceleration) or 0.15
+  state.scrollSensitivity = tonumber(state.scrollSensitivity) or 0.15
+  state.scrollAcceleration = tonumber(state.scrollAcceleration) or 1.0
   state.scrollFrictionalDecay = tonumber(state.scrollFrictionalDecay) or 0.85
   state.topRowVolume = tonumber(state.topRowVolume) or 100
   state.bottomRowVolume = tonumber(state.bottomRowVolume) or 100
@@ -152,6 +152,7 @@
   hs.settings.set("qwertyMidi_arpBottomEnabled", state.arpBottomEnabled == true)
   hs.settings.set("qwertyMidi_bpmStepSize", state.bpmStepSize)
   hs.settings.set("qwertyMidi_logicSyncEnabled", state.logicSyncEnabled == true)
+  hs.settings.set("qwertyMidi_scrollSensitivity", state.scrollSensitivity)
   hs.settings.set("qwertyMidi_scrollAcceleration", state.scrollAcceleration)
   hs.settings.set("qwertyMidi_scrollFrictionalDecay", state.scrollFrictionalDecay)
   hs.settings.set("qwertyMidi_topRowVolume", state.topRowVolume)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:57:19-06:00
Completed At: 2026-08-01T12:57:19-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -68,7 +68,13 @@
 
     -- Scroll handling
     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
-    local accel = state.scrollAcceleration or 0.15
+    local sens = state.scrollSensitivity or 0.15
+    local accel = state.scrollAcceleration or 1.0
+
+    -- Apply non-linear acceleration curve based on gesture magnitude
+    local absDelta = math.abs(deltaY)
+    local accelFactor = (absDelta > 1) and (absDelta ^ (accel - 1.0)) or 1.0
+    local scaledDelta = deltaY * sens * accelFactor
 
     if phase ~= 0 then
       local decay = state.scrollFrictionalDecay or 0.85
@@ -75,9 +75,9 @@
-        return true -- block post-release momentum events completely
-      end
-      deltaY = deltaY * accel * decay
-    else
-      deltaY = deltaY * accel
-    end
+        return true
+      end
+      scaledDelta = scaledDelta * decay
+    end
+
+    deltaY = scaledDelta
 
     -- Allow native webview scrolling only when cursor is specifically over a scrollable pane in the HUD
     if _G.activeWatchers.isHoveringScrollable then
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:57:26-06:00
Completed At: 2026-08-01T12:57:26-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,7 +10,8 @@
   local logicSync      = state.logicSyncEnabled
   local gate           = state.arpGatePercent or 80
   local zoom           = state.zoomLevel or 1.0
-  local acceleration  = state.scrollAcceleration or 0.15
+  local sensitivity = state.scrollSensitivity or 0.15
+  local acceleration  = state.scrollAcceleration or 1.0
   local decay         = state.scrollFrictionalDecay or 0.85
 
   -- Build BPM step selected states
@@ -23,6 +23,7 @@
   end
 
   -- Format floats nicely for slider defaults
+  local sensFmt    = string.format("%.2f", sensitivity)
   local accFmt     = string.format("%.2f", acceleration)
   local decayFmt   = string.format("%.2f", decay)
 
@@ -261,11 +261,24 @@
 
       <div class="row">
         <div class="row-label">
-          <strong>Scroll Acceleration</strong>
-          <span>Speed/curve of active scrolling</span>
-        </div>
-        <div class="slider-row">
-          <input type="range" id="accelerationSlider" min="0.01" max="0.50" step="0.01"
+          <strong>Mod Wheel Base Sensitivity</strong>
+          <span>Base scaling multiplier</span>
+        </div>
+        <div class="slider-row">
+          <input type="range" id="sensitivitySlider" min="0.02" max="0.50" step="0.01"
+            value="%s"
+            oninput="onSensitivity(this.value)">
+          <div class="slider-val" id="sensitivityVal">%s</div>
+        </div>
+      </div>
+
+      <div class="row">
+        <div class="row-label">
+          <strong>Velocity Acceleration</strong>
+          <span>Dynamic velocity exponent (0.1-3.0)</span>
+        </div>
+        <div class="slider-row">
+          <input type="range" id="accelerationSlider" min="0.10" m
<truncated 1171 bytes>
ned) {
+      var el = document.getElementById('sensitivitySlider');
+      if (el) el.value = s.scrollSensitivity;
+      var valEl = document.getElementById('sensitivityVal');
+      if (valEl) valEl.textContent = parseFloat(s.scrollSensitivity).toFixed(2);
+    }
     if (s.scrollAcceleration !== undefined) {
       var el = document.getElementById('accelerationSlider');
       if (el) el.value = s.scrollAcceleration;
@@ -396,8 +396,10 @@
 ]],
     -- sensitivity slider
     sensFmt, sensFmt,
+    -- acceleration slider
+    accFmt, accFmt,
     -- momentum slider
-    momentFmt, momentFmt,
+    decayFmt, decayFmt,
     -- bpm step selects
     bpmSel["1"], bpmSel["5"], bpmSel["10"], bpmSel["25"],
     -- logic sync checked
@@ -436,8 +436,12 @@
       local val = tonumber(body.value) or 1.0
       state.zoomLevel = val
       hs.settings.set("qwertyMidi_zoomLevel", val)
-    elseif body.type == "setAcceleration" then
+    elseif body.type == "setSensitivity" then
       local val = tonumber(body.value) or 0.15
+      state.scrollSensitivity = val
+      hs.settings.set("qwertyMidi_scrollSensitivity", val)
+    elseif body.type == "setAcceleration" then
+      local val = tonumber(body.value) or 1.0
       state.scrollAcceleration = val
       hs.settings.set("qwertyMidi_scrollAcceleration", val)
     elseif body.type == "setDecay" then
@@ -479,7 +479,8 @@
     logicSyncEnabled = state.logicSyncEnabled,
     arpGatePercent = state.arpGatePercent or 80,
     zoomLevel = state.zoomLevel or 1.0,
-    scrollAcceleration = state.scrollAcceleration or 0.15,
+    scrollSensitivity = state.scrollSensitivity or 0.15,
+    scrollAcceleration = state.scrollAcceleration or 1.0,
     scrollFrictionalDecay = state.scrollFrictionalDecay or 0.85
   }
   local jsonStr = hs.json.encode(s)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:57:27-06:00
Completed At: 2026-08-01T12:57:27-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T12:57:29-06:00
Completed At: 2026-08-01T12:57:29-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

The requested changes have been applied. I have added `scrollSensitivity`, `scrollAcceleration`, and `scrollFrictionalDecay` configurations, updated the scroll tap logic in `init.lua`, added the corresponding sliders to the settings UI, and bundled/reloaded the project.

---
