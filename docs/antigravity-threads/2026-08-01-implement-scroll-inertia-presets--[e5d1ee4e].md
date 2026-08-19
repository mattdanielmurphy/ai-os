---
title: "Implement Scroll Inertia Presets"
date: "2026-08-01"
conversation_id: "e5d1ee4e-c23b-4edd-9607-61c69a4ea4e7"
source: "antigravity"
---

# Implement Scroll Inertia Presets

## User

Add inertia preset implementation and dropdown settings to qwerty-midi-hammerspoon.

Files to modify:
1. `src/config.lua`:
   - In default state table, add `scrollInertiaPreset = getSetting("scrollInertiaPreset", "linear_damped")` (options: "linear_damped", "direct_raw", "exponential_decay", "friction_coasting").
   - In `saveSettings()`, sanitize `state.scrollInertiaPreset` (ensure string, default to "linear_damped") and save via `hs.settings.set("qwertyMidi_scrollInertiaPreset", state.scrollInertiaPreset)`.

2. `src/init.lua`:
   - Update scroll wheel handler (`_G.activeWatchers.midiScrollTap`).
   - Read `preset = state.scrollInertiaPreset or "linear_damped"`.
   - Calculate `inertiaScale`:
     - If `phase == 0` (user actively scrolling/touching trackpad): `inertiaScale = state.scrollMomentumScale` (or 1.0 depending on preset, but for active touch use `state.scrollMomentumScale`).
     - If `phase ~= 0` (momentum phase):
       - preset `"direct_raw"`: ignore phase, return immediately if `phase ~= 0` (0% momentum).
       - preset `"linear_damped"`: current behavior: `inertiaScale = 1.0` (which is full raw phase velocity) or `state.scrollMomentumScale`. Let's define `"linear_damped"` as scaling momentum by `state.scrollMomentumScale` (e.g. `(phase == 0 and state.scrollMomentumScale or (state.scrollMomentumScale * 0.5))`).
       - preset `"exponential_decay"`: damp inertia smoothly with aggressive scale e.g. `(phase == 0 and state.scrollMomentumScale or (state.scrollMomentumScale * 0.15))`.
       - preset `"friction_coasting"`: smooth coasting e.g. `(phase == 0 and state.scrollMomentumScale or (state.scrollMomentumScale * 0.4))`.

Let's organize the exact logic clearly in `src/init.lua`:
```lua
    local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
    local preset = state.scrollInertiaPreset or "linear_damped"

    local inertiaScale = 1.0
    if preset == "direct_raw" then
      if phase ~= 0 then return true end -- drop momentum events completely
      inertiaScale = state.scrollMomentumScale
    elseif preset == "exponential_decay" then
      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.15)
    elseif preset == "friction_coasting" then
      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.45)
    else -- linear_damped (default)
      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.3)
    end
```

3. `src/settings_ui.lua`:
   - Add a dropdown control in the "Trackpad / Scroll" section for "Inertia Preset":
     Options:
     - `direct_raw` ("Direct (No Inertia / Raw Touch)")
     - `linear_damped` ("Linear Damped (Balanced)")
     - `exponential_decay` ("Exponential Decay (Tight & Fast Stop)")
     - `friction_coasting` ("Friction Coasting (Smooth Slide)")
   - Wire `onInertiaPresetChange(val)` to post message `{ type = "setInertiaPreset", value = val }`.
   - Update Lua message handler in `src/settings_ui.lua` for `setInertiaPreset` to update `state.scrollInertiaPreset` and save setting.
   - Update `qwerty_midi.lua` (if bundled or duplicated) to stay in sync with single source files.

4. Run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` to update `qwerty_midi.lua` and reload Hammerspoon.

---

## Assistant

Created At: 2026-08-01T12:51:12-06:00
Completed At: 2026-08-01T12:51:12-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"32354"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"11738"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"15909"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T12:51:13-06:00
Completed At: 2026-08-01T12:51:13-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua`
Total Lines: 699
Total Bytes: 32354
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
<truncated 32187 bytes>
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

Created At: 2026-08-01T12:51:15-06:00
Completed At: 2026-08-01T12:51:15-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -90,6 +90,7 @@
   -- Scroll / Trackpad
   scrollSensitivity    = getSetting("scrollSensitivity", 0.15),
   scrollMomentumScale  = getSetting("scrollMomentumScale", 0.3),
