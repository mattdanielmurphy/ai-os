---
title: "Optimize Antigravity Hotkey Script"
date: "2026-08-05"
conversation_id: "81fb7ce9-f02c-4874-85be-adc182ea7993"
source: "antigravity"
---

# Optimize Antigravity Hotkey Script

## User

Please update `/Users/matt/.hammerspoon/modules/keybindings.lua` to optimize the Antigravity send-button hotkey. The current file content is:

```lua
-- ~/.hammerspoon/modules/keybindings.lua
-- Contains custom keybindings, specifically context-aware hotkeys.
--
-- ── Global Anchoring Convention ─────────────────────────────────────────────────
-- All persistent watchers, filters, and hotkeys in this file are anchored to the
-- global `activeWatchers` table (defined in init.lua) so Lua's garbage collector
-- never silently reclaims them. Local variables are NOT safe for these resources.
-- Do NOT add timer-based health checks — the root cause is always a missing global
-- reference, not a runtime glitch.
-- ────────────────────────────────────────────────────────────────────────────────

-- Map cmd-e to cmd-opt-g specifically in Google Chrome
activeWatchers.chromeHotkey = hs.hotkey.new({"cmd"}, "e", function()
  -- Trigger cmd-alt-g
  hs.eventtap.keyStroke({"cmd", "alt"}, "g")
end)

local chromeBundleID = "com.google.Chrome"

local function enableChromeHotkey()
  activeWatchers.chromeHotkey:enable()
end

local function disableChromeHotkey()
  activeWatchers.chromeHotkey:disable()
end

-- Context-aware hotkey for Google Chrome (cmd-e -> cmd-alt-g)
activeWatchers.chromeWatcher = hs.application.watcher.new(function(appName, eventType, app)
  if app and app:bundleID() == chromeBundleID then
    if eventType == hs.application.watcher.activated then
      enableChromeHotkey()
    elseif eventType == hs.application.watcher.deactivated then
      disableChromeHotkey()
    end
  end
end)
activeWatchers.chromeWatcher:start()

-- Check if Google Chrome is already the active/frontmost application when Hammerspoon starts/reloads
local frontApp = hs.app
<truncated 3836 bytes>
true) ~= nil
    end,
    { count = 1 }  -- stop after first match
  )
  return results and results[1] or nil
end

activeWatchers.antigravityHotkey = hs.hotkey.new({"cmd"}, "return", function()
  -- Fast path: try cached button first
  if _antigravitySendBtnCache then
    local ok = pcall(function()
      _antigravitySendBtnCache:performAction("AXPress")
    end)
    if ok then return end
    -- Cache is stale; clear it and fall through to re-search
    _antigravitySendBtnCache = nil
  end

  -- Slow path (runs once per window session): traverse AX tree
  local app = hs.application.find("Antigravity")
  if not app then return end

  local win = app:mainWindow()
  if not win then return end

  local axWin = hs.axuielement.windowElement(win)
  if not axWin then return end

  local btn = _findSendBtn(axWin)
  if btn then
    _antigravitySendBtnCache = btn
    btn:performAction("AXPress")
  else
    hs.alert.show("Send button not found")
  end
end)

local function enableAntigravityHotkey()
  activeWatchers.antigravityHotkey:enable()
end

local function disableAntigravityHotkey()
  -- Invalidate cache so a fresh window gets a fresh search
  _antigravitySendBtnCache = nil
  activeWatchers.antigravityHotkey:disable()
end

activeWatchers.antigravityWatcher = hs.application.watcher.new(function(appName, eventType, app)
  if appName == "Antigravity" then
    if eventType == hs.application.watcher.activated then
      enableAntigravityHotkey()
    elseif eventType == hs.application.watcher.deactivated then
      disableAntigravityHotkey()
    end
  end
end)
activeWatchers.antigravityWatcher:start()

-- Initial state check on Hammerspoon reload
local _agFrontApp = hs.application.frontmostApplication()
if _agFrontApp and _agFrontApp:name() == "Antigravity" then
  enableAntigravityHotkey()
end
```

Use `replace_file_content` to replace from line 46 to line 109 in `/Users/matt/.hammerspoon/modules/keybindings.lua`.

---

## Assistant

