---
title: "Update Hammerspoon Settings Script"
date: "2026-08-13"
conversation_id: "13334b95-0ac1-4fc4-a93f-2d4e605a7eb2"
source: "antigravity"
---

# Update Hammerspoon Settings Script

## User

Update /Users/matt/.hammerspoon/modules/right_command_raycast.lua and /Users/matt/projects/hs-rcmd/right_command_raycast.lua to fix the Right Command + Comma settings window launch issue according to the plan:

1. In `openSettingsWebview()`:
   - Configure webview window level and focus:
     ```lua
     if settingsWebview then
         settingsWebview:level(hs.drawing.windowLevels.floating)
         settingsWebview:bringToFront()
         settingsWebview:centerOnScreen()
         settingsWebview:show()
         settingsWebview:focus()
         local cfg = getSettings()
         settingsWebview:evaluateJavaScript("initSettings(" .. hs.json.encode(cfg) .. ")")
         return
     end
     ```
   - When creating `hs.webview.new(...)`:
     ```lua
     settingsWebview:level(hs.drawing.windowLevels.floating)
     settingsWebview:windowTitle("Right Command Settings")
     settingsWebview:bringToFront()
     settingsWebview:centerOnScreen()
     settingsWebview:show()
     settingsWebview:focus()
     ```

2. In the eventtap handler when `keycode == COMMA_KEYCODE or char == ","` is detected:
   - Stop `holdTimer` and `longHoldTimer`.
   - Set `isCancelled = true`, `modeActive = false`, `isHoldingRightCmd = false`, `keyBuffer = {}`.
   - Hide Raycast if it was launched/active:
     ```lua
     local app = getTargetApp()
     if app then app:hide() end
     ```
   - Call `_G.openRightCmdSettings()`.
   - Return `true` to consume the keypress.

Ensure both `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` and `/Users/matt/projects/hs-rcmd/right_command_raycast.lua` are updated identically.

---

## Assistant

The requested updates have been applied to both `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` and `/Users/matt/projects/hs-rcmd/right_command_raycast.lua`. The settings window now properly handles window levels, centering, and focus, and the eventtap handler now correctly resets the state and hides the launcher application when Right Command + Comma is pressed.

---