+  scrollInertiaPreset  = getSetting("scrollInertiaPreset", "linear_damped"),
 
   DIGIT_KEYCODES = {
     [50] = "`", [29] = "0", [18] = "1", [19] = "2", [20] = "3", [21] = "4",
@@ -131,6 +131,7 @@
   state.bpmStepSize = tonumber(state.bpmStepSize) or 10
   state.scrollSensitivity = tonumber(state.scrollSensitivity) or 0.15
   state.scrollMomentumScale = tonumber(state.scrollMomentumScale) or 0.3
+  if type(state.scrollInertiaPreset) ~= "string" then state.scrollInertiaPreset = "linear_damped" end
   state.topRowVolume = tonumber(state.topRowVolume) or 100
   state.bottomRowVolume = tonumber(state.bottomRowVolume) or 100
   state.zoomLevel = tonumber(state.zoomLevel) or 1.0
@@ -154,6 +154,7 @@
   hs.settings.set("qwertyMidi_logicSyncEnabled", state.logicSyncEnabled == true)
   hs.settings.set("qwertyMidi_scrollSensitivity", state.scrollSensitivity)
   hs.settings.set("qwertyMidi_scrollMomentumScale", state.scrollMomentumScale)
+  hs.settings.set("qwertyMidi_scrollInertiaPreset", state.scrollInertiaPreset)
   hs.settings.set("qwertyMidi_topRowVolume", state.topRowVolume)
   hs.settings.set("qwertyMidi_bottomRowVolume", state.bottomRowVolume)
   hs.settings.set("qwertyMidi_zoomLevel", state.zoomLevel)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:51:16-06:00
Completed At: 2026-08-01T12:51:16-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 319
Total Bytes: 11738
Showing lines 1 to 319
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
<truncated 9669 bytes>
:%M:%S") .. " [WATCHDOG]: " .. msg .. "\n"); f:close() end
266:         
267:         pcall(function()
268:           local h = hud.reloadMidiWebview()
269:           if h then h:show() end
270:           hs.alert.show("UI Auto-Recovered by Watchdog", 2.0)
271:         end)
272:       end
273:     end
274:   end
275: end)
276: 
277: _G.activeWatchers.midiToggleHotkey = hs.hotkey.bind({ "cmd", "alt" }, "M", function()
278:   _G.toggleMidiMode()
279: end)
280: 
281: _G.activeWatchers.midiRefreshHotkey = hs.hotkey.bind({ "cmd", "alt" }, "R", function()
282:   hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5)
283:   hs.notify.new({ title = "QWERTY MIDI", informativeText = "Executing full Hammerspoon hard reload..." }):send()
284:   hs.timer.doAfter(0.1, function() hs.reload() end)
285: end)
286: 
287: if _G.activeWatchers.settingsHotkey then
288:   _G.activeWatchers.settingsHotkey:delete()
289:   _G.activeWatchers.settingsHotkey = nil
290: end
291: 
292: profileLog("Before panicAllChannels")
293: midi.panicAllChannels()
294: 
295: -- Auto-reopen window if it was open when the last reload occurred
296: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
297: if wasOpen then
298:   profileLog("Auto-reopening controller window (was open before reload)")
299:   hs.timer.doAfter(0.3, function()
300:     local ok, err = pcall(function()
301:       _G.toggleMidiMode(true)
302:     end)
303:     if not ok then
304:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
305:     end
306:   end)
307: end
308: 
309: _G.pingController = function() return hud.pingController() end
310: _G.dumpMidiLogs = function() return hud.dumpMidiLogs() end
311: _G.hardResetController = function() hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5); hs.reload() end
312: 
313: profileLog("Init complete!")
314: 
315: return {
316:   toggleMidiMode = _G.toggleMidiMode,
317:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
318: }
319: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:51:18-06:00
Completed At: 2026-08-01T12:51:18-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -68,7 +68,19 @@
 
     -- Dampen (not block) momentum/inertia events so deceleration feels natural but short
     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
