---
title: "Automate CloudMounter Popup Dismissal"
date: "2026-08-06"
conversation_id: "71fcd7d3-1ab3-413d-8d9c-5ff0d6223d0d"
source: "antigravity"
---

# Automate CloudMounter Popup Dismissal

## User

Add a window watcher to /Users/matt/.hammerspoon/modules/keybindings.lua to auto-dismiss CloudMounter's "Upgrade to PRO version required!" nag dialog using Hammerspoon.

Add the following logic anchored to `_G.activeWatchers.cloudMounterFilter`:

```lua
-- ── Auto-dismiss CloudMounter Upgrade Popup ────────────────────────────────────
activeWatchers.cloudMounterFilter = hs.window.filter.new(function(win)
  local app = win:application()
  if app and app:bundleID() and app:bundleID():find("com.eltima.cloudmounter") then
    return true
  end
  return false
end)

activeWatchers.cloudMounterFilter:subscribe(hs.window.filter.windowCreated, function(win)
  if win:title() == "Upgrade to PRO version required!" then
    -- Immediately send ESC to close the window
    win:focus()
    hs.eventtap.keyStroke({}, "escape", 0, win:application())
    hs.alert.show("⚡️ CloudMounter PRO nag auto-dismissed")
  end
end)
```

Append this code at the bottom of /Users/matt/.hammerspoon/modules/keybindings.lua. Use replace_file_content or multi_replace_file_content. Do not try to call subagents.

---

## Assistant

Created At: 2026-08-05T19:40:43-06:00
Completed At: 2026-08-05T19:40:43-06:00
File Path: `file:///Users/matt/.hammerspoon/modules/keybindings.lua`
Total Lines: 121
Total Bytes: 4532
Showing lines 1 to 121
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
<truncated 1463 bytes>
[1] or nil
64: end
65: 
66: activeWatchers.antigravityHotkey = hs.hotkey.new({"cmd"}, "return", function()
67:   -- Fast path: try cached button first
68:   if _antigravitySendBtnCache then
69:     local ok = pcall(function()
70:       _antigravitySendBtnCache:performAction("AXPress")
71:     end)
72:     if ok then return end
73:     -- Cache is stale; clear it and fall through to re-search
74:     _antigravitySendBtnCache = nil
75:   end
76: 
77:   -- Slow path (runs once per window session): traverse AX tree
78:   local app = hs.application.find("Antigravity")
79:   if not app then return end
80: 
81:   local win = app:mainWindow()
82:   if not win then return end
83: 
84:   local axWin = hs.axuielement.windowElement(win)
85:   if not axWin then return end
86: 
87:   local btn = _findSendBtn(axWin)
88:   if btn then
89:     _antigravitySendBtnCache = btn
90:     btn:performAction("AXPress")
91:   else
92:     hs.alert.show("Send button not found")
93:   end
94: end)
95: 
96: local function enableAntigravityHotkey()
97:   activeWatchers.antigravityHotkey:enable()
98: end
99: 
100: local function disableAntigravityHotkey()
101:   -- Invalidate cache so a fresh window gets a fresh search
102:   _antigravitySendBtnCache = nil
103:   activeWatchers.antigravityHotkey:disable()
104: end
105: 
106: activeWatchers.antigravityWatcher = hs.application.watcher.new(function(appName, eventType, app)
107:   if appName == "Antigravity" then
108:     if eventType == hs.application.watcher.activated then
109:       enableAntigravityHotkey()
110:     elseif eventType == hs.application.watcher.deactivated then
111:       disableAntigravityHotkey()
112:     end
113:   end
114: end)
115: activeWatchers.antigravityWatcher:start()
116: 
117: -- Initial state check on Hammerspoon reload
118: local _agFrontApp = hs.application.frontmostApplication()
119: if _agFrontApp and _agFrontApp:name() == "Antigravity" then
120:   enableAntigravityHotkey()
121: end
The above content shows the entire, complete file contents of the requested file.

---
