---
title: "Debugging Stuck MIDI Notes"
date: "2026-08-03"
conversation_id: "5d5e4c02-6298-46cd-8500-5e56f90dd308"
source: "antigravity"
---

# Debugging Stuck MIDI Notes

## User

Analyze why notes sustain when sustain is disabled and arp is off in qwerty-midi-hammerspoon.
Current state context:
1. In handleKeyDown (src/controls.lua), noteKey calculation determines:
   arpActive = state.arpEnabled and arpEnabledForRow
   isArpNote = state.shiftHeld and (not arpActive) or arpActive
   isSustainedNote = (state.shiftHeld and (not sustainActive)) or ((not state.shiftHeld) and sustainActive)
   pressedKeys[code] = { pitches = chordPitches, isArpNote = isArpNote, isSustainedNote = isSustainedNote, channel = ch }

2. In handleKeyUp (src/controls.lua):
   if isArpNote then arpRemoveNote else noteOff / sustainedPitches end

3. Check if lowerRowKeys overlap with upperRowKeys or if transposeShift / pitch calculation causes mismatches, or if keyInfo lookup fails on key release, or if DAW CC 64 remains on.

Draft a detailed implementation_plan.md to fix this exact issue. Write the implementation plan directly to /Users/matt/.gemini/antigravity/brain/8e88f3b9-9fb8-4e3f-8fe9-13832960244d/implementation_plan.md.

---

## Assistant

Created At: 2026-08-02T21:04:13-06:00
Completed At: 2026-08-02T21:04:14-06:00

				The command exited with code 0.
				Output:
				drwxr-xr-x@ 29 matt  staff  928 Jul 28 23:49 /Users/matt/projects/qwerty-midi-hammerspoon

