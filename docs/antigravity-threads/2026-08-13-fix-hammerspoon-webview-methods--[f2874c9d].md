---
title: "Fix Hammerspoon Webview Methods"
date: "2026-08-13"
conversation_id: "f2874c9d-af0a-432d-bdc3-6d04353b0bbf"
source: "antigravity"
---

# Fix Hammerspoon Webview Methods

## User

Fix `centerOnScreen` method error in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

In Hammerspoon `hs.webview`:
`settingsWebview` does NOT have a `centerOnScreen()` method!
Instead, center the geometry when creating `rect` or setting frame:

```lua
local screenFrame = hs.screen.mainScreen():frame()
local w, h = 480, 520
local rect = hs.geometry.rect(
    screenFrame.x + (screenFrame.w - w) / 2,
    screenFrame.y + (screenFrame.h - h) / 2,
    w,
    h
)
```

Remove `settingsWebview:centerOnScreen()` line!

Also, remove any other invalid methods like `bringToFront()` if `hs.webview` uses `settingsWebview:show()` / `settingsWebview:focus()`.
Valid `hs.webview` methods:
- `settingsWebview:windowStyle({"titled", "closable"})`
- `settingsWebview:windowTitle("Right Command Settings")`
- `settingsWebview:html(html)`
- `settingsWebview:show()`
- `settingsWebview:focus()`

Please write this fix to `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

The `centerOnScreen` error has been fixed in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`. I removed the invalid `centerOnScreen()` and `bringToFront()` methods, replaced the latter with `settingsWebview:focus()`, and implemented centering by manually calculating the `hs.geometry.rect` based on the main screen's frame before creating the webview.

---
