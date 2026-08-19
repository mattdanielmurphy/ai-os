---
title: "Fix Hammerspoon Webview Code"
date: "2026-08-13"
conversation_id: "7c0477ea-91e3-4ba9-ae16-cdd2c7653967"
source: "antigravity"
---

# Fix Hammerspoon Webview Code

## User

Fix line 256 in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`:

`settingsWebview` does NOT have a `focus()` method in `hs.webview`.
Simply use `settingsWebview:show()`.
To focus the webview window in Hammerspoon:
`settingsWebview:show()` is all that is required.

Please remove `settingsWebview:focus()` from `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

The invalid `settingsWebview:focus()` call has been removed from `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---
