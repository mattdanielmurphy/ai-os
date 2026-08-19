---
title: "Update CloudMounter Hammerspoon Script"
date: "2026-08-06"
conversation_id: "53a140f2-370b-4cc6-96fb-d55d99d66119"
source: "antigravity"
---

# Update CloudMounter Hammerspoon Script

## User

Update the CloudMounter auto-dismiss filter in /Users/matt/.hammerspoon/modules/keybindings.lua.

Target file: /Users/matt/.hammerspoon/modules/keybindings.lua
StartLine: 123, EndLine: 138
TargetContent:
```
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
    win:focus()
    hs.eventtap.keyStroke({}, "escape", 0, win:application())
    hs.alert.show("⚡️ CloudMounter PRO nag auto-dismissed")
  end
end)
```
ReplacementContent:
```
-- ── Auto-dismiss CloudMounter Upgrade Popup ────────────────────────────────────
activeWatchers.cloudMounterFilter = hs.window.filter.new(function(win)
  local app = win:application()
  if app and app:bundleID() and app:bundleID():find("com.eltima.cloudmounter") then
    return true
  end
  return false
end)

activeWatchers.cloudMounterFilter:subscribe(hs.window.filter.windowCreated, function(win)
  -- CloudMounter modal dialog title can be "Upgrade to PRO version required!" or plain "Window" (AXDialog)
  local title = win:title()
  local subrole = win:subrole()
  if title == "Upgrade to PRO version required!" or (subrole == "AXDialog" and (title == "" or title == "Window")) then
    win:focus()
    hs.timer.doAfter(0.05, function()
      hs.eventtap.keyStroke({}, "escape", 0, win:application())
      hs.alert.show("⚡️ CloudMounter PRO nag auto-dismissed")
    end)
  end
end)
```
Do not call subagents.

---

## Assistant

Created At: 2026-08-05T20:43:13-06:00
Completed At: 2026-08-05T20:43:13-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.hammerspoon/modules/keybindings.lua. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -130,9 +130,14 @@
 end)
 
 activeWatchers.cloudMounterFilter:subscribe(hs.window.filter.windowCreated, function(win)
-  if win:title() == "Upgrade to PRO version required!" then
+  -- CloudMounter modal dialog title can be "Upgrade to PRO version required!" or plain "Window" (AXDialog)
+  local title = win:title()
+  local subrole = win:subrole()
+  if title == "Upgrade to PRO version required!" or (subrole == "AXDialog" and (title == "" or title == "Window")) then
     win:focus()
-    hs.eventtap.keyStroke({}, "escape", 0, win:application())
-    hs.alert.show("⚡️ CloudMounter PRO nag auto-dismissed")
+    hs.timer.doAfter(0.05, function()
+      hs.eventtap.keyStroke({}, "escape", 0, win:application())
+      hs.alert.show("⚡️ CloudMounter PRO nag auto-dismissed")
+    end)
   end
 end)
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

---
