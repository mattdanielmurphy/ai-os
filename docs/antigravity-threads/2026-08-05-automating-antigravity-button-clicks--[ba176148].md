---
title: "Automating Antigravity Button Clicks"
date: "2026-08-05"
conversation_id: "ba176148b8761290"
source: "antigravity"
---

# Automating Antigravity Button Clicks

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-05 00:55 MDT-6] [context to this point is 0]




[Attached Context: Mac Apps & Automation Context]

```text

[Mac Environment & Installed Applications Context]

Primary Directory: /Users/matt

Installed Development & Utility Apps:

- Raycast (Launcher & Extension Runner)

- Hammerspoon (Lua Desktop & Window Automation)

- Obsidian (Personal Vault & Project Notes)

- Xcode & Command Line Tools (macOS Development)

- Docker Desktop & Container Tools

- iTerm2 & Terminal (Zsh shell)

- VS Code & Antigravity / Cursor

- CleanShot X (Screen capture & recording)

- Karabiner-Elements (Keyboard remapping)

- Homebrew (/opt/homebrew)

- Bun, Node.js, Python 3.12, Rust / Cargo

```







[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

I want to make an automation for clicking this "Send message" button in Antigravity.

Sadly it's electron... so there's no menu item for it, there's no keyboard shortcut for it... (that's why I'm doing this!)

I mean; technically there IS a keyboard shortcut (return) but you can't be focused on an artifact and use it; so I have to use the mouse again and again like a caveman.

Anyway, question is: can I use hammerspoon for this?

In keyboard maestro, I know I'd just use Click on found image.

But I only use that when I HAVE to because it's finicky.

What can Hammerspoon do? I've heard it can do a heck of a lot

---

## Assistant

Hammerspoon can handle this, and you have a few different avenues to approach it. Even though Antigravity is an Electron app and lacks standard macOS UI hooks, Chromium still broadcasts its DOM to the macOS Accessibility API.

Here is how you can tackle this in Hammerspoon, starting with the most robust method and ending with the image-search fallback you are used to in Keyboard Maestro.

Method 1: The Accessibility API (Recommended)

This is the cleanest approach. You don't need to move the mouse or rely on pixel-perfect image matching. Hammerspoon’s `hs.axuielement` can search the application's underlying accessibility tree for the button and trigger its `AXPress` action directly.

Based on `image_431c62.png`, the button has a tooltip that says "Send message ⏎". In Electron apps, this usually means the HTML element has an `aria-label` or `title` that macOS reads as an `AXDescription`.

You can bind a hotkey to run a recursive search for that specific button and press it:

Lua

```
-- Bind to your preferred shortcut (e.g., Cmd+Option+Return)
hs.hotkey.bind({"cmd", "alt"}, "return", function()
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
end)

```

Method 2: UI Focus + Keystroke Chaining

If you are focused on an artifact and simply hitting `Return` doesn't work, there might be a keyboard shortcut in Antigravity to *focus* the chat input (for example, `Cmd+L` or `Cmd+J`).

If that exists, Hammerspoon can just chain the inputs instantly without relying on the UI tree:

Lua

```
hs.hotkey.bind({"cmd", "alt"}, "return", function()
    local app = hs.application.find("Antigravity")
    if app and app:isFrontmost() then
        -- 1. Send the shortcut to focus the chat box (replace "l" with actual shortcut)
        hs.eventtap.keyStroke({"cmd"}, "l")
        
        -- 2. Brief pause to let the Electron UI catch up
        hs.timer.usleep(50000) 
        
        -- 3. Send the Return key to submit
        hs.eventtap.keyStroke({}, "return")
    end
end)

```

Method 3: Hammerspoon's Image Search

If the accessibility tree is too slow to parse (Electron trees can be massive) or the button lacks an `AXDescription`, Hammerspoon can replicate Keyboard Maestro's "Click on found image" using `hs.screen:findImage()`.

You will need to take a small, precise screenshot of the purple arrow button (e.g., `send_btn.png`) and save it to your `~/.hammerspoon/` directory.

Lua

```
hs.hotkey.bind({"cmd", "alt"}, "return", function()
    -- Load the cropped image of the button
    local targetImage = hs.image.imageFromPath(os.getenv("HOME") .. "/.hammerspoon/send_btn.png")
    if not targetImage then 
        print("Image not found")
        return 
    end
    
    local screen = hs.mouse.getCurrentScreen()
    -- Search the current screen for the image
    local matchRect = screen:findImage(targetImage)
    
    if matchRect then
        local currentMousePos = hs.mouse.absolutePosition()
        local buttonCenter = matchRect.center
        
        -- Click the center of the found image
        hs.eventtap.leftClick(buttonCenter)
        
        -- Return the mouse to where you were working
        hs.mouse.absolutePosition(currentMousePos)
    else
        hs.alert.show("Could not find the send button on screen")
    end
end)

```


Have you run Apple's Accessibility Inspector (included with Xcode) on the Antigravity window yet to see exactly what `AXRole` and `AXDescription` that button broadcasts?

---
