---
title: "Refactor Trackpad Scrolling Parameters"
date: "2026-08-01"
conversation_id: "47ef46c5-4827-421e-9538-1b997f166803"
source: "antigravity"
---

# Refactor Trackpad Scrolling Parameters

## User

Separate trackpad scroll control into two independent parameters:
1. `scrollAcceleration` (Speed & curve of active scrolling while fingers touch the trackpad).
2. `scrollFrictionalDecay` (Friction / Coast duration after fingers lift off). Also fix the unnatural "ramp up/down" feel during phase change by calculating smooth decay or clean phase handoff.

Implement in:
1. `src/config.lua`:
   - `scrollAcceleration` (default 0.15)
   - `scrollFrictionalDecay` (default 0.85, range 0.0 - 0.98 where 0 is instant stop, 0.85 is smooth decay)
   - Remove/deprecate `scrollInertiaPreset` and old single `scrollMomentumScale`.
   - Update `saveSettings()` for `scrollAcceleration` and `scrollFrictionalDecay`.

2. `src/init.lua`:
   - Update `_G.activeWatchers.midiScrollTap`:
   - Track `scrollVelocity = 0` across events.
   - When `phase == 0` (active touch):
     - `scrollVelocity = deltaY * (state.scrollAcceleration or 0.15)`
     - Apply active delta directly.
   - When `phase ~= 0` (momentum / release phase):
     - If `state.scrollFrictionalDecay == 0`, ignore momentum events completely (`return true`).
     - Otherwise, compute decayed velocity smoothly: `scrollVelocity = scrollVelocity * state.scrollFrictionalDecay`.
     - Accumulate `scrollVelocity` into `modAccumulator`.
     - Stop momentum if `math.abs(scrollVelocity) < 0.01`.

3. `src/settings_ui.lua`:
   - Replace the single Momentum scale & Preset dropdown with two dedicated sliders:
     - **Scroll Acceleration** (0.01 to 0.50)
     - **Post-Release Coasting (Inertia Friction)** (0.00 = Instant stop to 0.98 = Long glide)
   - Wire handlers `onAcceleration(val)` and `onFrictionalDecay(val)`.
   - Update `qwerty_midi.lua` bundle via `bin/bundle_and_reload.sh`.

---

## Assistant

