---
title: "Update Features Documentation Roadmap"
date: "2026-08-01"
conversation_id: "7722e51e-bfdf-476e-b64a-b82627728523"
source: "antigravity"
---

# Update Features Documentation Roadmap

## User

Please update FEATURES.md to add a new section or bullet points capturing future roadmap/planned features:
1. Independent Arpeggiators per Row: Top row and bottom row having completely independent arpeggiators (independent direction, rate, gate, pattern step state, while remaining synced to global BPM).
2. Dual Independent Instruments / MIDI Channels: Top row and bottom row functioning as two independent virtual instruments by routing to separate configurable CoreMIDI channels (e.g. MIDI Channel 1 for Top Row, MIDI Channel 2 for Bottom Row) to target different soft synths in DAW/Logic Pro.
3. On-Controller Synth / Preset Picker: Ability to select synths / patch presets directly from the controller UI (via MIDI Program Change messages, Bank Select CC 0/32, or AppleScript/MIDI control surface integration for Logic Pro).

Format these cleanly under a new section `## Future Roadmap & Planned Architecture` at the bottom of FEATURES.md. Keep existing formatting intact.

---

## Assistant

Created At: 2026-08-01T00:01:26-06:00
Completed At: 2026-08-01T00:01:26-06:00
{"name":".DS_Store","sizeBytes":"8196"}
{"name":".claude","isDir":true}
{"name":".devtool","isDir":true}
{"name":".git","isDir":true}
{"name":".gitignore","sizeBytes":"324"}
{"name":"AG_CONTEXT.md","sizeBytes":"1983"}
{"name":"DEVELOPMENT_JOURNAL.md","sizeBytes":"13307"}
{"name":"FEATURES.md","sizeBytes":"6161"}
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
{"name":"qwerty_midi.lua","sizeBytes":"288773"}
{"name":"src","isDir":true}
{"name":"src-tauri","isDir":true}
{"name":"test_logic_ui.scpt","sizeBytes":"2306"}
{"name":"test_profile.lua","sizeBytes":"297"}
{"name":"test_set_bpm.lua","sizeBytes":"1932"}
{"name":"tmp","isDir":true}
{"name":"tmp_test_applescript.scpt","sizeBytes":"331"}
{"name":"vite.config.js","sizeBytes":"213"}

Summary: This directory contains 12 subdirectories and 15 files.

