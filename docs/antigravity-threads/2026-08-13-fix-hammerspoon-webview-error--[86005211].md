---
title: "Fix Hammerspoon Webview Error"
date: "2026-08-13"
conversation_id: "86005211-787d-4349-9015-53b3157aef24"
source: "antigravity"
---

# Fix Hammerspoon Webview Error

## User

Fix the line 237 error in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua` where `settingsWebview:title("Right Command Settings")` failed with `ERROR: incorrect number of arguments. Expected 1, got 2`.

In Hammerspoon, `hs.webview:windowTitle([title])` or `hs.webview:windowTitleVisibility("visible")` should be used instead of calling `webview:title(...)` directly!
Or set windowTitle: `settingsWebview:windowTitle("Right Command Settings")`.

Also, let's fix the `rcmd + ,` hotkey logic so that pressing `,` (Comma) while holding Right Command opens the settings window WITHOUT launching Raycast!

Root cause of why Raycast was opening instead of settings:
When Right Command goes down, `flagsChanged` fires and immediately schedules `holdTimer` (100ms) to launch Raycast!
When the user presses `,` (Comma) 50ms later:
1. The `keyDown` event for Comma comes in.
2. In the `keyDown` handler, if it detects `,` (keycode 43 or character `,`), it MUST:
   - Immediately stop and clear `holdTimer` (`if holdTimer then holdTimer:stop(); holdTimer = nil end`)
   - Immediately stop and clear `longHoldTimer` (`if longHoldTimer then longHoldTimer:stop(); longHoldTimer = nil end`)
   - Set `isCancelled = true`, `modeActive = false`, `isHoldingRightCmd = false`
   - Open settings (`_G.openRightCmdSettings()`)
   - Return `true` (consume event so `,` is NOT sent to active app or Raycast).

Let's review the code in `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`:

```lua
_G.activeWatchers = _G.activeWatchers or {}

local settingsKey = "rightCmdRaycast_settings"

local defaults = {
    initialHoldDelay = 100,
    longHoldDelay = 4000,
    showLongHoldIcon = true,
    targetApp = "Raycast",
    autoEnterOnRelease = true
}

local function getSettings()
    local s = hs.settings.get(settingsKey)
    if type(s) ~= "table" then return defaults end
    for k, v in pairs(defaults) do
        if s[k] == nil then s[k] = v end
    end
    return s
end

local function saveSettings(settings)
    hs.settings.set(se
<truncated 13227 bytes>
   end
        return false
    end

    if isHoldingRightCmd then
        -- Check for Comma (keycode 43 or character ',')
        local char = event:getCharacters()
        if keycode == COMMA_KEYCODE or char == "," then
            if type == hs.eventtap.event.types.keyDown then
                if holdTimer then holdTimer:stop(); holdTimer = nil end
                if longHoldTimer then longHoldTimer:stop(); longHoldTimer = nil end
                isCancelled = true
                modeActive = false
                isHoldingRightCmd = false
                keyBuffer = {}
                _G.openRightCmdSettings()
            end
            return true -- Consume event so Raycast does NOT open!
        end

        if keycode == ESCAPE_KEYCODE then
            if type == hs.eventtap.event.types.keyDown then
                if holdTimer then holdTimer:stop(); holdTimer = nil end
                if longHoldTimer then longHoldTimer:stop(); longHoldTimer = nil end
                isCancelled = true
                modeActive = false
                keyBuffer = {}
            end
            return true
        end

        if not isCancelled then
            if holdTimer then
                holdTimer:stop()
                holdTimer = nil
                triggerLauncher()
            end

            local isDown = (type == hs.eventtap.event.types.keyDown)
            local app = getTargetApp()
            if modeActive and app and app:isFrontmost() then
                flags.cmd = nil
                local e = hs.eventtap.event.newKeyEvent(flags, keycode, isDown)
                e:post(app)
            else
                table.insert(keyBuffer, { keycode = keycode, flags = flags, isDown = isDown })
            end
        end
        return true
    end

    return false
end)

activeWatchers.rightCmdRaycastTap:start()
```

Please update `/Users/matt/.hammerspoon/modules/right_command_raycast.lua`.

---

## Assistant

FINISHED

---
