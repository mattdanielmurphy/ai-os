---
title: "Update MIDI Note Functions"
date: "2026-08-03"
conversation_id: "a84efff6-b23e-4ad9-a596-a1a36cf66fbc"
source: "antigravity"
---

# Update MIDI Note Functions

## User

In /Users/matt/projects/qwerty-midi-hammerspoon/src/midi.lua:

1. Update `sendMidiNote` to emit both `noteOff` and `noteOn` with velocity 0 when sending Note Off, so all legacy/DAW synths immediately damp note envelopes regardless of status byte parsing:
```lua
local function sendMidiNote(cmd, noteNum, vel, channel)
  if type(noteNum) == "table" then
    channel = channel or noteNum.channel
    noteNum = noteNum.pitch
  end
  if not noteNum or type(noteNum) ~= "number" or noteNum < 0 or noteNum > 127 then return end
  local dev = getMidiDevice()
  if dev then
    local ch = channel or 0
    if cmd == "noteOff" or (cmd == "noteOn" and vel == 0) then
      dev:sendCommand("noteOff", { note = noteNum, velocity = 0, channel = ch })
      dev:sendCommand("noteOn", { note = noteNum, velocity = 0, channel = ch })
    else
      dev:sendCommand("noteOn", { note = noteNum, velocity = vel, channel = ch })
    end
  end
end
```

2. Add `sendSustainCC(val)` to broadcast CC 64 to all 16 MIDI channels (`0..15`):
```lua
local function sendSustainCC(val)
  local dev = getMidiDevice()
  if not dev then return end
  for ch = 0, 15 do
    dev:sendCommand("controlChange", { controllerNumber = 64, controllerValue = val, channel = ch })
  end
end
```

3. Export `sendSustainCC` in return table:
```lua
return {
  getMidiDevice = getMidiDevice,
  sendMidiNote = sendMidiNote,
  sendMidiCC = sendMidiCC,
  sendSustainCC = sendSustainCC,
  panicAllChannels = panicAllChannels
}
```

Apply these edits using replace_file_content.

---

## Assistant

Created At: 2026-08-03T02:04:07-06:00
Completed At: 2026-08-03T02:04:07-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/src/midi.lua`
Total Lines: 77
Total Bytes: 2621
Showing lines 1 to 77
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: local hsMidi = require("hs.midi")
2: 
3: _G.activeWatchers = _G.activeWatchers or {}
4: 
5: local function getMidiDevice()
6:   if _G.activeWatchers.midiDevice then return _G.activeWatchers.midiDevice end
7: 
8:   local devices = hsMidi.devices() or {}
9:   local virtualSources = hsMidi.virtualSources() or {}
10: 
11:   for _, devName in ipairs(devices) do
12:     if string.find(devName, "IAC") or string.find(devName, "Bus") then
13:       _G.activeWatchers.midiDevice = hsMidi.new(devName)
14:       return _G.activeWatchers.midiDevice
15:     end
16:   end
17: 
18:   for _, devName in ipairs(virtualSources) do
19:     if string.find(devName, "IAC") or string.find(devName, "Bus") then
20:       _G.activeWatchers.midiDevice = hsMidi.newVirtualSource(devName)
21:       return _G.activeWatchers.midiDevice
22:     end
23:   end
24: 
25:   if #devices > 0 then
26:     _G.activeWatchers.midiDevice = hsMidi.new(devices[1])
27:   elseif #virtualSources > 0 then
28:     _G.activeWatchers.midiDevice = hsMidi.newVirtualSource(virtualSources[1])
29:   end
30: 
31:   return _G.activeWatchers.midiDevice
32: end
33: 
34: local function sendMidiNote(cmd, noteNum, vel, channel)
35:   if type(noteNum) == "table" then
36:     channel = channel or noteNum.channel
37:     noteNum = noteNum.pitch
38:   end
39:   if not noteNum or type(noteNum) ~= "number" or noteNum < 0 or noteNum > 127 then return end
40:   local dev = getMidiDevice()
41:   if dev then
42:     dev:sendCommand(cmd, { note = noteNum, velocity = vel, channel = channel or 0 })
43:   end
44: end
45: 
46: local function sendMidiCC(controllerNum, val, channel)
47:   local dev = getMidiDevice()
48:   if dev then
49:     dev:sendCommand("controlChange", { controllerNumber = controllerNum, controllerValue = val, channel = channel or 0 })
50:   end
51: end
52: 
53: local function panicAllChannels()
54:   local dev = getMidiDevice()
55:   if not dev then return end
56: 
57:   for ch = 0, 15 do
58:     -- Turn off sustain, all sound, all notes, and reset controllers across all channels
59:     dev:sendCommand("controlChange", { controllerNumber = 64, controllerValue = 0, channel = ch })
60:     dev:sendCommand("controlChange", { controllerNumber = 120, controllerValue = 0, channel = ch })
61:     dev:sendCommand("controlChange", { controllerNumber = 123, controllerValue = 0, channel = ch })
62:     dev:sendCommand("controlChange", { controllerNumber = 121, controllerValue = 0, channel = ch })
63:     -- Send Note Off for all 128 pitches on each channel to ensure synths ignore/bypass CC #64 or CC #123 release held notes
64:     for note = 0, 127 do
65:       dev:sendCommand("noteOff", { note = note, velocity = 0, channel = ch })
66:     end
67:   end
68: end
69: 
70: return {
71:   getMidiDevice = getMidiDevice,
72:   sendMidiNote = sendMidiNote,
73:   sendMidiCC = sendMidiCC,
74:   panicAllChannels = panicAllChannels
75: }
76: 
77: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-03T02:04:09-06:00
Completed At: 2026-08-03T02:04:09-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/src/midi.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -39,7 +39,21 @@
   if not noteNum or type(noteNum) ~= "number" or noteNum < 0 or noteNum > 127 then return end
   local dev = getMidiDevice()
   if dev then
-    dev:sendCommand(cmd, { note = noteNum, velocity = vel, channel = channel or 0 })
+    local ch = channel or 0
+    if cmd == "noteOff" or (cmd == "noteOn" and vel == 0) then
+      dev:sendCommand("noteOff", { note = noteNum, velocity = 0, channel = ch })
+      dev:sendCommand("noteOn", { note = noteNum, velocity = 0, channel = ch })
+    else
+      dev:sendCommand("noteOn", { note = noteNum, velocity = vel, channel = ch })
+    end
+  end
+end
+
+local function sendSustainCC(val)
+  local dev = getMidiDevice()
+  if not dev then return end
+  for ch = 0, 15 do
+    dev:sendCommand("controlChange", { controllerNumber = 64, controllerValue = val, channel = ch })
   end
 end
 
@@ -70,6 +70,7 @@
   getMidiDevice = getMidiDevice,
   sendMidiNote = sendMidiNote,
   sendMidiCC = sendMidiCC,
+  sendSustainCC = sendSustainCC,
   panicAllChannels = panicAllChannels
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-03T02:04:10-06:00
Completed At: 2026-08-03T02:04:10-06:00
Message sent to "8e88f3b9-9fb8-4e3f-8fe9-13832960244d".

OK. I have updated `/Users/matt/projects/qwerty-midi-hammerspoon/src/midi.lua` as requested.

---
