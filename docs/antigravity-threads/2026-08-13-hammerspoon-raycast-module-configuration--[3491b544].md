---
title: "Hammerspoon Raycast Module Configuration"
date: "2026-08-13"
conversation_id: "3491b544-dedf-4c7c-9e2b-e72396455c85"
source: "antigravity"
---

# Hammerspoon Raycast Module Configuration

## User

Create /Users/matt/.hammerspoon/modules/right_command_raycast.lua and update /Users/matt/.hammerspoon/init.lua to require it.

Requirements for right_command_raycast.lua:
- Anchoring: Anchor eventtap watcher to `_G.activeWatchers.rightCmdRaycastTap`.
- Intercept right command key down and up.
- Code for right cmd: `hs.keycodes.map.cmd` or raw code 54 (right cmd keycode on macOS is 54, left cmd is 55). Specifically check `event:getProperty(hs.eventtap.event.properties.keyboardEventKeycode) == 54` or flags event for right command (flag `cmd` set, raw flags check `flags.cmd` and keycode 54).
- When right cmd DOWN is detected (flagsChanged or keyDown where keycode == 54 and right cmd bit is toggled on):
  1. Trigger Raycast using `hs.application.launchOrFocus("Raycast")` (or `hs.eventtap.keyStroke({"cmd"}, "space")` / `hs.task.new("/usr/bin/open", nil, {"-a", "Raycast"}):start()`). `hs.application.launchOrFocus("Raycast")` or `hs.task.new("/usr/bin/open", nil, {"-a", "Raycast"}):start()` works cleanly. Let's do `hs.application.launchOrFocus("Raycast")`.
  2. Set state `active = true`, `cancelled = false`.
- While `active` is true:
  - If ESCAPE key is pressed (`keyDown`, keycode 53 / `hs.keycodes.map["escape"]`): set `cancelled = true`, `active = false`, and return `true` (consume escape so it cancels the action).
  - All other keys pass through normally (return `false`).
- When right cmd UP is detected (keycode == 54 and right cmd released):
  - If `active` is true and `cancelled` is false:
    - Send Return key (`hs.eventtap.keyStroke({}, "return")`).
  - Reset `active = false`, `cancelled = false`.
- Return `false` for flagsChanged so modifier flag changes pass through as normal unless specified.

Let's double-check macOS keycodes & flags:
Keycode 54 is Right Command. Keycode 55 is Left Command. Keycode 53 is Escape.
In eventtap for flagsChanged and keyDown/keyUp:
```lua
_G.activeWatchers = _G.activeWatchers or {}

local isRightCmdActive = false
local isCancelled = false

local RIGHT_CMD_KEYCODE = 54
local ESCAPE_KEYCODE = 53

activeWatchers.rightCmdRaycastTap = hs.eventtap.new({
  hs.eventtap.event.types.flagsChanged,
  hs.eventtap.event.types.keyDown,
}, function(event)
  local type = event:getType()
  local keycode = event:getProperty(hs.eventtap.event.properties.keyboardEventKeycode)
  
  if type == hs.eventtap.event.types.flagsChanged then
    if keycode == RIGHT_CMD_KEYCODE then
      local flags = event:getFlags()
      if flags.cmd then
        -- Right cmd pressed down
        if not isRightCmdActive then
          isRightCmdActive = true
          isCancelled = false
          hs.application.launchOrFocus("Raycast")
        end
      else
        -- Right cmd released
        if isRightCmdActive then
          if not isCancelled then
            hs.eventtap.keyStroke({}, "return")
          end
          isRightCmdActive = false
          isCancelled = false
        end
      end
    end
  elseif type == hs.eventtap.event.types.keyDown then
    if isRightCmdActive then
      if keycode == ESCAPE_KEYCODE then
        isCancelled = true
        isRightCmdActive = false
        return true -- Consume Escape keypress
      end
    end
  end
  return false
end)

activeWatchers.rightCmdRaycastTap:start()
```

Please write this to `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` and update `/Users/matt/.hammerspoon/init.lua` to add `require("modules.right_command_raycast")`.

---

## Assistant

The requested changes have been completed:

1.  **Module Created**: `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` was created with the eventtap logic to monitor the right command key and trigger Raycast.
2.  **Configuration Updated**: `/Users/matt/.hammerspoon/init.lua` was updated to include `require("modules.right_command_raycast")`.

Your Hammerspoon configuration monitors the `~/.hammerspoon/` directory for changes and should automatically reload to apply these updates.

---
