---
title: "Fix Hammerspoon Eventtap Logic"
date: "2026-08-13"
conversation_id: "bde17c24-b844-44db-a5ec-c047cf7855de"
source: "antigravity"
---

# Fix Hammerspoon Eventtap Logic

## User

Fix `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`:

Problem analysis:
1. Lines 445-448 added `activeWatchers.rightCmdRaycastHotkey = hs.hotkey.new({"cmd"}, ",", ...)`! Because `cmd + ,` is registered globally with `hs.hotkey.new`, ANY press of `Cmd + ,` (including Left Command + Comma, which is standard in macOS for app preferences!) triggers `openSettingsWebview()` AND intercepts `cmd + ,` globally!
2. Furthermore, in the eventtap (line 395): `if keycode == COMMA_KEYCODE or char == "," then` - `char` was NOT defined! (`char` is nil, raising a Lua runtime error inside the eventtap loop, which causes the eventtap to abort or crash silently, causing Right Command to fall back/cancel like Escape!).

Fixes:
1. REMOVE `activeWatchers.rightCmdSettingsHotkey` completely! We ONLY want `Right Command + ,` to open the settings window. Standard `Left Cmd + ,` should function normally as standard macOS Preferences.
2. In eventtap:
   - Calculate `local char = event:getCharacters()`.
   - On `flagsChanged` for Right Command (54):
     - When Right Cmd goes down (`flags.cmd` and `keycode == 54`):
       Check `isHoldingRightCmd`.
     - When Right Cmd goes UP (`not flags.cmd`):
       If `isHoldingRightCmd`:
         - If `modeActive` and not `isCancelled` and `cfg.autoEnterOnRelease`:
           - Send `Return`.
         - Reset all state variables (`isHoldingRightCmd = false`, `modeActive = false`, `isCancelled = false`, `keyBuffer = {}`).
   - In `keyDown` / `keyUp`:
     - `if isHoldingRightCmd then`:
       - Check if keycode is 43 (Comma) or `char == ","`:
         - Stop `holdTimer` & `longHoldTimer`.
         - Set `isCancelled = true`, `modeActive = false`, `isHoldingRightCmd = false`.
         - Call `_G.openRightCmdSettings()`.
         - Return `true` (consume event).
       - Check if keycode is 53 (Escape):
         - Stop `holdTimer` & `longHoldTimer`.
         - Set `isCancelled = true`, `modeActive = false`.
         - Return `true` (consume Escape).
       - For other keys:
         - Strip `cmd` flag, forward key to target app or buffer, return `true`.

Please write the clean, fixed implementation to `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

The requested fixes have been applied to `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

The global `Cmd + ,` hotkey has been removed to restore normal macOS preferences functionality, and the `eventtap` logic has been corrected to handle the `char` variable properly, preventing crashes.

---
