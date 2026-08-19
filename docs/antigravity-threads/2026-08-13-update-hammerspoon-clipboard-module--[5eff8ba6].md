---
title: "Update Hammerspoon Clipboard Module"
date: "2026-08-13"
conversation_id: "5eff8ba6-0690-45b1-ad23-5607390c4cc9"
source: "antigravity"
---

# Update Hammerspoon Clipboard Module

## User

Please update /Users/matt/.hammerspoon/modules/clipboard.lua and /Users/matt/.hammerspoon/init.lua:

1. In `/Users/matt/.hammerspoon/modules/clipboard.lua`:
   Set `M.id = "clipboard"` and `M.name = "Clipboard Cleaner"`.
   Remove the top-level call to `M.start()` at line 232 so it doesn't auto-start on require.

2. In `/Users/matt/.hammerspoon/init.lua`:
   Register `clipboard` with ModuleManager: `ModuleManager.register(require("modules.clipboard"))`.

---

## Assistant

The `clipboard` module has been updated and registered as requested.

*   Modified [`clipboard.lua`](file:///Users/matt/.hammerspoon/modules/clipboard.lua) to define `id` and `name` and disable auto-start.
*   Modified [`init.lua`](file:///Users/matt/.hammerspoon/init.lua) to register the module via `ModuleManager`.

---
