---
title: "Fix Hammerspoon Eventtap Bug"
date: "2026-08-14"
conversation_id: "98364cec-c14d-4368-a437-b29bc886423a"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please fix `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua`:

Line 175 has a bug: `event:getFlags():contain(...)` failed because `event:getFlags()` is a table without a `contain` method.

Fix the eventtap callback (around lines 170-220):
```lua

_G.activeWatchers.geminiSearchTap = hs.eventtap.new({hs.eventtap.event.types.keyDown}, function(event)
    if isDeleting then return false end

    local app = hs.application.frontmostApplication()
    if not app then return false end
    local appName = app:name() or ""
    local bundleID = app:bundleID() or ""
    
    local isTargetApp = (
        appName:find("Antigravity") or 
        appName:find("Hermes") or 
        bundleID:find("antigravity") or 
        bundleID:find("hermes")
    )
    if not isTargetApp then return false end

    local keyCode = event:getKeyCode()
    if keyCode == 51 then -- Backspace / Delete
        if #typedBuffer > 0 then
            typedBuffer = typedBuffer:sub(1, -2)
        end
        return false
    end

    local chars = event:getCharacters()
    if not chars or #chars == 0 then return false end

    typedBuffer = typedBuffer .. chars
    if #typedBuffer > 20 then
        typedBuffer = typedBuffer:sub(-20)
    end

    if bufferResetTimer then bufferResetTimer:stop() end
    bufferResetTimer = hs.timer.doAfter(2.0, function()
        typedBuffer = ""
    end)

    if typedBuffer:sub(-7) == "@gemini" then
        typedBuffer = ""
        isDeleting = true
        
        -- Delete 7 characters
        hs.timer.doAfter(0.01, function()
            for i = 1, 7 do
                hs.eventtap.keyStroke({}, "delete", 0)
            end
            isDeleting = false
            hs.timer.doAfter(0.05, function()
                showChooser()
            end)
        end)
        return false
    end

    return false
end)
```

Replace the faulty `event:getFlags():contain` logic in `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua`.

</span>



<span title="Responded at 1:24am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The issue in `/Users/matt/.hammerspoon/modules/gemini_thread_search.lua` has been resolved. The `event:getFlags()` method returns a table of flags, so I updated the code to access the `maskNonCoalesced` property directly from that table instead of using an invalid `:contain()` method.
The change has been applied:
```diff
-    if event:getFlags():contain("maskNonCoalesced") or event:getProperty(hs.eventtap.event.properties.eventSourceStateID) ~= 0 then
+    local flags = event:getFlags()
+    if flags.maskNonCoalesced or event:getProperty(hs.eventtap.event.properties.eventSourceStateID) ~= 0 then
```
I have notified the parent agent.

</span>



</span>

</span>