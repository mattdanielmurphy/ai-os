# qwerty-midi-hammerspoon: Arpeggiator Gate Length Consistency Fix

## Date: 2026-07-25

## Symptom

Top row notes (QWERTYUIOP[]) and bottom row notes (ZXCVBNM,./') have inconsistent behavior:
- Bottom row notes go through the arpeggiator with gate length control
- Top row notes bypass the arpeggiator, playing as direct MIDI noteOn

## Root Cause

`arpTopEnabled` in `config.lua` defaulted to `false` while `arpBottomEnabled` defaulted to `true`. Since the arpeggiator checks row-specific enable flags before routing notes, top row keys were always sent as direct MIDI while bottom row keys were arpeggiated with gate length.

## Files Changed

### `src/config.lua` line 67
```diff
- arpTopEnabled = getSetting("arpTopEnabled", false),
+ arpTopEnabled = getSetting("arpTopEnabled", true),
```

### `src/controls.lua` line 344 (resetAll handler)
```diff
- state.arpTopEnabled = false
+ state.arpTopEnabled = true
```

## Key Insight: Always Fix Both Code Paths

When changing a default configuration value, you MUST find and fix every place the system resets to defaults:

1. **Initial default** (config.lua or state init) — where the value is set on first load
2. **Factory reset / clear all** (controls.lua resetAll handler) — where the user can restore defaults

These two code paths are often in different files and can diverge. The resetAll path is easy to miss because it's in the controls/actions handler, not the config file.

## Architecture Context

- **Note routing**: `controls.lua handleKeyDown()` checks `isTop` → `arpEnabledForRow` using `state.arpTopEnabled` / `state.arpBottomEnabled`. If the row's arp is disabled, the note is sent as direct MIDI (`midi.sendMidiNote("noteOn", ...)`). If enabled, it goes to `arpeggiator.arpAddNote()` which applies gate length.
- **Arpeggiator tick**: `arpeggiator.lua arpTick()` also re-checks row ARP enable flags for each held note when building the pitch list.
- **Gate application**: Gate ratio is applied uniformly via `getArpIntervalSeconds() * gateRatio` — no row-specific gate logic.
- **Transposer**: `transposer.lua getEffectiveRowVelocity()` uses `isSplitArp` logic to boost top-row volume when only the bottom row is arpeggiated — this is a velocity boost, not a gate inconsistency.
- **Verification**: After changes, run `./bin/bundle_and_reload.sh` to bundle and reload Hammerspoon. Verify with `grep -n 'arpTopEnabled\|arpBottomEnabled' src/config.lua src/controls.lua`.

## User Controls

- Backtick key: Toggles arpeggiator engine on/off (cycles through Off → Latch → On → Off)
- `1` key: Toggles `arpTopEnabled` on/off (independent control)
- `2` key: Toggles `arpBottomEnabled` on/off
- `7`/`8` keys: Adjust gate percent (5% steps, range 5–150%)