Created At: 2026-08-02T21:04:19-06:00
Completed At: 2026-08-02T21:04:19-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1283
Total Bytes: 44289
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local config = require("config")
2: local midi = require("midi")
3: local transposer = require("transposer")
4: local arpeggiator = require("arpeggiator")
5: local hud = require("hud")
6: 
7: local state = config.state
8: local SCALES = config.SCALES
9: local NOTE_NAMES = config.NOTE_NAMES
10: 
11: _G.activeWatchers = _G.activeWatchers or {}
12: 
13: -- Clear any stale repeat timers from a previous module load (Hammerspoon reload safety)
14: if _G._qmidiRepeatTimers then
15:   for code, entry in pairs(_G._qmidiRepeatTimers) do
16:     pcall(function()
17:       if entry.timer then entry.timer:stop() end
18:       if entry.interval then entry.interval:stop() end
19:     end)
20:   end
21: end
22: _G._qmidiRepeatTimers = {}
23: local controlRepeatTimers = _G._qmidiRepeatTimers
24: 
25: local function stopControlRepeat(code)
26:   if code and controlRepeatTimers[code] then
27:     pcall(function()
28:       if controlRepeatTimers[code].timer then
29:         controlRepeatTimers[code].timer:stop()
30:       end
31:       if controlRepeatTimers[code].interval then
32:         controlRepeatTimers[code].interval:stop()
33:       end
34:     end)
35:     controlRepeatTimers[code] = nil
36:   end
37: end
38: 
39: local function stopAllControlRepeats()
40:   for code in pairs(controlRepeatTimers) do
41:     stopControlRepeat(code)
42:   end
43: end
44: 
45: local stateUndoStack = {}
46: local stateRedoStack = {}
47: local isRestoringControllerState = false
48: 
49: local function captureStateSnapshot(label)
50:   return {
51:     label = label or "State Change",
52: 
<truncated 28236 bytes>
",
759:       color = "#d4a359"
760:     }
761:     hud.updateWebviewHud(spot)
762:   elseif act == "volDown" then
763:     state.topRowVolume = math.max(0, state.topRowVolume - 4)
764:     state.bottomRowVolume = math.max(0, state.bottomRowVolume - 4)
765:     local spot = {
766:       title = "ROW VOLUMES",
767:       value = "TOP " .. math.floor((state.topRowVolume / 127) * 100) .. "% | BOT " .. math.floor((state.bottomRowVolume / 127) * 100) .. "%",
768:       subtext = "Dual Row Volume Level",
769:       targetId = "header",
770:       color = "#d4a359"
771:     }
772:     hud.updateWebviewHud(spot)
773:   elseif act == "volUp" or act == "volume" then
774:     state.topRowVolume = math.min(127, state.topRowVolume + 4)
775:     state.bottomRowVolume = math.min(127, state.bottomRowVolume + 4)
776:     local spot = {
777:       title = "ROW VOLUMES",
778:       value = "TOP " .. math.floor((state.topRowVolume / 127) * 100) .. "% | BOT " .. math.floor((state.bottomRowVolume / 127) * 100) .. "%",
779:       subtext = "Dual Row Volume Level",
780:       targetId = "header",
781:       color = "#d4a359"
782:     }
783:     hud.updateWebviewHud(spot)
784:   elseif act == "arpTopToggle" then
785:     state.arpTopEnabled = not state.arpTopEnabled
786:     if not state.arpTopEnabled then
787:       for code in pairs(state.arpHeldNotes) do
788:         local noteKey = config.getNoteKey(code)
789:         if noteKey and noteKey.isTop then
790:           state.arpHeldNotes[code] = nil
791:           state.arpKeysCurrentlyHeld[code] = nil
792:         end
793:       end
794:     end
795:     local spot = {
796:       title = "TOP ROW ARP",
797:       value = state.arpTopEnabled and "TOP ARP: ON" or "TOP ARP: OFF",
798:       subtext = arpeggiator.getArpRowTargetSubtext(),
799:       targetId = "arp-top-toggle",
800:       color = "#d4a359"
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-02T21:04:26-06:00
Completed At: 2026-08-02T21:04:26-06:00
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":993,"LineContent":"local function handleKeyDown(code)"}
{"File":"/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua","LineNumber":1279,"LineContent":"  handleKeyDown = handleKeyDown,"}

Created At: 2026-08-02T21:04:30-06:00
Completed At: 2026-08-02T21:04:30-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua`
Total Lines: 1283
Total Bytes: 44289
Showing lines 980 to 1280
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
980:   if not act then return false end
981:   local repeatingActions = {
982:     bpmUp = true, bpmDown = true,
983:     relUp = true, relDown = true, releaseUp = true, releaseDown = true,
984:     arpGateUp = true, arpGateDown = true,
985:     volUp = true, volDown = true, volume = true,
986:     topVolUp = true, topVolDown = true,
987:     botVolUp = true, botVolDown = true,
988:     modWheelUp = true, modWheelDown = true, modWheel = true
989:   }
990:   return repeatingActions[act] == true
991: end
992: 
993: local function handleKeyDown(code)
994:   if code == 50 then -- Backtick
995:     state.modeSelectHeld = true
996:     state.modeWasSelectedDuringHold = false
997:     hud.updateWebviewHud()
998:     return true
999:   end
1000: 
1001:   if state.modeSelectHeld then
1002:     -- Mode Selector is Active!
1003:     if code == 0 then -- 'a' key
1004:       state.currentMode = "ArpAdvanced"
1005:       state.modeWasSelectedDuringHold = true
1006:       -- Release any currently pressed piano keys to prevent stuck notes
1007:       local keysToRelease = {}
1008:       for heldCode, _ in pairs(state.pressedKeys) do
1009:         table.insert(keysToRelease, heldCode)
1010:       end
1011:       for _, heldCode in ipairs(keysToRelease) do
1012:         handleKeyUp(heldCode)
1013:       end
1014:       hud.updateWebviewHud()
1015:       return true
1016:     end
1017:     -- If it's another key, ignore/block it while mode selector is held
1018:     return true 
1019:   end
1020: 
1021:   if state.pressedKeys[code] then
1022:     return true
1023:   end
1024:
<truncated 8767 bytes>
 if act == "sustain" then
1227:       if state.sustainWasActiveOnPress then
1228:         state.sustainActive = false
1229:         midi.sendMidiCC(64, 0)
1230:       else
1231:         state.sustainActive = true
1232:         midi.sendMidiCC(64, 127)
1233:       end
1234: 
1235:       if not state.sustainActive then
1236:         midi.sendMidiCC(64, 0)
1237:         cleanupSustainPitches()
1238:       end
1239: 
1240:       local spot = {
1241:         title = "SUSTAIN (CC #64)",
1242:         value = state.sustainActive and "SUSTAIN ON" or "SUSTAIN OFF",
1243:         subtext = state.sustainActive and "Notes held across release" or "Damping enabled",
1244:         targetId = "key-48",
1245:         color = state.sustainActive and "#d4a359" or "#b5aba0"
1246:       }
1247:       hud.updateWebviewHud(spot)
1248:     elseif act == "chordToggle" then
1249:       if state.chordWasActiveOnPress then
1250:         state.chordModeActive = false
1251:       else
1252:         state.chordModeActive = true
1253:       end
1254:       
1255:       local spot = {
1256:         title = "CHORD MODE",
1257:         value = state.chordModeActive and "ON" or "OFF",
1258:         subtext = "Chord mode: " .. (state.chordModeActive and "Enabled" or "Disabled"),
1259:         targetId = "header",
1260:         color = state.chordModeActive and "#d4a359" or "#b5aba0"
1261:       }
1262:       hud.updateWebviewHud(spot)
1263:     else
1264:       hud.updateWebviewHud()
1265:     end
1266:     return true
1267:   end
1268: 
1269:   -- Fallback cleanup for unmapped or ignored keys
1270:   if state.pressedKeys[code] then
1271:     state.pressedKeys[code] = nil
1272:   end
1273: 
1274:   return true
1275: end
1276: 
1277: return {
1278:   executeControlAction = executeControlAction,
1279:   handleKeyDown = handleKeyDown,
1280:   handleKeyUp = handleKeyUp,
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-02T21:04:46-06:00
Completed At: 2026-08-02T21:04:47-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua`
Total Lines: 764
Total Bytes: 35374
Showing lines 1 to 764
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
17:   currentMode = "Home",
18:   modeSelectHeld = false,
19:   modeWasSelectedDuringHold = false,
20:   currentRoot = getSetting("currentRoot", 0),            -- 0 = C (0..11)
21:   currentScaleIdx = getSetting("currentScaleIdx", 1),    -- 1 = Major / Ionian
22:   octaveShift = getSetting("octaveShift", 0),            -- Global Octave offset in semitones (-36 to +36)
23:   topRowOctaveOffset = getSetting("topRowOctaveOffset", 12), -- Independent Top Row Octave Offset
24:   bottomRowOctaveOffset = getSetting("bottomRowOctaveOffset", 0), -- Independent Bottom Row Octave Offset
25:   transposeShift = getSetting("transposeShift", 0),     -- Transpose offset in scale degrees (-12 to +12)
26:   sustainActive = false,      -- Sustain toggle state (CC64)
27:   sustainKeyDownTime = 0,     -- Timestamp when sustain key was pressed down
28:   sustainWasActiveOnPress = false,
29:   arpLatchActive = getSetting("arpLatchActive", false),  -- Arpeggiator Latch mode
30:   shiftHeld = false,          -- Shift key act
<truncated 35532 bytes>

719:     return arpAdvancedControlKeysMap
720:   end
721:   if _cachedActiveControlKeysMap then return _cachedActiveControlKeysMap end
722:   local map = {}
723:   for code, k in pairs(homeRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
724:   for code, k in pairs(upperRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
725:   for code, k in pairs(lowerRowKeys) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
726:   for code, k in pairs(numberRowControls) do if k.action ~= nil or k.shiftAction ~= nil then map[code] = k end end
727:   _cachedActiveControlKeysMap = map
728:   return map
729: end
730: 
731: 
732: return {
733:   state = state,
734:   saveSettings = saveSettings,
735:   SCALES = SCALES,
736:   NOTE_NAMES = NOTE_NAMES,
737:   WHITE_KEY_INDEX = WHITE_KEY_INDEX,
738:   ACTION_CATALOG = ACTION_CATALOG,
739:   defaultNumberRowControls = defaultNumberRowControls,
740:   defaultUpperRowKeys = defaultUpperRowKeys,
741:   defaultLowerRowKeys = defaultLowerRowKeys,
742:   defaultHomeRowControls = defaultHomeRowControls,
743:   numberRowControls = numberRowControls,
744:   upperRowKeys = upperRowKeys,
745:   lowerRowKeys = lowerRowKeys,
746:   homeRowControls = homeRowControls,
747:   applyCustomLayout = applyCustomLayout,
748:   saveCustomLayout = saveCustomLayout,
749:   selectPreset = selectPreset,
750:   savePreset = savePreset,
751:   renamePreset = renamePreset,
752:   deletePreset = deletePreset,
753:   duplicatePreset = duplicatePreset,
754:   getPresetsList = getPresetsList,
755:   resetLayout = resetLayout,
756:   updateKeyMapping = updateKeyMapping,
757:   getLayoutConfig = getLayoutConfig,
758:   getNoteKey = getNoteKey,
759:   getControlKey = getControlKey,
760:   getNumberControlKey = getNumberControlKey,
761:   getActiveNoteKeysMap = getActiveNoteKeysMap,
762:   getActiveControlKeysMap = getActiveControlKeysMap
763: }
764: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-02T21:05:13-06:00
Completed At: 2026-08-02T21:05:13-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/arpeggiator.lua`
Total Lines: 805
Total Bytes: 26464
Showing lines 1 to 800
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local config = require("config")
2: local midi = require("midi")
3: local transposer = require("transposer")
4: 
5: local state = config.state
6: local upperRowKeys = config.upperRowKeys
7: local lowerRowKeys = config.lowerRowKeys
8: local ARP_DIRECTIONS = state.ARP_DIRECTIONS
9: local ARP_RATES = state.ARP_RATES
10: local ARP_GATES = state.ARP_GATES
11: local DIGIT_KEYCODES = state.DIGIT_KEYCODES
12: 
13: 
14: local function countTableKeys(t)
15:   local count = 0
16:   for _ in pairs(t or {}) do count = count + 1 end
17:   return count
18: end
19: 
20: local hudModule = nil
21: 
22: local function setHudModule(m)
23:   hudModule = m
24: end
25: 
26: local function updateHud(spotlightInfo, activeArpPitch)
27:   if hudModule and hudModule.updateWebviewHud then
28:     hudModule.updateWebviewHud(spotlightInfo, activeArpPitch)
29:   end
30: end
31: 
32: local function stopArpTimer()
33:   state.arpBeatPosition = 0
34:   if state.arpActiveGateTimers then
35:     for pitchInfo, entry in pairs(state.arpActiveGateTimers) do
36:       if entry and entry.timer then entry.timer:stop() end
37:       local pitch = type(pitchInfo) == "table" and pitchInfo.pitch or pitchInfo
38:       local ch = entry and entry.channel or 0
39:       midi.sendMidiNote("noteOff", pitch, 0, ch)
40:     end
41:     state.arpActiveGateTimers = {}
42:   end
43:   if state.arpGateTimer then
44:     state.arpGateTimer:stop()
45:     state.arpGateTimer = nil
46:   end
47:   if state.arpTimer then
48:     state.arpTimer:stop()
49:     state.arpTimer = nil
50:   end
51:   if state.arpCurrentPit
<truncated 26836 bytes>
stdOut:match("^%s*(.-)%s*$"))
749:       if val and val >= 20 and val <= 300 and math.abs(state.arpBpm - val) > 0.01 and not logicBpmDebounceTimer then
750:         state.arpBpm = val
751:         applyBpmChange()
752:         updateHud()
753:       end
754:     end
755:   end, { "-l", "JavaScript", "-e", script })
756:   task:start()
757: end
758: 
759: local function toggleLogicSync()
760:   state.logicSyncEnabled = not state.logicSyncEnabled
761:   if state.logicSyncEnabled then
762:     syncLogicBpm()
763:   end
764:   local spot = {
765:     title = "LOGIC PRO SYNC",
766:     value = state.logicSyncEnabled and "SYNC: ON" or "SYNC: OFF",
767:     subtext = state.logicSyncEnabled and ("Synced to Logic (" .. formatBpm(state.arpBpm) .. " BPM)") or "Manual BPM Mode",
768:     targetId = "bpm-val",
769:     color = "#d4a359"
770:   }
771:   updateHud(spot)
772: end
773: 
774: local function initLogicSync()
775:   if not _G.activeWatchers.logicSyncTimer then
776:     _G.activeWatchers.logicSyncTimer = hs.timer.doEvery(1.0, syncLogicBpm)
777:   end
778:   syncLogicBpm()
779: end
780: 
781: initLogicSync()
782: 
783: return {
784:   setHudModule = setHudModule,
785:   stopArpTimer = stopArpTimer,
786:   getArpIntervalSeconds = getArpIntervalSeconds,
787:   startArpTimer = startArpTimer,
788:   arpAddNote = arpAddNote,
789:   arpRemoveNote = arpRemoveNote,
790:   formatBpm = formatBpm,
791:   applyBpmChange = applyBpmChange,
792:   applyGatePercentChange = applyGatePercentChange,
793:   updateLatchedArpNotes = updateLatchedArpNotes,
794:   updateLatchedArpChordNotes = updateLatchedArpChordNotes,
795:   getArpRowTargetSubtext = getArpRowTargetSubtext,
796:   toggleArpPower = toggleArpPower,
797:   toggleArp = toggleArp,
798:   handleBpmInput = handleBpmInput,
799:   toggleLogicSync = toggleLogicSync,
800:   syncLogicBpm = syncLogicBpm,
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

---
