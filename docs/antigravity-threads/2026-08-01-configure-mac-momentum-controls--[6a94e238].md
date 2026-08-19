---
title: "Configure Mac Momentum Controls"
date: "2026-08-01"
conversation_id: "6a94e238-6d39-44b1-baf3-1f59c9db7ac3"
source: "antigravity"
---

# Configure Mac Momentum Controls

## User

Fix the macOS momentum stream issue and introduce two new controls to eliminate unpredictable momentum glide:

1. **Max Inertia Duration / Cap** (`scrollMaxInertiaMs`): Hard time limit (e.g. 50ms – 500ms) on how long inertia is allowed to continue after finger lift-off. Once this duration elapses, all remaining momentum events from macOS are hard cut off!
2. **Velocity Damping Threshold** (`scrollInertiaCutoff`): Velocity threshold below which momentum stops immediately (cuts off the long trailing tail).

Implementation in `src/config.lua`:
- Add `scrollMaxInertiaMs = getSetting("scrollMaxInertiaMs", 250)` (range 50ms to 600ms, default 250ms).
- Add `scrollInertiaCutoff = getSetting("scrollInertiaCutoff", 0.5)` (range 0.1 to 2.0, default 0.5).
- Save in `saveSettings()`.

Implementation in `src/init.lua`:
- Track `_G.activeWatchers.lastActiveTouchTime` when `phase == 0`.
- When `phase ~= 0` (momentum phase):
  - Check `local timeSinceTouch = (hs.timer.absoluteTime() - (_G.activeWatchers.lastActiveTouchTime or 0)) / 1e6` (in ms).
  - If `timeSinceTouch > (state.scrollMaxInertiaMs or 250)` then `return true` (hard stop!).
  - If `math.abs(scaledDelta) < (state.scrollInertiaCutoff or 0.5)` then `return true` (drop slow trailing tail!).

Implementation in `src/settings_ui.lua`:
- Add sliders for:
  - **Max Inertia Duration** (`scrollMaxInertiaMs`, range 50ms - 600ms, default 250ms): `<span>Hard cap on momentum duration (50ms = sharp stop, 500ms = long coast)</span>`
  - **Low Velocity Cutoff** (`scrollInertiaCutoff`, range 0.1 - 2.0, default 0.5): `<span>Cuts off the slow unpredictable tail at the end of momentum</span>`
- Wire state sync and slider handlers.
- Update canvas visualization to reflect the hard time cutoff line!

Run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

---

## Assistant

