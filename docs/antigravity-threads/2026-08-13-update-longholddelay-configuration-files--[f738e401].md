---
title: "Update LongHoldDelay Configuration Files"
date: "2026-08-13"
conversation_id: "f738e401-7eb9-4601-b94a-31c1b4aa8b47"
source: "antigravity"
---

# Update LongHoldDelay Configuration Files

## User

Update longHoldDelay default from 4000 (4.0s) to 2000 (2.0s) in both `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` and `/Users/matt/projects/hs-rcmd/right_command_raycast.lua`.

Look for:
```lua
local defaults = {
    initialHoldDelay = 100,
    longHoldDelay = 4000,
```
and change `longHoldDelay = 4000` to `longHoldDelay = 2000`.

Also update any comments or defaults UI sliders to reflect 2000 ms (2.0s). Use replace_file_content to update both files cleanly.

---

## Assistant

The `longHoldDelay` has been updated from 4000 (4.0s) to 2000 (2.0s) in both requested files. The UI settings and slider limits have also been updated to match this change.

---