Created At: 2026-08-01T12:55:28-06:00
Completed At: 2026-08-01T12:55:28-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"32612"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"12356"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"16862"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T12:55:29-06:00
Completed At: 2026-08-01T12:55:29-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua`
Total Lines: 702
Total Bytes: 32612
Showing lines 1 to 702
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
<truncated 32460 bytes>
d
657: 
658: local function getActiveControlKeysMap()
659:   if _cachedActiveControlKeysMap then return _cachedActiveControlKeysMap end
660:   local map = {}
661:   for code, k in pairs(homeRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
662:   for code, k in pairs(upperRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
663:   for code, k in pairs(lowerRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
664:   for code, k in pairs(numberRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
665:   _cachedActiveControlKeysMap = map
666:   return map
667: end
668: 
669: 
670: return {
671:   state = state,
672:   saveSettings = saveSettings,
673:   SCALES = SCALES,
674:   NOTE_NAMES = NOTE_NAMES,
675:   WHITE_KEY_INDEX = WHITE_KEY_INDEX,
676:   ACTION_CATALOG = ACTION_CATALOG,
677:   defaultNumberRowControls = defaultNumberRowControls,
678:   defaultUpperRowKeys = defaultUpperRowKeys,
679:   defaultLowerRowKeys = defaultLowerRowKeys,
680:   defaultHomeRowControls = defaultHomeRowControls,
681:   numberRowControls = numberRowControls,
682:   upperRowKeys = upperRowKeys,
683:   lowerRowKeys = lowerRowKeys,
684:   homeRowControls = homeRowControls,
685:   applyCustomLayout = applyCustomLayout,
686:   saveCustomLayout = saveCustomLayout,
687:   selectPreset = selectPreset,
688:   savePreset = savePreset,
689:   renamePreset = renamePreset,
690:   deletePreset = deletePreset,
691:   duplicatePreset = duplicatePreset,
692:   getPresetsList = getPresetsList,
693:   resetLayout = resetLayout,
694:   updateKeyMapping = updateKeyMapping,
695:   getLayoutConfig = getLayoutConfig,
696:   getNoteKey = getNoteKey,
697:   getControlKey = getControlKey,
698:   getNumberControlKey = getNumberControlKey,
699:   getActiveNoteKeysMap = getActiveNoteKeysMap,
700:   getActiveControlKeysMap = getActiveControlKeysMap
701: }
702: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:55:30-06:00
Completed At: 2026-08-01T12:55:30-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 331
Total Bytes: 12356
Showing lines 1 to 331
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
<truncated 10347 bytes>
:%M:%S") .. " [WATCHDOG]: " .. msg .. "\n"); f:close() end
278:         
279:         pcall(function()
280:           local h = hud.reloadMidiWebview()
281:           if h then h:show() end
282:           hs.alert.show("UI Auto-Recovered by Watchdog", 2.0)
283:         end)
284:       end
285:     end
286:   end
287: end)
288: 
289: _G.activeWatchers.midiToggleHotkey = hs.hotkey.bind({ "cmd", "alt" }, "M", function()
290:   _G.toggleMidiMode()
291: end)
292: 
293: _G.activeWatchers.midiRefreshHotkey = hs.hotkey.bind({ "cmd", "alt" }, "R", function()
294:   hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5)
295:   hs.notify.new({ title = "QWERTY MIDI", informativeText = "Executing full Hammerspoon hard reload..." }):send()
296:   hs.timer.doAfter(0.1, function() hs.reload() end)
297: end)
298: 
299: if _G.activeWatchers.settingsHotkey then
300:   _G.activeWatchers.settingsHotkey:delete()
301:   _G.activeWatchers.settingsHotkey = nil
302: end
303: 
304: profileLog("Before panicAllChannels")
305: midi.panicAllChannels()
306: 
307: -- Auto-reopen window if it was open when the last reload occurred
308: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
309: if wasOpen then
310:   profileLog("Auto-reopening controller window (was open before reload)")
311:   hs.timer.doAfter(0.3, function()
312:     local ok, err = pcall(function()
313:       _G.toggleMidiMode(true)
314:     end)
315:     if not ok then
316:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
317:     end
318:   end)
319: end
320: 
321: _G.pingController = function() return hud.pingController() end
322: _G.dumpMidiLogs = function() return hud.dumpMidiLogs() end
323: _G.hardResetController = function() hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5); hs.reload() end
324: 
325: profileLog("Init complete!")
326: 
327: return {
328:   toggleMidiMode = _G.toggleMidiMode,
329:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
330: }
331: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:55:30-06:00
Completed At: 2026-08-01T12:55:30-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua`
Total Lines: 545
Total Bytes: 16862
Showing lines 1 to 545
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
13:   local sensitivity    = state.scrollSensitivity or 0.15
14:   local momentumScale  = state.scrollMomentumScale or 0.3
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
27:   local sensFmt    = string.format("%.2f", sensitivity)
28:   local momentFmt  = string.format("%.2f", momentumScale)
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
48
<truncated 15930 bytes>
w({ x = x, y = y, w = w, h = h }, { developerExtrasEnabled = true }, uc)
492:   wv:windowTitle("QWERTY MIDI Settings")
493:   -- Borderless floating panel that sits above the HUD webview
494:   wv:windowStyle({ "borderless", "nonactivating" })
495:   wv:level(hs.drawing.windowLevels.floating + 1)
496:   wv:allowTextEntry(true)
497:   wv:html(generateSettingsHTML())
498: 
499:   _G.activeWatchers.settingsWebview = wv
500:   return wv
501: end
502: 
503: local function syncStateToWebview()
504:   if not _G.activeWatchers.settingsWebview then return end
505:   local s = {
506:     bpmStepSize = state.bpmStepSize or 10,
507:     logicSyncEnabled = state.logicSyncEnabled,
508:     arpGatePercent = state.arpGatePercent or 80,
509:     zoomLevel = state.zoomLevel or 1.0,
510:     scrollSensitivity = state.scrollSensitivity or 0.15,
511:     scrollMomentumScale = state.scrollMomentumScale or 0.3,
512:     scrollInertiaPreset = state.scrollInertiaPreset or "linear_damped"
513:   }
514:   local jsonStr = hs.json.encode(s)
515:   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
516: end
517: 
518: local function toggleSettingsWindow()
519:   local wv = createSettingsWebview()
520: 
521:   if wv:isVisible() then
522:     wv:hide()
523:   else
524:     local screen = hs.screen.mainScreen():frame()
525:     local w, h = 528, 612
526:     local x = math.floor(screen.x + (screen.w - w) / 2)
527:     local y = math.floor(screen.y + (screen.h - h) / 2)
528:     wv:frame({ x = x, y = y, w = w, h = h })
529: 
530:     syncStateToWebview()
531:     wv:show()
532:   end
533: end
534: 
535: -- Cleanup old instance on reload and pre-warm new settings webview
536: if _G.activeWatchers.settingsWebview then
537:   _G.activeWatchers.settingsWebview:delete()
538:   _G.activeWatchers.settingsWebview = nil
539: end
540: createSettingsWebview()
541: 
542: return {
543:   toggleSettingsWindow = toggleSettingsWindow
544: }
545: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:55:33-06:00
Completed At: 2026-08-01T12:55:33-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -88,9 +88,8 @@
   logicSyncTimer = nil,
 
   -- Scroll / Trackpad
