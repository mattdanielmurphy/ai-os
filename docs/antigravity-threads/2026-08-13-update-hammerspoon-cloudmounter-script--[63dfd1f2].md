---
title: "Update Hammerspoon CloudMounter Script"
date: "2026-08-13"
conversation_id: "63dfd1f2-b721-4f0c-8e56-d6b43bb52c99"
source: "antigravity"
---

# Update Hammerspoon CloudMounter Script

## User

Update /Users/matt/.hammerspoon/modules/keybindings.lua to wrap the CloudMounter window filter initialization and subscription in `pcall` and defer it slightly with `hs.timer.doAfter` to prevent PID race crashes:

```lua
-- ── Auto-dismiss CloudMounter Upgrade Popup (Focus-Preserving) ─────────────────
hs.timer.doAfter(0.5, function()
  local ok, err = pcall(function()
    activeWatchers.cloudMounterFilter = hs.window.filter.new(function(win)
      local app = win:application()
      if app and app:bundleID() and app:bundleID():find("com.eltima.cloudmounter") then
        return true
      end
      return false
    end)

    activeWatchers.cloudMounterFilter:subscribe(hs.window.filter.windowCreated, function(win)
      local title = win:title()
      local subrole = win:subrole()
      if title == "Upgrade to PRO version required!" or (subrole == "AXDialog" and (title == "" or title == "Window")) then
        hs.timer.doAfter(0.05, function()
          local app = win:application()
          if app then
            hs.eventtap.keyStroke({}, "escape", 0, app)
          end
          notifySubtle("⚡️ CloudMounter PRO nag auto-dismissed", 1.5)
        end)
      end
    end)
  end)

  if not ok then
    print("⚠️  cloudMounterFilter setup deferred/failed: " .. tostring(err))
  end
end)
```

Make sure to edit /Users/matt/.hammerspoon/modules/keybindings.lua cleanly using replace_file_content.

---

## Assistant

The CloudMounter window filter initialization and subscription in `/Users/matt/.hammerspoon/modules/keybindings.lua` has been updated to be wrapped in a `pcall` and deferred using `hs.timer.doAfter(0.5, ...)` to prevent potential PID race condition crashes.

---
