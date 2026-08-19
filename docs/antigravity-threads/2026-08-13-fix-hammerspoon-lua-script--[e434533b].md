---
title: "Fix Hammerspoon Lua Script"
date: "2026-08-13"
conversation_id: "e434533b-ad8a-4f51-8810-ff79d4eb8cea"
source: "antigravity"
---

# Fix Hammerspoon Lua Script

## User

Fix line 238 in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`:

Remove `settingsWebview:windowTitleVisibility("visible")` because `hs.webview` does not have a `windowTitleVisibility` method!

Only call valid `hs.webview` methods:
- `settingsWebview:windowStyle({"titled", "closable"})`
- `settingsWebview:windowTitle("Right Command Settings")`
- `settingsWebview:html(html)`
- `settingsWebview:bringToFront()`
- `settingsWebview:centerOnScreen()`
- `settingsWebview:show()`

Please update `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` to remove line 238.

---

## Assistant

The requested edit has been completed. The line `settingsWebview:windowTitleVisibility("visible")` has been removed from `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---