Created At: 2026-08-01T13:08:31-06:00
Completed At: 2026-08-01T13:08:31-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"33007"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"12190"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"22510"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T13:08:32-06:00
Completed At: 2026-08-01T13:08:32-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua`
Total Lines: 708
Total Bytes: 33007
Showing lines 1 to 708
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
<truncated 32885 bytes>
d
663: 
664: local function getActiveControlKeysMap()
665:   if _cachedActiveControlKeysMap then return _cachedActiveControlKeysMap end
666:   local map = {}
667:   for code, k in pairs(homeRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
668:   for code, k in pairs(upperRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
669:   for code, k in pairs(lowerRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
670:   for code, k in pairs(numberRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
671:   _cachedActiveControlKeysMap = map
672:   return map
673: end
674: 
675: 
676: return {
677:   state = state,
678:   saveSettings = saveSettings,
679:   SCALES = SCALES,
680:   NOTE_NAMES = NOTE_NAMES,
681:   WHITE_KEY_INDEX = WHITE_KEY_INDEX,
682:   ACTION_CATALOG = ACTION_CATALOG,
683:   defaultNumberRowControls = defaultNumberRowControls,
684:   defaultUpperRowKeys = defaultUpperRowKeys,
685:   defaultLowerRowKeys = defaultLowerRowKeys,
686:   defaultHomeRowControls = defaultHomeRowControls,
687:   numberRowControls = numberRowControls,
688:   upperRowKeys = upperRowKeys,
689:   lowerRowKeys = lowerRowKeys,
690:   homeRowControls = homeRowControls,
691:   applyCustomLayout = applyCustomLayout,
692:   saveCustomLayout = saveCustomLayout,
693:   selectPreset = selectPreset,
694:   savePreset = savePreset,
695:   renamePreset = renamePreset,
696:   deletePreset = deletePreset,
697:   duplicatePreset = duplicatePreset,
698:   getPresetsList = getPresetsList,
699:   resetLayout = resetLayout,
700:   updateKeyMapping = updateKeyMapping,
701:   getLayoutConfig = getLayoutConfig,
702:   getNoteKey = getNoteKey,
703:   getControlKey = getControlKey,
704:   getNumberControlKey = getNumberControlKey,
705:   getActiveNoteKeysMap = getActiveNoteKeysMap,
706:   getActiveControlKeysMap = getActiveControlKeysMap
707: }
708: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T13:08:32-06:00
Completed At: 2026-08-01T13:08:32-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 337
Total Bytes: 12190
Showing lines 1 to 337
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
<truncated 10211 bytes>
:%M:%S") .. " [WATCHDOG]: " .. msg .. "\n"); f:close() end
284:         
285:         pcall(function()
286:           local h = hud.reloadMidiWebview()
287:           if h then h:show() end
288:           hs.alert.show("UI Auto-Recovered by Watchdog", 2.0)
289:         end)
290:       end
291:     end
292:   end
293: end)
294: 
295: _G.activeWatchers.midiToggleHotkey = hs.hotkey.bind({ "cmd", "alt" }, "M", function()
296:   _G.toggleMidiMode()
297: end)
298: 
299: _G.activeWatchers.midiRefreshHotkey = hs.hotkey.bind({ "cmd", "alt" }, "R", function()
300:   hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5)
301:   hs.notify.new({ title = "QWERTY MIDI", informativeText = "Executing full Hammerspoon hard reload..." }):send()
302:   hs.timer.doAfter(0.1, function() hs.reload() end)
303: end)
304: 
305: if _G.activeWatchers.settingsHotkey then
306:   _G.activeWatchers.settingsHotkey:delete()
307:   _G.activeWatchers.settingsHotkey = nil
308: end
309: 
310: profileLog("Before panicAllChannels")
311: midi.panicAllChannels()
312: 
313: -- Auto-reopen window if it was open when the last reload occurred
314: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
315: if wasOpen then
316:   profileLog("Auto-reopening controller window (was open before reload)")
317:   hs.timer.doAfter(0.3, function()
318:     local ok, err = pcall(function()
319:       _G.toggleMidiMode(true)
320:     end)
321:     if not ok then
322:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
323:     end
324:   end)
325: end
326: 
327: _G.pingController = function() return hud.pingController() end
328: _G.dumpMidiLogs = function() return hud.dumpMidiLogs() end
329: _G.hardResetController = function() hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5); hs.reload() end
330: 
331: profileLog("Init complete!")
332: 
333: return {
334:   toggleMidiMode = _G.toggleMidiMode,
335:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
336: }
337: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T13:08:33-06:00
Completed At: 2026-08-01T13:08:33-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua`
Total Lines: 684
Total Bytes: 22510
Showing lines 1 to 684
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
13:   local sensitivity = state.scrollSensitivity or 0.15
14:   local acceleration = state.scrollAcceleration or 1.0
15:   local initGain = state.scrollInertiaInitial or 1.0
16:   local decay = state.scrollInertiaDecay or 0.85
17:   local curveExp = state.scrollCurveExponent or 1.0
18: 
19:   -- Build BPM step selected states
20:   local bpmSel = { ["1"]="", ["5"]="", ["10"]="", ["25"]="" }
21:   bpmSel[tostring(bpmStep)] = "selected"
22: 
23:   -- Build zoom selected states
24:   local zoomSel = {}
25:   for _, v in ipairs({0.8, 1.0, 1.2, 1.4}) do
26:     zoomSel[tostring(v)] = math.abs(zoom - v) < 0.05 and "selected" or ""
27:   end
28: 
29:   -- Format floats nicely for slider defaults
30:   local sensFmt    = string.format("%.2f", sensitivity)
31:   local accFmt     = string.format("%.2f", acceleration)
32:   local initFmt    = string.format("%.2f", initGain)
33:   local decayFmt   = string.format("%.2f", decay)
34:   local curveFmt   = string.format("%.1f", curveExp)
35: 
36:   return string.format([[
37: <!DOCTYPE html>
38: <html>
39: <head>
40:   <meta charset="utf-8"/>
41:   <style>
42:     * { box-
<truncated 22273 bytes>
)
630:   -- Borderless floating panel that sits above the HUD webview
631:   wv:windowStyle({ "borderless", "nonactivating" })
632:   wv:level(hs.drawing.windowLevels.floating + 1)
633:   wv:allowTextEntry(true)
634:   wv:html(generateSettingsHTML())
635: 
636:   _G.activeWatchers.settingsWebview = wv
637:   return wv
638: end
639: 
640: local function syncStateToWebview()
641:   if not _G.activeWatchers.settingsWebview then return end
642:   local s = {
643:     bpmStepSize = state.bpmStepSize or 10,
644:     logicSyncEnabled = state.logicSyncEnabled,
645:     arpGatePercent = state.arpGatePercent or 80,
646:     zoomLevel = state.zoomLevel or 1.0,
647:     scrollSensitivity = state.scrollSensitivity or 0.15,
648:     scrollAcceleration = state.scrollAcceleration or 1.0,
649:     scrollInertiaInitial = state.scrollInertiaInitial or 1.0,
650:     scrollInertiaDecay = state.scrollInertiaDecay or 0.85,
651:     scrollCurveExponent = state.scrollCurveExponent or 1.0
652:   }
653:   local jsonStr = hs.json.encode(s)
654:   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
655: end
656: 
657: local function toggleSettingsWindow()
658:   local wv = createSettingsWebview()
659: 
660:   if wv:isVisible() then
661:     wv:hide()
662:   else
663:     local screen = hs.screen.mainScreen():frame()
664:     local w, h = 528, 612
665:     local x = math.floor(screen.x + (screen.w - w) / 2)
666:     local y = math.floor(screen.y + (screen.h - h) / 2)
667:     wv:frame({ x = x, y = y, w = w, h = h })
668: 
669:     syncStateToWebview()
670:     wv:show()
671:   end
672: end
673: 
674: -- Cleanup old instance on reload and pre-warm new settings webview
675: if _G.activeWatchers.settingsWebview then
676:   _G.activeWatchers.settingsWebview:delete()
677:   _G.activeWatchers.settingsWebview = nil
678: end
679: createSettingsWebview()
680: 
681: return {
682:   toggleSettingsWindow = toggleSettingsWindow
683: }
684: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T13:08:36-06:00
Completed At: 2026-08-01T13:08:51-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -93,6 +93,8 @@
   scrollInertiaInitial  = getSetting("scrollInertiaInitial", 1.0),
   scrollInertiaDecay    = getSetting("scrollInertiaDecay", 0.85),
   scrollCurveExponent   = getSetting("scrollCurveExponent", 1.0),
+  scrollMaxInertiaMs    = getSetting("scrollMaxInertiaMs", 250),
+  scrollInertiaCutoff   = getSetting("scrollInertiaCutoff", 0.5),
 
   DIGIT_KEYCODES = {
     [50] = "`", [29] = "0", [18] = "1", [19] = "2", [20] = "3", [21] = "4",
@@ -137,6 +137,8 @@
   state.scrollInertiaInitial = tonumber(state.scrollInertiaInitial) or 1.0
   state.scrollInertiaDecay = tonumber(state.scrollInertiaDecay) or 0.85
   state.scrollCurveExponent = tonumber(state.scrollCurveExponent) or 1.0
+  state.scrollMaxInertiaMs = tonumber(state.scrollMaxInertiaMs) or 250
+  state.scrollInertiaCutoff = tonumber(state.scrollInertiaCutoff) or 0.5
   state.topRowVolume = tonumber(state.topRowVolume) or 100
   state.bottomRowVolume = tonumber(state.bottomRowVolume) or 100
   state.zoomLevel = tonumber(state.zoomLevel) or 1.0
@@ -163,6 +163,8 @@
   hs.settings.set("qwertyMidi_scrollInertiaInitial", state.scrollInertiaInitial)
   hs.settings.set("qwertyMidi_scrollInertiaDecay", state.scrollInertiaDecay)
   hs.settings.set("qwertyMidi_scrollCurveExponent", state.scrollCurveExponent)
+  hs.settings.set("qwertyMidi_scrollMaxInertiaMs", state.scrollMaxInertiaMs)
+  hs.settings.set("qwertyMidi_scrollInertiaCutoff", state.scrollInertiaCutoff)
   hs.settings.set("qwertyMidi_topRowVolume", state.topRowVolume)
   hs.settings.set("qwertyMidi_bottomRowVolume", state.bottomRowVolume)
   hs.settings.set("qwertyMidi_zoomLevel", state.zoomLevel)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-01T13:08:53-06:00
Completed At: 2026-08-01T13:08:53-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -68,6 +68,10 @@
 
     -- Scroll handling
     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
+    if phase == 0 then
+      _G.activeWatchers.lastActiveTouchTime = hs.timer.absoluteTime()
+    end
+
     local sens = state.scrollSensitivity or 0.15
     local accel = state.scrollAcceleration or 1.0
     local initGain = state.scrollInertiaInitial or 1.0
@@ -74,4 +74,6 @@
     local curveExp = state.scrollCurveExponent or 1.0
+    local maxInertiaMs = state.scrollMaxInertiaMs or 250
+    local inertiaCutoff = state.scrollInertiaCutoff or 0.5
 
     deltaY = math.max(-100, math.min(100, deltaY))
 
@@ -81,6 +81,10 @@
     local scaledDelta = curvedDelta * sens * accel
 
     if phase ~= 0 then
+      local timeSinceTouch = (hs.timer.absoluteTime() - (_G.activeWatchers.lastActiveTouchTime or 0)) / 1e6
+      if timeSinceTouch > maxInertiaMs then return true end
+      if math.abs(scaledDelta) < inertiaCutoff then return true end
+
       if initGain == 0 then return true end
       scaledDelta = scaledDelta * initGain * decay
     end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T13:09:00-06:00
Completed At: 2026-08-01T13:09:00-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -321,6 +321,28 @@
 
       <div class="row">
         <div class="row-label">
+          <strong>Max Inertia Duration</strong>
+          <span>Hard cap on momentum duration (50ms = sharp stop, 500ms = long coast)</span>
+        </div>
+        <input type="number" id="maxInertiaMs" value="%d" min="50" max="600" step="10"
+          onchange="send('setMaxInertia', parseInt(this.value))">
+      </div>
+
+      <div class="row">
+        <div class="row-label">
+          <strong>Low Velocity Cutoff</strong>
+          <span>Cuts off the slow unpredictable tail at the end of momentum</span>
+        </div>
+        <div class="slider-row">
+          <input type="range" id="inertiaCutoffSlider" min="0.1" max="2.0" step="0.1"
+            value="%s"
+            oninput="onCutoff(this.value)">
+          <div class="slider-val" id="inertiaCutoffVal">%s</div>
+        </div>
+      </div>
+
+      <div class="row">
+        <div class="row-label">
           <strong>Velocity Curve Exponent</strong>
           <span>Gesture curve shape (1.0 = linear, 2.0 = exponential ramp-up/down)</span>
         </div>
@@ -332,7 +332,7 @@
       </div>
       <div style="margin-top: 15px;">
         <canvas id="physicsCanvas" width="460" height="140" style="background:rgba(20,16,10,0.6); border:1px solid rgba(212,163,89,0.3); border-radius:8px; cursor:crosshair;"></canvas>
-        <div style="font-size: 0.72rem; color: rgba(212,163,89,0.7); margin-top: 6px; display: flex; justify-content: space-between;"><span>── Solid: Response Curve</span><span>- - Dashed: Coasting Tail</span><span>Scroll box to test</span></div>
+        <div style="font-size: 0.72rem; color: rgba(212,163,89,0.7);
<truncated 1859 bytes>
cument.getElementById('curveSlider');
       if (el) el.value = s.scrollCurveExponent;
@@ -543,6 +543,8 @@
     accFmt, accFmt,
     initFmt, initFmt,
     decayFmt, decayFmt,
+    math.floor(state.scrollMaxInertiaMs or 250),
+    string.format("%.1f", state.scrollInertiaCutoff or 0.5), string.format("%.1f", state.scrollInertiaCutoff or 0.5),
     curveFmt, curveFmt,
     -- bpm step selects
     bpmSel["1"], bpmSel["5"], bpmSel["10"], bpmSel["25"],
@@ -602,6 +602,14 @@
       local val = tonumber(body.value) or 1.0
       state.scrollCurveExponent = math.max(0.5, math.min(3.0, val))
       hs.settings.set("qwertyMidi_scrollCurveExponent", val)
+    elseif body.type == "setMaxInertia" then
+      local val = tonumber(body.value) or 250
+      state.scrollMaxInertiaMs = math.max(50, math.min(600, val))
+      hs.settings.set("qwertyMidi_scrollMaxInertiaMs", val)
+    elseif body.type == "setCutoff" then
+      local val = tonumber(body.value) or 0.5
+      state.scrollInertiaCutoff = math.max(0.1, math.min(2.0, val))
+      hs.settings.set("qwertyMidi_scrollInertiaCutoff", val)
     elseif body.type == "close" then
       if _G.activeWatchers.settingsWebview then
         _G.activeWatchers.settingsWebview:hide()
@@ -641,7 +641,9 @@
     scrollAcceleration = state.scrollAcceleration or 1.0,
     scrollInertiaInitial = state.scrollInertiaInitial or 1.0,
     scrollInertiaDecay = state.scrollInertiaDecay or 0.85,
-    scrollCurveExponent = state.scrollCurveExponent or 1.0
+    scrollCurveExponent = state.scrollCurveExponent or 1.0,
+    scrollMaxInertiaMs = state.scrollMaxInertiaMs or 250,
+    scrollInertiaCutoff = state.scrollInertiaCutoff or 0.5
   }
   local jsonStr = hs.json.encode(s)
   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T13:09:01-06:00
Completed At: 2026-08-01T13:09:01-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T13:09:03-06:00
Completed At: 2026-08-01T13:09:03-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

The requested scroll momentum controls have been implemented.

### Changes implemented:

*   **Logic (`src/config.lua` & `src/init.lua`)**:
    *   Added `scrollMaxInertiaMs` (default: 250ms) and `scrollInertiaCutoff` (default: 0.5) to settings.
    *   Updated the scroll event handler (`init.lua`) to track the initial touch time and apply hard cutoffs based on the new constraints when in momentum phase (`phase ~= 0`).
*   **UI (`src/settings_ui.lua`)**:
    *   Added a number input for **Max Inertia Duration** and a slider for **Low Velocity Cutoff**.
    *   Updated the physics canvas visualization to show a dashed line representing the coasting tail, including the new hard time cutoff point.
*   **Deployment**:
    *   Bundled and reloaded the project using `/Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

You can now adjust these new parameters in the QWERTY MIDI settings window to tune your trackpad scrolling experience.

---
