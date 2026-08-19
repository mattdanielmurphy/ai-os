---
title: "Fix Hammerspoon Scroll Freeze"
date: "2026-08-01"
conversation_id: "8a1a92d7-b9f8-4450-8fbe-37342fa1bf0a"
source: "antigravity"
---

# Fix Hammerspoon Scroll Freeze

## User

Fix the app freeze / infinite loop in scroll eventtap!

Root cause:
In macOS `hs.eventtap` for `scrollWheel`, `scrollWheelEventScrollPhase` returns `0` when there is NO trackpad momentum phase or when active touch is occurring, BUT macOS generates momentum scroll events with `phase ~= 0` (e.g., phase 128 = momentum Began, phase 256 = momentum Changed, phase 512 = momentum Ended).
When `phase ~= 0`, `deltaY = _G.activeWatchers.scrollVelocity` set `deltaY` to a static non-zero value, but because macOS delivers 50+ momentum events per second, overriding `deltaY` to `scrollVelocity` on every macOS momentum event without scaling it by the native delta or using a timer caused a massive deluge of UI/MIDI updates blocking the main Lua thread!

Simpler, clean fix:
Directly process macOS scroll wheel events natively without synthetic recursion/state corruption!
1. Active touch: `deltaY` is the real macOS trackpad delta. Multiply `deltaY` by `(state.scrollAcceleration or 0.15)`.
2. Momentum phase (`phase ~= 0`): If `state.scrollFrictionalDecay == 0`, drop momentum events completely (`return true`). Otherwise, scale native momentum `deltaY` by `(state.scrollAcceleration or 0.15) * (state.scrollFrictionalDecay or 0.85)`.
3. No infinite synthetic velocity override!

Update `src/init.lua`:
```lua
    local deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventDeltaAxis1) or 0
    if deltaY == 0 then
      deltaY = event:getProperty(hs.eventtap.event.properties.scrollWheelEventPointDeltaAxis1) or 0
    end

    local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
    local accel = state.scrollAcceleration or 0.15

    if phase ~= 0 then
      local decay = state.scrollFrictionalDecay or 0.85
      if decay == 0 then
        return true -- block post-release momentum events completely
      end
      deltaY = deltaY * accel * decay
    else
      deltaY = deltaY * accel
    end
```

