---
title: "QWERTY MIDI Arpeggiator Fixes"
date: "2026-08-01"
conversation_id: "b80ad57a-a07c-4972-af04-f49e57c4f730"
source: "antigravity"
---

# QWERTY MIDI Arpeggiator Fixes

## User

Write an implementation plan to /Users/matt/.gemini/antigravity/brain/8a68576b-bf2e-41c5-bd4e-152ee6473fd0/implementation_plan.md for fixing the QWERTY MIDI Arpeggiator & Key Control failures.

Contents:
# QWERTY MIDI Arpeggiator & Control Key Recovery Plan

Fixing the infinite key-repeat loop on backtick release, missing number-row control maps, hardcoded HUD keycode checks, and gate timer type errors.

## User Review Required

> [!IMPORTANT]
> The primary fixes are:
> 1. Fixing `handleKeyUp` in `src/controls.lua` so key `50` (backtick) calls `stopControlRepeat(code)` on release, stopping the infinite 80ms `arpToggle` loop.
> 2. Including `numberRowControls` in `getActiveControlKeysMap()` in `src/config.lua`.
> 3. Updating `src/hud.lua` to check action names (`cData.action == "arpToggle"`) and highlight `arpToggle` keys when `state.arpEnabled` is true.
> 4. Updating `src/arpeggiator.lua` gate timer type checks from `type(timer) == "table"` to checking `:stop` or `timer ~= nil`, and storing channel metadata with gate timers.

## Proposed Changes

### Key Controls (`src/controls.lua`)
#### [MODIFY] [src/controls.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/src/controls.lua)
- In `handleKeyUp(code)` (line 1022), ensure `stopControlRepeat(code)` is called when backtick is released before returning.

### Configuration (`src/config.lua`)
#### [MODIFY] [src/config.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/src/config.lua)
- Update `getActiveControlKeysMap()` to iterate and include `numberRowControls`.

### HUD Rendering (`src/hud.lua`)
#### [MODIFY] [src/hud.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua)
- Replace hardcoded keycode checks (`50`, `18`, `19`) with action string matching.
- Add `isArpToggle` check to set `isActiveToggle = true` when `state.arpEnabled` is true.
- Parse integer keycodes from composite keys (`"12_72"`) in row toggle note cleanup.

### Arpeggiator Engine (`src/arpeggiator.lua`)
#### [MODIFY] [src/arpeggiator.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/src/arpeggiator.lua)
- Update gate timer type checks from `type(...) == "table"` to `timer and timer.stop`.
- Store channel metadata in `state.arpActiveGateTimers[pitch]` (`{ timer = t, channel = ch }`) so `stopArpTimer()` and gate changes send `noteOff` on the exact triggering MIDI channel.

### Monolithic Distribution Bundle (`qwerty_midi.lua`)
#### [MODIFY] [qwerty_midi.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua)
- Run `bin/bundle_and_reload.sh` to update `qwerty_midi.lua` and reload Hammerspoon.

## Verification Plan

### Automated Tests
- Syntax check modified files: `luac -p src/controls.lua src/config.lua src/hud.lua src/arpeggiator.lua`.

### Manual Verification
- Execute `bin/bundle_and_reload.sh`.
- Press and release backtick (key `50`); verify `state.arpEnabled` toggles ON/LATCH/OFF cleanly without infinite key repeating.
- Press keys while Arp is enabled; verify arpeggios play smoothly without note choke or hanging notes.
- Check HUD UI tiles; verify Arp toggle key lights up when active.

---

## Assistant

Created At: 2026-07-31T22:18:28-06:00
Completed At: 2026-07-31T22:18:28-06:00
Created file file:///Users/matt/.gemini/antigravity/brain/b80ad57a-a07c-4972-af04-f49e57c4f730/implementation_plan.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
Note: You have just created an artifact and requested user feedback. Stop calling tools to end your turn, and allow the user to review the artifact, approve it, or provide feedback

Created At: 2026-07-31T22:18:28-06:00
Completed At: 2026-07-31T22:18:29-06:00
Message sent to "8a68576b-bf2e-41c5-bd4e-152ee6473fd0".

The implementation plan for the QWERTY MIDI Arpeggiator and Key Control fixes has been created at [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/b80ad57a-a07c-4972-af04-f49e57c4f730/implementation_plan.md) and the parent agent has been notified.

---
