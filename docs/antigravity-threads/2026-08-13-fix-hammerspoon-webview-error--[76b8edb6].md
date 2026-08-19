---
title: "Fix Hammerspoon Webview Error"
date: "2026-08-13"
conversation_id: "76b8edb6-0239-4b5b-acba-6edb1e2533d7"
source: "antigravity"
---

# Fix Hammerspoon Webview Error

## User

Remove `settingsWebview:focus()` on line 31 of `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

`settingsWebview` does NOT have a `focus()` method! Line 31 has `settingsWebview:focus()`, which throws an error when `openRightCmdSettings` is called if the webview was already instantiated!

Replace lines 29-35:
```lua
if settingsWebview then
    settingsWebview:show()
    local cfg = getSettings()
    settingsWebview:evaluateJavaScript("initSettings(" .. hs.json.encode(cfg) .. ")")
    return
end
```

Please update `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

The `settingsWebview:focus()` call has been removed from `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---