Created At: 2026-08-01T00:01:27-06:00
Completed At: 2026-08-01T00:01:27-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/FEATURES.md`
Total Lines: 36
Total Bytes: 6161
Showing lines 1 to 36
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # qwerty-midi-hammerspoon Features
2: 
3: - **Modal QWERTY MIDI Controller**: Swallows keys in active mode to trigger CoreMIDI noteOn/noteOff and CC commands.
4: - **HTML/CSS Canvas HUD**: Floating, zoomable HUD (`Cmd + Alt + M`) displaying scale, root note, active notes, and control statuses.
5: - **Fraunces Typography & Dark Neutral Theme**: Warm charcoal aesthetic (`rgba(24, 22, 20, 0.96)`) using the Inter/Fraunces typography.
6: - **Interactive UI Key Clicks**: Clicking on-screen keys (notes or controls) triggers native MIDI notes and parameter adjustments.
7: - **Dropdown Root Selection**: Clickable `<select>` badge in HUD header to select root note (C through B) directly from a styled dropdown.
8: - **Draggable Mode Slider**: Interactive scale mode slider in HUD header allowing direct drag and click selection across all 9 modes/scales.
9: - **Dedicated Sustain & Arp Latch Keys**:
10:   - **Sustain (`Tab`)**: Dedicated control for MIDI CC #64. Features dual action: **Tap** to toggle sustain ON/OFF, or **Hold** (>0.25s) for momentary pedal sustain. Shown on the upper row of the visual keyboard grid.
11:   - **Arp Latch (`A`)**: Dedicated control for Arpeggiator pattern latching. Features dual action: **Tap** to toggle latch ON/OFF, or **Hold** (>0.25s) for momentary pattern latching.
12: - **Built-in Arpeggiator**: Integrated arpeggiator engine with separate ON/OFF toggle, dropdown direction selector (UP, DOWN, UP-DOWN, RANDOM), time division rate dropdown (1/4 to 1/16T), note length gate duration dropdown (25% to 100%), selectable BPM speeds (freeform text inpu
<truncated 2736 bytes>
ysically held keys remain active.
29: - **Latched Arp Chord Visual Indicators**: When `ARP: LATCH` is active, all notes comprising the latched chord are clearly highlighted with a subtle blue cyan background glow, border highlight, and upper-corner dot indicator (`•`). Active arpeggiated step notes pulse bright yellow over their latched dot marker as each tick plays.
30: - **Logic Pro Session BPM Sync**: Real-time auto-synchronization between active Logic Pro session BPM and the Arpeggiator engine via non-blocking background AppleScript task with an interactive header `SYNC: ON/OFF` toggle button.
31: - **Ultra-Low Latency & 60 FPS Batched HUD Rendering**: Decoupled instant CoreMIDI note transmission from WebKit IPC visual updates. Visual HUD rendering is batched at ~60 FPS (16ms throttle) to eliminate main thread stalls and hiccupping during rapid note playing or fast arpeggio ticks.
32: - **Correlated Control Key Pair Styling**: Related control keys (e.g. `J`/`K` Transpose, `H`/`L` Root, `G`/`;` Mode, `D`/`F` Octave, `3`/`4` Dir, `5`/`6` Rate, `7`/`8` Gate, `9`/`0` Release, `-`/`=` BPM) share cohesive, understated color accents matching the warm dark HUD theme for effortless visual grouping without dominating note keys.
33: 
34: 
35: - **Instant Pre-Warmed Settings Window**: The Settings window (`Cmd+,` when MIDI mode is active) is pre-warmed as a hidden persistent webview on startup and toggled using instant non-destructive `:show()` / `:hide()` calls with state synchronization, eliminating WebKit window instantiation delays. When MIDI mode is toggled off (`Cmd+Alt+M`), `Cmd+,` is passed through natively to open other macOS app preferences.
36: - **Instant BPM Type-Tempo Mode & Drag Persistence**: Clicking the BPM display immediately opens 'Type tempo' input mode on mouse release. Dragging the BPM up/down dynamically adjusts tempo and commits the target BPM to both the Arpeggiator and active Logic Pro session on mouse release.
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T00:01:29-06:00
Completed At: 2026-08-01T00:01:33-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/FEATURES.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -33,4 +33,10 @@
 
 
 - **Instant Pre-Warmed Settings Window**: The Settings window (`Cmd+,` when MIDI mode is active) is pre-warmed as a hidden persistent webview on startup and toggled using instant non-destructive `:show()` / `:hide()` calls with state synchronization, eliminating WebKit window instantiation delays. When MIDI mode is toggled off (`Cmd+Alt+M`), `Cmd+,` is passed through natively to open other macOS app preferences.
-- **Instant BPM Type-Tempo Mode & Drag Persistence**: Clicking the BPM display immediately opens 'Type tempo' input mode on mouse release. Dragging the BPM up/down dynamically adjusts tempo and commits the target BPM to both the Arpeggiator and active Logic Pro session on mouse release.
+- **Instant BPM Type-Tempo Mode & Drag Persistence**: Clicking the BPM display immediately opens 'Type tempo' input mode on mouse release. Dragging the BPM up/down dynamically adjusts tempo and commits the target BPM to both the Arpeggiator and active Logic Pro session on mouse release.
+
+## Future Roadmap & Planned Architecture
+
+- **Independent Arpeggiators per Row**: Top row and bottom row having completely independent arpeggiators (independent direction, rate, gate, pattern step state, while remaining synced to global BPM).
+- **Dual Independent Instruments / MIDI Channels**: Top row and bottom row functioning as two independent virtual instruments by routing to separate configurable CoreMIDI channels (e.g. MIDI Channel 1 for Top Row, MIDI Channel 2 for Bottom Row) to target different soft synths in DAW/Logic Pro.
+- **On-Controller Synth / Preset Picker**: Ability to select synths / patch presets directly from the controller UI (via MIDI Program Change messages, Bank Select CC 0/32, or AppleScript/MIDI control surface integration for Logic Pro).
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-01T00:01:34-06:00
Completed At: 2026-08-01T00:01:34-06:00
Message sent to "9c654fd2-c5a5-4680-a4b8-556941afb981".

The requested updates to `FEATURES.md` have been completed successfully. I have added the new section `## Future Roadmap & Planned Architecture` at the end of the file with the specified roadmap items.

---