-  scrollSensitivity    = getSetting("scrollSensitivity", 0.15),
-  scrollMomentumScale  = getSetting("scrollMomentumScale", 0.3),
-  scrollInertiaPreset  = getSetting("scrollInertiaPreset", "linear_damped"),
+  scrollAcceleration    = getSetting("scrollAcceleration", 0.15),
+  scrollFrictionalDecay = getSetting("scrollFrictionalDecay", 0.85),
 
   DIGIT_KEYCODES = {
     [50] = "`", [29] = "0", [18] = "1", [19] = "2", [20] = "3", [21] = "4",
@@ -130,9 +130,8 @@
   state.arpGatePercent = tonumber(state.arpGatePercent) or 80.0
   state.arpBpm = tonumber(state.arpBpm) or 120.0
   state.bpmStepSize = tonumber(state.bpmStepSize) or 10
-  state.scrollSensitivity = tonumber(state.scrollSensitivity) or 0.15
-  state.scrollMomentumScale = tonumber(state.scrollMomentumScale) or 0.3
-  if type(state.scrollInertiaPreset) ~= "string" then state.scrollInertiaPreset = "linear_damped" end
+  state.scrollAcceleration = tonumber(state.scrollAcceleration) or 0.15
+  state.scrollFrictionalDecay = tonumber(state.scrollFrictionalDecay) or 0.85
   state.topRowVolume = tonumber(state.topRowVolume) or 100
   state.bottomRowVolume = tonumber(state.bottomRowVolume) or 100
   state.zoomLevel = tonumber(state.zoomLevel) or 1.0
@@ -154,9 +154,8 @@
   hs.settings.set("qwertyMidi_arpBottomEnabled", state.arpBottomEnabled == true)
   hs.settings.set("qwertyMidi_bpmStepSize", state.bpmStepSize)
   hs.settings.set("qwertyMidi_logicSyncEnabled", state.logicSyncEnabled == true)
-  hs.settings.set("qwertyMidi_scrollSensitivity", state.scrollSensitivity)
-  hs.settings.set("qwertyMidi_scrollMomentumScale", state.scrollMomentumScale)
-  hs.settings.set("qwertyMidi_scrollInertiaPreset", state.scrollInertiaPreset)
+  hs.settings.set("qwertyMidi_scrollAcceleration", state.scrollAcceleration)
+  hs.settings.set("qwertyMidi_scrollFrictionalDecay", state.scrollFrictionalDecay)
   hs.settings.set("qwertyMidi_topRowVolume", state.topRowVolume)
   hs.settings.set("qwertyMidi_bottomRowVolume", state.bottomRowVolume)
   hs.settings.set("qwertyMidi_zoomLevel", state.zoomLevel)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:55:37-06:00
Completed At: 2026-08-01T12:55:37-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -66,20 +66,17 @@
       deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventPointDeltaAxis1) or 0
     end
 
