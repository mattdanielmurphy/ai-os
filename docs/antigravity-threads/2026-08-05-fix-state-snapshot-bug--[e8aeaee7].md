---
title: "Fix State Snapshot Bug"
date: "2026-08-05"
conversation_id: "e8aeaee7-2c6b-4020-91ba-2cbe1876f321"
source: "antigravity"
---

# Fix State Snapshot Bug

## User

Edit `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` using `replace_file_content`.

The current applyStateSnapshot function has a bug: it compares snap values to state values AFTER state was already overwritten with snap values, so the comparison is always equal. Fix by capturing the old values before overwriting.

StartLine: 80
EndLine: 115
TargetContent:
local function applyStateSnapshot(snap)
  isRestoringControllerState = true

  state.currentRoot = snap.currentRoot
  state.currentScaleIdx = snap.currentScaleIdx
  state.octaveShift = snap.octaveShift
  state.topRowOctaveOffset = snap.topRowOctaveOffset
  state.bottomRowOctaveOffset = snap.bottomRowOctaveOffset or 0
  state.transposeShift = snap.transposeShift
  state.topRowVolume = snap.topRowVolume
  state.bottomRowVolume = snap.bottomRowVolume
  state.arpEnabled = snap.arpEnabled
  state.arpLatchActive = snap.arpLatchActive
  state.arpDirectionIdx = snap.arpDirectionIdx
  state.arpRateIdx = snap.arpRateIdx
  state.arpGatePercent = snap.arpGatePercent
  state.arpBpm = snap.arpBpm
  state.arpTopEnabled = snap.arpTopEnabled
  state.arpBottomEnabled = snap.arpBottomEnabled
  state.ccStates[1] = snap.modWheel
  
  if snap.sustainActive ~= nil then state.sustainActive = snap.sustainActive end
  if snap.chordModeActive ~= nil then state.chordModeActive = snap.chordModeActive end

  arpeggiator.updateLatchedArpNotes()
  if snap.arpBpm ~= state.arpBpm or snap.arpRateIdx ~= state.arpRateIdx then
    arpeggiator.applyBpmChange()
  end
  if snap.arpGatePercent ~= state.arpGatePercent then
    arpeggiator.applyGatePercentChange()
  end
  midi.sendMidiCC(1, snap.modWheel)

  isRestoringControllerState = false
  config.saveSettings()
end

ReplacementContent:
local function applyStateSnapshot(snap)
  isRestoringControllerState = true

  -- Capture current values before overwriting so we can skip no-op arp restarts
  local prevBpm = state.arpBpm
  local prevRateIdx = state.arpRateIdx
  local prevGatePercent = state.arpGatePercent

  state.currentRoot = snap.currentRoot
  state.currentScaleIdx = snap.currentScaleIdx
  state.octaveShift = snap.octaveShift
  state.topRowOctaveOffset = snap.topRowOctaveOffset
  state.bottomRowOctaveOffset = snap.bottomRowOctaveOffset or 0
  state.transposeShift = snap.transposeShift
  state.topRowVolume = snap.topRowVolume
  state.bottomRowVolume = snap.bottomRowVolume
  state.arpEnabled = snap.arpEnabled
  state.arpLatchActive = snap.arpLatchActive
  state.arpDirectionIdx = snap.arpDirectionIdx
  state.arpRateIdx = snap.arpRateIdx
  state.arpGatePercent = snap.arpGatePercent
  state.arpBpm = snap.arpBpm
  state.arpTopEnabled = snap.arpTopEnabled
  state.arpBottomEnabled = snap.arpBottomEnabled
  state.ccStates[1] = snap.modWheel
  
  if snap.sustainActive ~= nil then state.sustainActive = snap.sustainActive end
  if snap.chordModeActive ~= nil then state.chordModeActive = snap.chordModeActive end

  arpeggiator.updateLatchedArpNotes()
  if snap.arpBpm ~= prevBpm or snap.arpRateIdx ~= prevRateIdx then
    arpeggiator.applyBpmChange()
  end
  if snap.arpGatePercent ~= prevGatePercent then
    arpeggiator.applyGatePercentChange()
  end
  midi.sendMidiCC(1, snap.modWheel)

  isRestoringControllerState = false
  config.saveSettings()
end

AllowMultiple: false

---

## Assistant

Created At: 2026-08-04T22:39:13-06:00
Completed At: 2026-08-04T22:39:13-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -80,6 +80,11 @@
 local function applyStateSnapshot(snap)
   isRestoringControllerState = true
 
+  -- Capture current values before overwriting so we can skip no-op arp restarts
+  local prevBpm = state.arpBpm
+  local prevRateIdx = state.arpRateIdx
+  local prevGatePercent = state.arpGatePercent
+
   state.currentRoot = snap.currentRoot
   state.currentScaleIdx = snap.currentScaleIdx
   state.octaveShift = snap.octaveShift
@@ -101,10 +101,10 @@
   if snap.chordModeActive ~= nil then state.chordModeActive = snap.chordModeActive end
 
   arpeggiator.updateLatchedArpNotes()
-  if snap.arpBpm ~= state.arpBpm or snap.arpRateIdx ~= state.arpRateIdx then
-    arpeggiator.applyBpmChange()
-  end
-  if snap.arpGatePercent ~= state.arpGatePercent then
+  if snap.arpBpm ~= prevBpm or snap.arpRateIdx ~= prevRateIdx then
+    arpeggiator.applyBpmChange()
+  end
+  if snap.arpGatePercent ~= prevGatePercent then
     arpeggiator.applyGatePercentChange()
   end
   midi.sendMidiCC(1, snap.modWheel)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-04T22:39:14-06:00
Completed At: 2026-08-04T22:39:14-06:00
Message sent to "fd9660db-ab17-45eb-9be1-3e86cb42ee52".

I have fixed the `applyStateSnapshot` function in `/Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua` by capturing the `arpBpm`, `arpRateIdx`, and `arpGatePercent` values before the state is updated, ensuring the comparison logic correctly detects changes.

---
