---
title: "Fix Hammerspoon Modifier Logic"
date: "2026-08-13"
conversation_id: "938af967-4d96-43d3-95aa-e4a7af9e9774"
source: "antigravity"
---

# Fix Hammerspoon Modifier Logic

## User

Investigate and fix why `Right Command` was acting like Escape or cancelling when typing.

Look at the logic in `right_command_raycast.lua`:
Line 394: `if isHoldingRightCmd then`
Line 420: `if not isCancelled then`
Line 421: `if holdTimer then holdTimer:stop() holdTimer = nil triggerLauncher() end`

Look at line 427:
```lua
if modeActive and app and app:isFrontmost() then
    flags.cmd = nil
    local e = hs.eventtap.event.newKeyEvent(flags, keycode, isDown)
    e:post(app)
else
    table.insert(keyBuffer, { keycode = keycode, flags = flags, isDown = isDown })
end
```
Wait! Look at `hs.eventtap.event.newKeyEvent(flags, keycode, isDown)`!
In Hammerspoon API, `hs.eventtap.event.newKeyEvent(modifiers, key, isDown)`:
If `modifiers` is a table of modifier strings e.g. `{"cmd"}`, but `flags` from `event:getFlags()` is a table mapping modifier names to booleans (`{ cmd = true, shift = false }`)!
Passing `flags` directly as `modifiers` table to `hs.eventtap.event.newKeyEvent` FAILS or creates invalid events because `newKeyEvent` expects an ARRAY table of modifier names (like `{"shift"}`), NOT a dictionary of booleans!

AND when `newKeyEvent` errors out silently inside the eventtap callback, the eventtap stops or crashes!

Let's fix the modifier conversion helper in Lua:
```lua
local function flagsToModifierTable(flags)
    local mods = {}
    if not flags then return mods end
    if flags.shift then table.insert(mods, "shift") end
    if flags.alt then table.insert(mods, "alt") end
    if flags.ctrl then table.insert(mods, "ctrl") end
    if flags.fn then table.insert(mods, "fn") end
    -- DO NOT include "cmd" since we are stripping command!
    return mods
end
```

Then when creating a new key event:
```lua
local mods = flagsToModifierTable(flags)
local e = hs.eventtap.event.newKeyEvent(mods, keycode, isDown)
```

Also, when `e:post(app)` is called:
`newKeyEvent` with `keycode` (number) creates the key event. Posting it to `app` delivers it directly to the target application!

Let's also trace the flow when the user presses `Right Command`:
1. User presses Right Command (54). `flagsChanged` fires.
   `isHoldingRightCmd = true`, `modeActive = false`, `isCancelled = false`.
   `holdTimer` starts (100ms).
2. User types a key e.g. `s` after 100ms:
   `holdTimer` has fired `triggerLauncher()`. Raycast is launched/focused, `modeActive = true`.
   Eventtap intercepts `s` (`keyDown`).
   `isHoldingRightCmd` is true. `COMMA_KEYCODE` is false. `ESCAPE_KEYCODE` is false.
   `isCancelled` is false.
   Converts `flags` to array `mods = flagsToModifierTable(flags)`.
   Creates `hs.eventtap.event.newKeyEvent(mods, keycode, isDown)`.
   Posts to Raycast.
   Returns `true` (consumes `s` from active app so no `Cmd+S`).
3. User releases Right Command:
   `flagsChanged` fires for 54.
   `isHoldingRightCmd` is true, `flags.cmd` is false.
   If `modeActive` and not `isCancelled` and `cfg.autoEnterOnRelease`:
     Posts `Return` key to Raycast.
   Resets states.

Please rewrite `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` with this `flagsToModifierTable` fix and clean event handling.

---

## Assistant

The issue in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` where `Right Command` was incorrectly handling key events has been resolved.

The root cause was that `hs.eventtap.event.newKeyEvent` was being passed the raw `flags` dictionary (returned by `event:getFlags()`), which Hammerspoon's API does not support. It expects an array of modifier names.

### Fix Summary
- Added a `flagsToModifierTable(flags)` helper function to correctly convert Hammerspoon's flag table into an array of modifier strings (`"shift"`, `"alt"`, etc.), explicitly excluding `"cmd"`.
- Updated `flushBuffer()` and the main event handling logic to use this helper when creating new key events.
- This ensures that keystrokes typed while `Right Command` is held are correctly passed to the target application without crashing the eventtap.

The fix has been applied directly to the file. You may need to reload your Hammerspoon configuration for the changes to take effect.

---