-    -- Dampen (not block) momentum/inertia events so deceleration feels natural but short
+    -- Scroll handling
     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
-    local preset = state.scrollInertiaPreset or "linear_damped"
-
-    local inertiaScale = 1.0
-    if preset == "direct_raw" then
-      if phase ~= 0 then return true end -- drop momentum events completely
-      inertiaScale = state.scrollMomentumScale
-    elseif preset == "exponential_decay" then
-      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.15)
-    elseif preset == "friction_coasting" then
-      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.45)
-    else -- linear_damped (default)
-      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.3)
+    _G.activeWatchers.scrollVelocity = _G.activeWatchers.scrollVelocity or 0
+
+    if phase == 0 then
+      _G.activeWatchers.scrollVelocity = deltaY * (state.scrollAcceleration or 0.15)
+    else
+      if state.scrollFrictionalDecay == 0 then return true end
+      _G.activeWatchers.scrollVelocity = _G.activeWatchers.scrollVelocity * state.scrollFrictionalDecay
+      if math.abs(_G.activeWatchers.scrollVelocity) < 0.01 then return true end
+      deltaY = _G.activeWatchers.scrollVelocity
     end
 
     -- Allow native webview scrolling only when cursor is specifically over a scrollable pane in the HUD
@@ -86,12 +86,12 @@
       return false
     end
 
-        if deltaY ~= 0 then
+    if deltaY ~= 0 then
       if state.shiftHeld then
         local avgVol = (state.topRowVolume + state.bottomRowVolume) / 2
         _G.activeWatchers.volAccumulator = _G.activeWatchers.volAccumulator or avgVol
-        local sensitivity = 0.25 * inertiaScale
-        _G.activeWatchers.volAccumulator = math.max(0, math.min(127, _G.activeWatchers.volAccumulator - (deltaY * sensitivity)))
+        -- Adjusting volume with new scroll mechanics
+        _G.activeWatchers.volAccumulator = math.max(0, math.min(127, _G.activeWatchers.volAccumulator - deltaY))
         local newVol = math.floor(_G.activeWatchers.volAccumulator + 0.5)
 
         local deltaVol = newVol - math.floor(avgVol + 0.5)
@@ -109,8 +109,7 @@
       else
         local currentMod = state.ccStates[1] or 0
         _G.activeWatchers.modAccumulator = _G.activeWatchers.modAccumulator or currentMod
-        local sensitivity = state.scrollSensitivity * inertiaScale
-        _G.activeWatchers.modAccumulator = math.max(0, math.min(127, _G.activeWatchers.modAccumulator - (deltaY * sensitivity)))
+        _G.activeWatchers.modAccumulator = math.max(0, math.min(127, _G.activeWatchers.modAccumulator - deltaY))
         local newMod = math.floor(_G.activeWatchers.modAccumulator + 0.5)
 
         if newMod ~= state.ccStates[1] then
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:55:43-06:00
Completed At: 2026-08-01T12:55:43-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,8 +10,8 @@
   local logicSync      = state.logicSyncEnabled
   local gate           = state.arpGatePercent or 80
   local zoom           = state.zoomLevel or 1.0
-  local sensitivity    = state.scrollSensitivity or 0.15
-  local momentumScale  = state.scrollMomentumScale or 0.3
+  local acceleration  = state.scrollAcceleration or 0.15
+  local decay         = state.scrollFrictionalDecay or 0.85
 
   -- Build BPM step selected states
   local bpmSel = { ["1"]="", ["5"]="", ["10"]="", ["25"]="" }
@@ -23,8 +23,8 @@
   end
 
   -- Format floats nicely for slider defaults
