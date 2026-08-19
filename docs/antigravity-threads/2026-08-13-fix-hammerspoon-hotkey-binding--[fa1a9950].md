---
title: "Fix Hammerspoon Hotkey Binding"
date: "2026-08-13"
conversation_id: "fa1a9950-2ed6-450b-a8fc-d5e033b5b6d3"
source: "antigravity"
---

# Fix Hammerspoon Hotkey Binding

## User

Fix the Right Command + Comma hotkey binding and scope issues in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

Issues:
1. `openSettingsWebview` was defined as `local function openSettingsWebview()`. We should anchor it to `_G.openRightCmdSettingsWebview` or make it accessible so that calling `hs.hotkey.bind` or eventtap can trigger it reliably.
2. In the eventtap:
   - When Right Command is held down, `flagsChanged` fires first and starts `holdTimer` (100ms) to trigger Raycast.
   - If user presses `,` (keycode 43) while holding Right Command, `isHoldingRightCmd` is true, but `holdTimer` might have already triggered `triggerLauncher()` or might still be pending.
   - Also, `Right Cmd + ,` should be bound via a dedicated `hs.hotkey.bind` OR handled cleanly in the eventtap BEFORE `holdTimer` launches Raycast!
   - Actually, a dedicated `hs.hotkey.new({"cmd"}, ",", function() ... end)` or checking keycode 43 inside `keyDown` tap should work, but wait! In `flagsChanged`, pressing Right Command starts the timer. If user presses `,`, it's a keydown event for keycode 43.
   - In `keyDown`: if `keycode == 43` (Comma):
     - Stop `holdTimer` and `longHoldTimer`.
     - Set `isCancelled = true` and `modeActive = false`.
     - Call `openSettingsWebview()`.
     - Return `true` (consume event).

Also, let's add a global helper `_G.openRightCmdSettings = openSettingsWebview` so it can also be tested via Hammerspoon console or hotkey!

Let's also add a dedicated `hs.hotkey.new({"cmd"}, ",", ...)` anchor in `activeWatchers.rightCmdSettingsHotkey` to ensure `Right Cmd + ,` opens settings even if eventtap keycode matching varies across keyboard layouts!

Let's check:
```lua
activeWatchers.rightCmdSettingsHotkey = hs.hotkey.new({"cmd"}, ",", function()
  openSettingsWebview()
end)
```
Wait, if Right Command is held down, `flags.cmd` is active, so `hs.hotkey.bind({"cmd"}, ",")` or `hs.hotkey.new` will trigger when Cmd (left or right) + `,` is pressed!
Wait! Is `cmd + ,` a standard macOS shortcut fo
<truncated 57 bytes>
"If I do right command + `,` then that should open a settings window for this."

So inside `eventtap` for `keyDown`:
Check if `isHoldingRightCmd` is true (meaning Right Command specifically keycode 54 was pressed) AND keycode is 43 (Comma):
```lua
if isHoldingRightCmd and keycode == COMMA_KEYCODE then
  if holdTimer then holdTimer:stop(); holdTimer = nil end
  if longHoldTimer then longHoldTimer:stop(); longHoldTimer = nil end
  isCancelled = true
  modeActive = false
  openSettingsWebview()
  return true
end
```

Wait, why did `Right Cmd + ,` fail previously?
In the `eventtap` code:
Line 393: `if isHoldingRightCmd then`
Line 394: `if keycode == COMMA_KEYCODE then`
Line 395: `if type == hs.eventtap.event.types.keyDown then`
Line 396: `openSettingsWebview()`
Line 397: `end`
Line 398: `return true`
Line 399: `end`

Wait! On line 412:
`if not isCancelled then`
`if holdTimer then holdTimer:stop() holdTimer = nil triggerLauncher() end`
Wait! Line 412 was executing AFTER line 394 if `keycode ~= COMMA_KEYCODE`.
BUT for `COMMA_KEYCODE` (keycode 43), why didn't line 394 execute?
Because when `flagsChanged` happened for Right Cmd (54), `isHoldingRightCmd` became `true`. Then at 100ms `holdTimer` fired and launched Raycast!
When Raycast launched and took focus, Raycast received focus, or the `eventtap` didn't catch the comma if `COMMA_KEYCODE` on their layout wasn't 43, OR `isHoldingRightCmd` was reset when Raycast took focus!

Let's fix both:
1. `COMMA_KEYCODE`: Also check `event:getCharacters() == ","` in addition to keycode 43! (`keycode == 43 or event:getCharacters() == ","`).
2. Make `_G.openRightCmdSettings = openSettingsWebview` globally exported so the user or script can call `_G.openRightCmdSettings()`.
3. Stop `holdTimer` and `longHoldTimer` immediately when Comma is pressed, cancel Raycast mode, and open settings.

Please write the updated `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

The fix has been applied to `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

### Summary of Changes:
*   **Global Access**: Exported `openSettingsWebview` as `_G.openRightCmdSettings`.
*   **Eventtap Logic**: The `eventtap` now correctly stops `holdTimer` and `longHoldTimer`, sets `isCancelled = true`, and `modeActive = false` when `,` is pressed while holding `Right Command`. Added a check for `event:getCharacters() == ","` to improve compatibility across keyboard layouts.
*   **Hotkey Anchor**: Added `activeWatchers.rightCmdSettingsHotkey` using `hs.hotkey.

---
