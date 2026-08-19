---
title: "Configure Antigravity Hammerspoon Hotkey"
date: "2026-08-05"
conversation_id: "b3cddf67-9d3a-4746-989c-e763bc71c9d0"
source: "antigravity"
---

# Configure Antigravity Hammerspoon Hotkey

## User

Please update `/Users/matt/.hammerspoon/modules/keybindings.lua` to add the Antigravity context-aware hotkey requested by the user.

Requirements:
1. Make sure all hotkeys and watchers are anchored to `_G.activeWatchers` (or `activeWatchers`) to prevent garbage collection.
2. Bind `{"cmd"}, "return"` ONLY when an `Antigravity` application window is focused/active.
3. The hotkey action should execute the following block:
```lua
local app = hs.application.find("Antigravity")
if not app then return end

local win = app:mainWindow()
if not win then return end

local axWin = hs.axuielement.windowElement(win)
if not axWin then return end

-- Recursive function to find the button by its Accessibility Description
local function findSendButton(element)
    if not element then return nil end
    
    local role = element.AXRole
    local desc = element.AXDescription
    
    -- Check if it's a button and matches the tooltip text
    if role == "AXButton" and desc and string.match(desc, "Send message") then
        return element
    end
    
    local children = element.AXChildren
    if children then
        for i, child in ipairs(children) do
            local found = findSendButton(child)
            if found then return found end
        end
    end
    return nil
end

local sendBtn = findSendButton(axWin)
if sendBtn then
    sendBtn:performAction("AXPress")
else
    hs.alert.show("Send button not found")
end
```
4. Support finding the app either by bundle ID or title matching "Antigravity", and toggle enabling/disabling the hotkey via an `hs.application.watcher` (and check initial state via `hs.application.frontmostApplication()`), matching the pattern already present in `/Users/matt/.hammerspoon/modules/keybindings.lua`.

Here is the current content of `/Users/matt/.hammerspoon/modules/keybindings.lua`:
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
local frontApp = hs.application.frontmostApplication()
if frontApp and frontApp:bundleID() == chromeBundleID then
  enableChromeHotkey()
end
```

Use `replace_file_content` to edit `/Users/matt/.hammerspoon/modules/keybindings.lua`.

---

## Assistant

Created At: 2026-08-05T00:59:09-06:00
Completed At: 2026-08-05T00:59:09-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.hammerspoon/modules/keybindings.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -41,4 +41,69 @@
 local frontApp = hs.application.frontmostApplication()
 if frontApp and frontApp:bundleID() == chromeBundleID then
   enableChromeHotkey()
-end
+end
+
+-- Antigravity Send Button Hotkey (cmd-return)
+activeWatchers.antigravityHotkey = hs.hotkey.new({"cmd"}, "return", function()
+  local app = hs.application.find("Antigravity")
+  if not app then return end
+
+  local win = app:mainWindow()
+  if not win then return end
+
+  local axWin = hs.axuielement.windowElement(win)
+  if not axWin then return end
+
+  -- Recursive function to find the button by its Accessibility Description
+  local function findSendButton(element)
+      if not element then return nil end
+      
+      local role = element.AXRole
+      local desc = element.AXDescription
+      
+      -- Check if it's a button and matches the tooltip text
+      if role == "AXButton" and desc and string.match(desc, "Send message") then
+          return element
+      end
+      
+      local children = element.AXChildren
+      if children then
+          for i, child in ipairs(children) do
+              local found = findSendButton(child)
+              if found then return found end
+          end
+      end
+      return nil
+  end
+
+  local sendBtn = findSendButton(axWin)
+  if sendBtn then
+      sendBtn:performAction("AXPress")
+  else
+      hs.alert.show("Send button not found")
+  end
+end)
+
+local function enableAntigravityHotkey()
+  activeWatchers.antigravityHotkey:enable()
+end
+
+local function disableAntigravityHotkey()
+  activeWatchers.antigravityHotkey:disable()
+end
+
+activeWatchers.antigravityWatcher = hs.application.watcher.new(function(appName, eventType, app)
+  if appName == "Antigravity" then
+    if eventType == hs.application.watcher.activated then
+      enableAntigravityHotkey()
+    elseif eventType == hs.application.watcher.deactivated then
+      disableAntigravityHotkey()
+    end
+  end
+end)
+activeWatchers.antigravityWatcher:start()
+
+local frontApp = hs.application.frontmostApplication()
+if frontApp and frontApp:name() == "Antigravity" then
+  enableAntigravityHotkey()
+end
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T00:59:10-06:00
Completed At: 2026-08-05T00:59:10-06:00
Message sent to "87630d27-d058-4309-9839-1c461c82a15a".

The update to `/Users/matt/.hammerspoon/modules/keybindings.lua` is complete. The Antigravity context-aware hotkey (`cmd + return`) has been added with the required accessibility-based button finding logic, anchoring, and lifecycle management.

---