-  local sensFmt    = string.format("%.2f", sensitivity)
-  local momentFmt  = string.format("%.2f", momentumScale)
+  local accFmt     = string.format("%.2f", acceleration)
+  local decayFmt   = string.format("%.2f", decay)
 
   return string.format([[
 <!DOCTYPE html>
@@ -261,41 +261,28 @@
 
       <div class="row">
         <div class="row-label">
-          <strong>Mod Wheel Sensitivity</strong>
-          <span>Speed of mod wheel change per scroll tick</span>
-        </div>
-        <div class="slider-row">
-          <input type="range" id="sensitivitySlider" min="0.02" max="0.5" step="0.01"
-            value="%s"
-            oninput="onSensitivity(this.value)">
-          <div class="slider-val" id="sensitivityVal">%s</div>
-        </div>
-      </div>
-
-      <div class="row">
-        <div class="row-label">
-          <strong>Momentum Scale</strong>
-          <span>Inertia strength after finger lifts (0 = none)</span>
-        </div>
-        <div class="slider-row">
-          <input type="range" id="momentumSlider" min="0" max="1" step="0.05"
-            value="%s"
-            oninput
<truncated 3925 bytes>
       local val = tonumber(body.value) or 1.0
       state.zoomLevel = val
       hs.settings.set("qwertyMidi_zoomLevel", val)
-    elseif body.type == "setSensitivity" then
+    elseif body.type == "setAcceleration" then
       local val = tonumber(body.value) or 0.15
-      state.scrollSensitivity = val
-      hs.settings.set("qwertyMidi_scrollSensitivity", val)
-    elseif body.type == "setMomentum" then
-      local val = tonumber(body.value) or 0.3
-      state.scrollMomentumScale = val
-      hs.settings.set("qwertyMidi_scrollMomentumScale", val)
-    elseif body.type == "setInertiaPreset" then
-      state.scrollInertiaPreset = body.value
-      hs.settings.set("qwertyMidi_scrollInertiaPreset", state.scrollInertiaPreset)
+      state.scrollAcceleration = val
+      hs.settings.set("qwertyMidi_scrollAcceleration", val)
+    elseif body.type == "setDecay" then
+      local val = tonumber(body.value) or 0.85
+      state.scrollFrictionalDecay = math.max(0, math.min(0.98, val))
+      hs.settings.set("qwertyMidi_scrollFrictionalDecay", val)
     elseif body.type == "close" then
       if _G.activeWatchers.settingsWebview then
         _G.activeWatchers.settingsWebview:hide()
@@ -501,9 +501,8 @@
     logicSyncEnabled = state.logicSyncEnabled,
     arpGatePercent = state.arpGatePercent or 80,
     zoomLevel = state.zoomLevel or 1.0,
-    scrollSensitivity = state.scrollSensitivity or 0.15,
-    scrollMomentumScale = state.scrollMomentumScale or 0.3,
-    scrollInertiaPreset = state.scrollInertiaPreset or "linear_damped"
+    scrollAcceleration = state.scrollAcceleration or 0.15,
+    scrollFrictionalDecay = state.scrollFrictionalDecay or 0.85
   }
   local jsonStr = hs.json.encode(s)
   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:55:44-06:00
Completed At: 2026-08-01T12:55:44-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T12:55:46-06:00
Completed At: 2026-08-01T12:55:46-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

The trackpad scroll control has been successfully refactored. The requested parameters (`scrollAcceleration` and `scrollFrictionalDecay`) are now implemented, replacing the previous inertia presets and momentum scaling.

### Summary of Changes

*   **`src/config.lua`**:
    *   Added `scrollAcceleration` (default 0.15).
    *   Added `scrollFrictionalDecay` (default 0.85).
    *   Deprecated `scrollInertiaPreset`, `scrollSensitivity`, and `scrollMomentumScale`.
    *   Updated `saveSettings()` to persist the new parameters.
*   **`src/init.lua`**:
    *   Updated `_G.activeWatchers.midiScrollTap` to handle the new scroll mechanics.
    *   Active touch now uses `scrollAcceleration`.
    *   Release/momentum phase now uses `scrollFrictionalDecay` for smooth deceleration, with a velocity threshold for stopping.
*   **`src/settings_ui.lua`**:
    *   Replaced the inertia preset dropdown and momentum slider with two dedicated sliders: **Scroll Acceleration** (0.01 to 0.50) and **Post-Release Coasting (Inertia Friction)** (0.00 to 0.98).
*   **Bundle & Reload**: Executed `./bin/bundle_and_reload.sh` to update the application and reload Hammerspoon.

The system is now running with the updated scroll configuration.

---