-    local inertiaScale = (phase == 0) and state.scrollMomentumScale or 1.0
+    local preset = state.scrollInertiaPreset or "linear_damped"
+
+    local inertiaScale = 1.0
+    if preset == "direct_raw" then
+      if phase ~= 0 then return true end -- drop momentum events completely
+      inertiaScale = state.scrollMomentumScale
+    elseif preset == "exponential_decay" then
+      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.15)
+    elseif preset == "friction_coasting" then
+      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.45)
+    else -- linear_damped (default)
+      inertiaScale = (phase == 0) and state.scrollMomentumScale or (state.scrollMomentumScale * 0.3)
+    end
 
     -- Allow native webview scrolling only when cursor is specifically over a scrollable pane in the HUD
     if _G.activeWatchers.isHoveringScrollable then
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:51:18-06:00
Completed At: 2026-08-01T12:51:18-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua`
Total Lines: 524
Total Bytes: 15909
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
<truncated 14872 bytes>
ath.floor(screen.y + (screen.h - h) / 2)
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
490:     scrollSensitivity = state.scrollSensitivity or 0.15,
491:     scrollMomentumScale = state.scrollMomentumScale or 0.3
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

Created At: 2026-08-01T12:51:21-06:00
Completed At: 2026-08-01T12:51:21-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/settings_ui.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -286,6 +286,19 @@
           <div class="slider-val" id="momentumVal">%s</div>
         </div>
       </div>
+
+      <div class="row">
+        <div class="row-label">
+          <strong>Inertia Preset</strong>
+          <span>Scroll momentum behavior</span>
+        </div>
+        <select id="inertiaPreset" onchange="send('setInertiaPreset', this.value)">
+          <option value="direct_raw">Direct (Raw Touch)</option>
+          <option value="linear_damped">Linear Damped</option>
+          <option value="exponential_decay">Exponential Decay</option>
+          <option value="friction_coasting">Friction Coasting</option>
+        </select>
+      </div>
     </div>
 
     <!-- Tempo & Sync -->
@@ -394,6 +394,10 @@
       var valEl = document.getElementById('momentumVal');
       if (valEl) valEl.textContent = parseFloat(s.scrollMomentumScale).toFixed(2);
     }
+    if (s.scrollInertiaPreset !== undefined) {
+      var el = document.getElementById('inertiaPreset');
+      if (el) el.value = s.scrollInertiaPreset;
+    }
   }
 </script>
 </body>
@@ -449,6 +449,9 @@
       local val = tonumber(body.value) or 0.3
       state.scrollMomentumScale = val
       hs.settings.set("qwertyMidi_scrollMomentumScale", val)
+    elseif body.type == "setInertiaPreset" then
+      state.scrollInertiaPreset = body.value
+      hs.settings.set("qwertyMidi_scrollInertiaPreset", state.scrollInertiaPreset)
     elseif body.type == "close" then
       if _G.activeWatchers.settingsWebview then
         _G.activeWatchers.settingsWebview:hide()
@@ -485,7 +485,8 @@
     arpGatePercent = state.arpGatePercent or 80,
     zoomLevel = state.zoomLevel or 1.0,
     scrollSensitivity = state.scrollSensitivity or 0.15,
-    scrollMomentumScale = state.scrollMomentumScale or 0.3
+    scrollMomentumScale = state.scrollMomentumScale or 0.3,
+    scrollInertiaPreset = state.scrollInertiaPreset or "linear_damped"
   }
   local jsonStr = hs.json.encode(s)
   _G.activeWatchers.settingsWebview:evaluateJavaScript("syncState(" .. jsonStr .. ");")
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:51:22-06:00
Completed At: 2026-08-01T12:51:22-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T12:51:23-06:00
Completed At: 2026-08-01T12:51:23-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

The requested inertia preset implementation has been successfully added to `qwerty-midi-hammerspoon`.

### Summary of Changes

*   **`src/config.lua`**:
    *   Added `scrollInertiaPreset` to the state table, defaulting to `"linear_damped"`.
    *   Updated `saveSettings()` to sanitize and persist the `scrollInertiaPreset` setting.
*   **`src/init.lua`**:
    *   Updated the `midiScrollTap` event handler. The `inertiaScale` calculation now dynamically switches based on the active `scrollInertiaPreset` ("direct_raw", "linear_damped", "exponential_decay", or "friction_coasting").
*   **`src/settings_ui.lua`**:
    *   Added a new "Inertia Preset" dropdown in the "Trackpad / Scroll" section.
    *   Wired the dropdown to a `setInertiaPreset` message handler, ensuring settings are updated and saved correctly.
    *   Updated the settings synchronization logic to correctly load and set the dropdown value in the UI.
*   **Execution**:
    *   Ran `bin/bundle_and_reload.sh` to update the bundled `qwerty_midi.lua` and trigger a Hammerspoon reload.

---