Created At: 2026-08-05T04:20:16-06:00
Completed At: 2026-08-05T04:20:16-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.hammerspoon/modules/keybindings.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -43,8 +43,38 @@
   enableChromeHotkey()
 end
 
--- Antigravity Send Button Hotkey (cmd-return)
+-- ── Antigravity Send Button Hotkey (cmd-return) ──────────────────────────────
+-- Fast path: cache the AXButton reference so we only traverse the AX tree once.
+-- On subsequent presses we hit the cached element directly (~immediate).
+-- Cache is cleared when Antigravity deactivates so stale refs are not reused.
+
+local _antigravitySendBtnCache = nil
+
+local function _findSendBtn(axWin)
+  -- Use built-in elementSearch for a fast BFS instead of manual recursion
+  local results = axWin:elementSearch(
+    function(el)
+      return el.AXRole == "AXButton" and
+             el.AXDescription ~= nil and
+             el.AXDescription:find("Send message", 1, true) ~= nil
+    end,
+    { count = 1 }  -- stop after first match
+  )
+  return results and results[1] or nil
+end
+
 activeWatchers.antigravityHotkey = hs.hotkey.new({"cmd"}, "return", function()
+  -- Fast path: try cached button first
+  if _antigravitySendBtnCache then
+    local ok = pcall(function()
+      _antigravitySendBtnCache:performAction("AXPress")
+    end)
+    if ok then return end
+    -- Cache is stale; clear it and fall through to re-search
+    _antigravitySendBtnCache = nil
+  end
+
+  -- Slow path (runs once per window session): traverse AX tree
   local app = hs.application.find("Antigravity")
   if not app then return end
 
@@ -53,33 +53,12 @@
   local axWin = hs.axuielement.windowElement(win)
   if not axWin then return end
 
-  -- Recursive function to find the button by its Accessibility Description
-  local function findSendButton(element)
-      if not element then return nil end
-      
-      local role = element.AXRole
-      local desc = element.AXDescription
-      
-      -- Check if it's a button and matches the tooltip text
-      if role == "AXButton" and desc and string.match(desc, "Send message") then
-          return element
-      end
-      
-      local children = element.AXChildren
-      if children then
-          for i, child in ipairs(children) do
-              local found = findSendButton(child)
-              if found then return found end
-          end
-      end
-      return nil
-  end
-
-  local sendBtn = findSendButton(axWin)
-  if sendBtn then
-      sendBtn:performAction("AXPress")
+  local btn = _findSendBtn(axWin)
+  if btn then
+    _antigravitySendBtnCache = btn
+    btn:performAction("AXPress")
   else
-      hs.alert.show("Send button not found")
+    hs.alert.show("Send button not found")
   end
 end)
 
@@ -87,6 +87,8 @@
 end
 
 local function disableAntigravityHotkey()
+  -- Invalidate cache so a fresh window gets a fresh search
+  _antigravitySendBtnCache = nil
   activeWatchers.antigravityHotkey:disable()
 end
 
@@ -100,7 +100,8 @@
 end)
 activeWatchers.antigravityWatcher:start()
 
-local frontApp = hs.application.frontmostApplication()
-if frontApp and frontApp:name() == "Antigravity" then
+-- Initial state check on Hammerspoon reload
+local _agFrontApp = hs.application.frontmostApplication()
+if _agFrontApp and _agFrontApp:name() == "Antigravity" then
   enableAntigravityHotkey()
 end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T04:20:17-06:00
Completed At: 2026-08-05T04:20:17-06:00
Message sent to "87630d27-d058-4309-9839-1c461c82a15a".

The Antigravity send-button hotkey in `/Users/matt/.hammerspoon/modules/keybindings.lua` has been updated to include reference caching. 

### Key Changes
*   **Performance Optimization**: Added `_antigravitySendBtnCache` to store the reference to the "Send message" button.
*   **Fast Path**: The hotkey now attempts to trigger `performAction("AXPress")` on the cached button immediately using `pcall` to detect stale references.
*   **Resilient Fallback**: If the cache is empty or stale, it performs a efficient BFS-based search using `hs.axuielement:elementSearch` and updates the cache.
*   **Cache Invalidation**: The cache is cleared in `disableAntigravityHotkey` to ensure a clean search when the application window is reactivated or re-initialized.

The update is now live in your configuration.

---
