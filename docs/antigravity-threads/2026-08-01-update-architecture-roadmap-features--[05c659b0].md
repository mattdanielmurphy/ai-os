---
title: "Update Architecture Roadmap Features"
date: "2026-08-01"
conversation_id: "05c659b0-226b-422e-858a-4ccb01d1405a"
source: "antigravity"
---

# Update Architecture Roadmap Features

## User

Please update FEATURES.md to add a new strategic goal under `## Future Roadmap & Planned Architecture`:
- **Decoupled Modular Keyboard Controller UI & Engine**: Abstract and decouple the core QWERTY key swallowing eventtap engine, visual canvas grid renderer, and layout manager from MIDI logic. Create a standalone, reusable macOS keyboard UI framework/library that can drive any generic app concept (MIDI controllers, shortcut decks, audio tools, macro launchers, custom keyboards) with clean plugin/adapter bindings.

Keep existing formatting clean and append this item under the Future Roadmap section.

---

## Assistant

Created At: 2026-08-01T00:03:06-06:00
Completed At: 2026-08-01T00:03:06-06:00
Found 1 results
FEATURES.md

Created At: 2026-08-01T00:03:07-06:00
Completed At: 2026-08-01T00:03:07-06:00
File Path: `file:///Users/matt/projects/qwerty-midi-hammerspoon/FEATURES.md`
Total Lines: 42
Total Bytes: 6936
Showing lines 1 to 42
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
<truncated 3535 bytes>
le) to eliminate main thread stalls and hiccupping during rapid note playing or fast arpeggio ticks.
32: - **Correlated Control Key Pair Styling**: Related control keys (e.g. `J`/`K` Transpose, `H`/`L` Root, `G`/`;` Mode, `D`/`F` Octave, `3`/`4` Dir, `5`/`6` Rate, `7`/`8` Gate, `9`/`0` Release, `-`/`=` BPM) share cohesive, understated color accents matching the warm dark HUD theme for effortless visual grouping without dominating note keys.
33: 
34: 
35: - **Instant Pre-Warmed Settings Window**: The Settings window (`Cmd+,` when MIDI mode is active) is pre-warmed as a hidden persistent webview on startup and toggled using instant non-destructive `:show()` / `:hide()` calls with state synchronization, eliminating WebKit window instantiation delays. When MIDI mode is toggled off (`Cmd+Alt+M`), `Cmd+,` is passed through natively to open other macOS app preferences.
36: - **Instant BPM Type-Tempo Mode & Drag Persistence**: Clicking the BPM display immediately opens 'Type tempo' input mode on mouse release. Dragging the BPM up/down dynamically adjusts tempo and commits the target BPM to both the Arpeggiator and active Logic Pro session on mouse release.
37: 
38: ## Future Roadmap & Planned Architecture
39: 
40: - **Independent Arpeggiators per Row**: Top row and bottom row having completely independent arpeggiators (independent direction, rate, gate, pattern step state, while remaining synced to global BPM).
41: - **Dual Independent Instruments / MIDI Channels**: Top row and bottom row functioning as two independent virtual instruments by routing to separate configurable CoreMIDI channels (e.g. MIDI Channel 1 for Top Row, MIDI Channel 2 for Bottom Row) to target different soft synths in DAW/Logic Pro.
42: - **On-Controller Synth / Preset Picker**: Ability to select synths / patch presets directly from the controller UI (via MIDI Program Change messages, Bank Select CC 0/32, or AppleScript/MIDI control surface integration for Logic Pro).
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-01T00:03:09-06:00
Completed At: 2026-08-01T00:03:09-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/qwerty-midi-hammerspoon/FEATURES.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -39,4 +39,5 @@
 
 - **Independent Arpeggiators per Row**: Top row and bottom row having completely independent arpeggiators (independent direction, rate, gate, pattern step state, while remaining synced to global BPM).
 - **Dual Independent Instruments / MIDI Channels**: Top row and bottom row functioning as two independent virtual instruments by routing to separate configurable CoreMIDI channels (e.g. MIDI Channel 1 for Top Row, MIDI Channel 2 for Bottom Row) to target different soft synths in DAW/Logic Pro.
-- **On-Controller Synth / Preset Picker**: Ability to select synths / patch presets directly from the controller UI (via MIDI Program Change messages, Bank Select CC 0/32, or AppleScript/MIDI control surface integration for Logic Pro).
+- **On-Controller Synth / Preset Picker**: Ability to select synths / patch presets directly from the controller UI (via MIDI Program Change messages, Bank Select CC 0/32, or AppleScript/MIDI control surface integration for Logic Pro).
+- **Decoupled Modular Keyboard Controller UI & Engine**: Abstract and decouple the core QWERTY key swallowing eventtap engine, visual canvas grid renderer, and layout manager from MIDI logic. Create a standalone, reusable macOS keyboard UI framework/library that can drive any generic app concept (MIDI controllers, shortcut decks, audio tools, macro launchers, custom keyboards) with clean plugin/adapter bindings.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-01T00:03:10-06:00
Completed At: 2026-08-01T00:03:10-06:00
Message sent to "9c654fd2-c5a5-4680-a4b8-556941afb981".

The requested update has been applied to [FEATURES.md](file:///Users/matt/projects/qwerty-midi-hammerspoon/FEATURES.md). I have appended the new strategic goal, "Decoupled Modular Keyboard Controller UI & Engine," to the `## Future Roadmap & Planned Architecture` section as requested.

---
