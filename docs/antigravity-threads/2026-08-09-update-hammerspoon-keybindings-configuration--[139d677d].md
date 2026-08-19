---
title: "Update Hammerspoon Keybindings Configuration"
date: "2026-08-09"
conversation_id: "139d677d-8bc3-492d-a8b9-e568760a24ff"
source: "antigravity"
---

# Update Hammerspoon Keybindings Configuration

## User

Please update `/Users/matt/.hammerspoon/modules/keybindings.lua` to append a disabled-by-default Hammerspoon implementation of the Caps Lock -> Cmd-Tilde / Cmd-Shift-Tilde key remap using `hs.eventtap`.

Add this code snippet at the end of `/Users/matt/.hammerspoon/modules/keybindings.lua`:

```lua
-- ── Caps Lock -> Cmd-Tilde / Cmd-Shift-Tilde (Disabled by default) ─────────
-- Remaps Caps Lock to ~ (grave_accent_and_tilde) when Command is held down.
-- Cmd + Caps Lock -> Cmd + `
-- Cmd + Shift + Caps Lock -> Cmd + Shift + ` (Cmd + ~)
-- To enable: change `enabled = false` to `enabled = true` below or call activeWatchers.capsCmdTildeTap:start()

local capsCmdTildeEnabled = false

if capsCmdTildeEnabled then
  activeWatchers.capsCmdTildeTap = hs.eventtap.new({ hs.eventtap.event.types.keyDown }, function(event)
    local keyCode = event:getKeyCode()
    -- 57 is Caps Lock keycode on macOS
    if keyCode == 57 then
      local flags = event:getFlags()
      if flags.cmd then
        local mods = { "cmd" }
        if flags.shift then
          table.insert(mods, "shift")
        end
        if flags.alt then
          table.insert(mods, "alt")
        end
        if flags.ctrl then
          table.insert(mods, "ctrl")
        end
        -- Post Cmd+(Shift)+` keystroke
        hs.eventtap.keyStroke(mods, "`", 0)
        return true -- suppress original Caps Lock event
      end
    end
    return false
  end)
  activeWatchers.capsCmdTildeTap:start()
end
```

Use `replace_file_content` to make this edit cleanly.

---

## Assistant

Created At: 2026-08-09T14:58:07-06:00
Completed At: 2026-08-09T14:58:07-06:00
File Path: `file:///Users/matt/.hammerspoon/modules/keybindings.lua`
Total Lines: 164
Total Bytes: 6164
Showing lines 1 to 164
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: -- ~/.hammerspoon/modules/keybindings.lua
2: -- Contains custom keybindings, specifically context-aware hotkeys.
3: --
4: -- ── Global Anchoring Convention ─────────────────────────────────────────────────
5: -- All persistent watchers, filters, and hotkeys in this file are anchored to the
6: -- global `activeWatchers` table (defined in init.lua) so Lua's garbage collector
7: -- never silently reclaims them. Local variables are NOT safe for these resources.
8: -- Do NOT add timer-based health checks — the root cause is always a missing global
9: -- reference, not a runtime glitch.
10: -- ────────────────────────────────────────────────────────────────────────────────
11: 
12: -- Map cmd-e to cmd-opt-g specifically in Google Chrome
13: activeWatchers.chromeHotkey = hs.hotkey.new({"cmd"}, "e", function()
14:   -- Trigger cmd-alt-g
15:   hs.eventtap.keyStroke({"cmd", "alt"}, "g")
16: end)
17: 
18: local chromeBundleID = "com.google.Chrome"
19: 
20: local function enableChromeHotkey()
21:   activeWatchers.chromeHotkey:enable()
22: end
23: 
24: local function disableChromeHotkey()
25:   activeWatchers.chromeHotkey:disable()
26: end
27: 
28: -- Context-aware hotkey for Google Chrome (cmd-e -> cmd-alt-g)
29: activeWatchers.chromeWatcher = hs.application.watcher.new(function(appName, eventType, app)
30:   if app and app:
<truncated 3310 bytes>

122: local _agFrontApp = hs.application.frontmostApplication()
123: if _agFrontApp and _agFrontApp:name() == "Antigravity" then
124:   enableAntigravityHotkey()
125: end
126: 
127: -- ── Subtle Notification Helper ──────────────────────────────────────────────────
128: local function notifySubtle(message, duration)
129:   local style = {
130:     strokeColor = { white = 0, alpha = 0 },
131:     fillColor = { white = 0, alpha = 0.75 },
132:     textColor = { white = 1, alpha = 0.85 },
133:     radius = 4,
134:     textSize = 12,
135:     atScreenEdge = 2, -- Top-right corner
136:     padding = 8
137:   }
138:   hs.alert.show(message, style, duration or 1.5)
139: end
140: 
141: -- ── Auto-dismiss CloudMounter Upgrade Popup (Focus-Preserving) ─────────────────
142: activeWatchers.cloudMounterFilter = hs.window.filter.new(function(win)
143:   local app = win:application()
144:   if app and app:bundleID() and app:bundleID():find("com.eltima.cloudmounter") then
145:     return true
146:   end
147:   return false
148: end)
149: 
150: activeWatchers.cloudMounterFilter:subscribe(hs.window.filter.windowCreated, function(win)
151:   -- CloudMounter modal dialog title can be "Upgrade to PRO version required!" or plain "Window" (AXDialog)
152:   local title = win:title()
153:   local subrole = win:subrole()
154:   if title == "Upgrade to PRO version required!" or (subrole == "AXDialog" and (title == "" or title == "Window")) then
155:     -- DO NOT call win:focus()! That steals focus from the user's active window/typing.
156:     hs.timer.doAfter(0.05, function()
157:       local app = win:application()
158:       if app then
159:         hs.eventtap.keyStroke({}, "escape", 0, app)
160:       end
161:       notifySubtle("⚡️ CloudMounter PRO nag auto-dismissed", 1.5)
162:     end)
163:   end
164: end)
The above content shows the entire, complete file contents of the requested file.

---