Apply this cleanly to `src/init.lua` and run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh`.

---

## Assistant

Created At: 2026-08-01T12:56:15-06:00
Completed At: 2026-08-01T12:56:15-06:00
{"name":"arpeggiator.lua","sizeBytes":"24900"}
{"name":"config.lua","sizeBytes":"32373"}
{"name":"controls.lua","sizeBytes":"39999"}
{"name":"hud.lua","sizeBytes":"31871"}
{"name":"init.lua","sizeBytes":"11997"}
{"name":"midi.lua","sizeBytes":"2621"}
{"name":"settings_ui.lua","sizeBytes":"15932"}
{"name":"transposer.lua","sizeBytes":"3723"}
{"name":"ui_html.lua","sizeBytes":"129170"}
{"name":"ui_html.lua.bak","sizeBytes":"119967"}
{"name":"web","isDir":true}

Summary: This directory contains 1 subdirectories and 10 files.

Created At: 2026-08-01T12:56:16-06:00
Completed At: 2026-08-01T12:56:16-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua`
Total Lines: 327
Total Bytes: 11997
Showing lines 1 to 327
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
<truncated 9968 bytes>
:%M:%S") .. " [WATCHDOG]: " .. msg .. "\n"); f:close() end
274:         
275:         pcall(function()
276:           local h = hud.reloadMidiWebview()
277:           if h then h:show() end
278:           hs.alert.show("UI Auto-Recovered by Watchdog", 2.0)
279:         end)
280:       end
281:     end
282:   end
283: end)
284: 
285: _G.activeWatchers.midiToggleHotkey = hs.hotkey.bind({ "cmd", "alt" }, "M", function()
286:   _G.toggleMidiMode()
287: end)
288: 
289: _G.activeWatchers.midiRefreshHotkey = hs.hotkey.bind({ "cmd", "alt" }, "R", function()
290:   hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5)
291:   hs.notify.new({ title = "QWERTY MIDI", informativeText = "Executing full Hammerspoon hard reload..." }):send()
292:   hs.timer.doAfter(0.1, function() hs.reload() end)
293: end)
294: 
295: if _G.activeWatchers.settingsHotkey then
296:   _G.activeWatchers.settingsHotkey:delete()
297:   _G.activeWatchers.settingsHotkey = nil
298: end
299: 
300: profileLog("Before panicAllChannels")
301: midi.panicAllChannels()
302: 
303: -- Auto-reopen window if it was open when the last reload occurred
304: local wasOpen = hs.settings.get("qwertyMidi_wasOpen")
305: if wasOpen then
306:   profileLog("Auto-reopening controller window (was open before reload)")
307:   hs.timer.doAfter(0.3, function()
308:     local ok, err = pcall(function()
309:       _G.toggleMidiMode(true)
310:     end)
311:     if not ok then
312:       print("QWERTY MIDI: auto-reopen failed: " .. tostring(err))
313:     end
314:   end)
315: end
316: 
317: _G.pingController = function() return hud.pingController() end
318: _G.dumpMidiLogs = function() return hud.dumpMidiLogs() end
319: _G.hardResetController = function() hs.alert.show("⚡ Hard Reloading Hammerspoon...", 1.5); hs.reload() end
320: 
321: profileLog("Init complete!")
322: 
323: return {
324:   toggleMidiMode = _G.toggleMidiMode,
325:   toggleSettingsWindow = settings_ui.toggleSettingsWindow
326: }
327: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T12:56:18-06:00
Completed At: 2026-08-01T12:56:18-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/init.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -68,15 +68,16 @@
 
     -- Scroll handling
     local phase = event:getProperty(hs.eventtap.event.properties.scrollWheelEventScrollPhase) or 0
-    _G.activeWatchers.scrollVelocity = _G.activeWatchers.scrollVelocity or 0
-
-    if phase == 0 then
-      _G.activeWatchers.scrollVelocity = deltaY * (state.scrollAcceleration or 0.15)
+    local accel = state.scrollAcceleration or 0.15
+
+    if phase ~= 0 then
+      local decay = state.scrollFrictionalDecay or 0.85
+      if decay == 0 then
+        return true -- block post-release momentum events completely
+      end
+      deltaY = deltaY * accel * decay
     else
-      if state.scrollFrictionalDecay == 0 then return true end
-      _G.activeWatchers.scrollVelocity = _G.activeWatchers.scrollVelocity * state.scrollFrictionalDecay
-      if math.abs(_G.activeWatchers.scrollVelocity) < 0.01 then return true end
-      deltaY = _G.activeWatchers.scrollVelocity
+      deltaY = deltaY * accel
     end
 
     -- Allow native webview scrolling only when cursor is specifically over a scrollable pane in the HUD
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T12:56:18-06:00
Completed At: 2026-08-01T12:56:18-06:00

				The command completed successfully.
				Output:
				📦 Bundling Hammerspoon modules...
🎨 Synced web UI into /Users/matt/projects/qwerty-midi-hammerspoon/src/ui_html.lua
✅ Bundled 9 Lua modules into /Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua
⚡ Reloading Hammerspoon via AppleScript...

Created At: 2026-08-01T12:56:19-06:00
Completed At: 2026-08-01T12:56:19-06:00
Message sent to "257f4471-7d68-436d-be6c-27574ddf4901".

I have successfully fixed the scroll eventtap issue.

**Changes:**
- Updated `src/init.lua` to remove the synthetic `scrollVelocity` override that was causing infinite loops during macOS momentum scroll events.
- Implemented native processing of scroll events, correctly handling trackpad active touch and momentum phases by applying acceleration and frictional decay directly to the native `deltaY`.
- Executed `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` to apply the changes and reload Hammerspoon.

The app should now handle scrolling smoothly without freezing the UI thread.

---
