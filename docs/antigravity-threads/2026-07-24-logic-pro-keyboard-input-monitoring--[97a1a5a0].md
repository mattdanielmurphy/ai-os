---
title: "Logic Pro Keyboard Input Monitoring"
date: "2026-07-24"
conversation_id: "97a1a5a090f09b4b"
source: "antigravity"
---

# Logic Pro Keyboard Input Monitoring

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Note-Taking Directive: When asked to "make a note about this", format a complete markdown note with frontmatter, high-level summary, detailed bulleted breakdown, expanded key details, and thread link. Output a single copy-pasteable bash command or file write appending to the Personal vault.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




can a Logic script monitor keyboard inputs?

---

## Assistant

**Yes for MIDI keyboards, but no for your computer’s QWERTY keyboard** (at least not directly within Logic Pro’s built-in Scripter).

How it breaks down depending on what type of input you are trying to capture:

1. MIDI Keyboards (Native Support)

If you are using Logic Pro’s built-in JavaScript **Scripter** plugin (found under MIDI FX on a track), it natively monitors and processes all incoming MIDI keyboard events in real time.

You hook into these inputs using the `HandleMIDI()` callback:

JavaScript

```
function HandleMIDI(event) {
    // Check if the input is from a keyboard note press
    if (event instanceof NoteOn) {
        Trace("Key pressed: " + event.pitch + " with velocity: " + event.velocity);
    }
    
    // Pass the MIDI event through (or modify/block it)
    event.send();
}

```


This gives you full access to note numbers, velocity, pitch bend, sustain pedal, and CC messages coming from any connected MIDI controller.

2. Computer (QWERTY) Keyboards (Restricted)

Logic Pro’s Scripter runs inside Logic's isolated audio/MIDI engine. For security and architectural reasons, it **cannot** listen for system-wide computer keystrokes directly.

If you need your QWERTY keyboard to trigger or monitor logic scripts, here are the standard workarounds:

**Musical Typing (`Shift + K`):** Enables Logic’s built-in virtual keyboard. Pressing QWERTY keys converts them into standard MIDI notes, which then pass directly into Scripter as regular `NoteOn` / `NoteOff` events.

**External Translation (Bome MIDI Translator / Keyboard Maestro):** You can run a background script or utility that listens for global QWERTY keystrokes and outputs them to a virtual MIDI port (IAC Driver on macOS), which Logic then reads natively.

**macOS Key Commands:** You can bind custom AppleScripts or System Events shortcuts to trigger Logic menu commands, though this operates at the OS level rather than inside a Logic MIDI script.

Are you looking to manipulate incoming MIDI notes or trigger events with your QWERTY keyboard?
Yes

---

## User

I meant my computer keyboard.

But if they can handle midi, I can just use some software to temporarily capture some keys on my keyboard and convert them to midi; then I have a custom midi controller which is my keyboard.

Surely some third party app for this already exists.

List the options. Free and Paid, the best available.

---

## Assistant

Several dedicated apps intercept QWERTY keystrokes system-wide and map them to virtual MIDI outputs (like macOS’s **IAC Driver** or a virtual port created by the app itself), which Logic’s Scripter can read directly.

Free & Open Source
1. Bome Keyboard (Free)

**What it is:** A lightweight virtual MIDI keyboard tool from Bome (the creators of Bome MIDI Translator).

**How it works:** Sits as a floating window or background tool. Keystrokes map to MIDI note values, CC messages, or pitch bends.

**Why it's good:** It generates a dedicated virtual MIDI port out of the box, requiring zero setup in macOS MIDI Studio. Lightweight with near-zero latency.

2. MidiKeys (Free / Open Source)

**What it is:** A classic, bare-bones utility hosted on GitHub designed purely for macOS.  
notes from flit

**How it works:** Translates physical alphanumeric keyboard presses into MIDI notes and routes them to a selected output port.

**Why it's good:** Enables **Global Hotkeys** mode, meaning it can capture QWERTY strokes even when the app itself is running in the background while you are focused inside Logic.  
GitHub Pages documentation

Paid & Advanced Solutions
3. Bome MIDI Translator Pro (~$65 USD / Free Trial)

**What it is:** The gold standard for custom MIDI mapping logic on macOS.

**How it works:** Intercepts system keystrokes, key combinations, or hold states, and runs full logic rules (variables, conditionals, timers) before outputting raw MIDI bytes to Logic.

**Why it's good:** Ideal for complex setups—such as using key modifiers (`Cmd`, `Option`, `Shift`) to change Octaves or mapping specific QWERTY keys to send MIDI CC continuous values instead of just `NoteOn`/`NoteOff`.

4. Easy MIDI ($29.99 USD)

**What it is:** A polished Mac App Store utility that turns your keyboard, mouse, and trackpad into a full MIDI control surface.  
Apple

**How it works:** Maps alphanumeric keys across multiple octaves, numeric keys to chords, and uses trackpad gestures (pinch, scroll) for pitch bend, velocity, and modulation.  
Apple

**Why it's good:** Great for turning a QWERTY layout into a flexible expressive performance controller without scripting.

macOS Quick-Setup Steps

**Enable the IAC Driver (if the app requires it):** Open **Audio MIDI Setup** on macOS -> `Cmd + 2` (MIDI Studio) -> Double-click **IAC Driver** -> Check **"Device is online"**.

**Launch your choice of translator** (e.g., MidiKeys) and set its **MIDI Output** to *IAC Driver Bus 1*.

**In Logic Pro:** Open your Scripter track. It will automatically detect incoming events from the IAC Driver, allowing your `HandleMIDI(event)` logic to parse those converted QWERTY presses.

---

## User

So specifically what I thought would be great to have is:

I'm already using a transposer so I only care about the white keys. Therefore the entire row above the home row is free, so that could +2 octaves above the home row.

And it'd be great to be able to use the bottom row as well for more controls.

And I'd love to be able to switch between regular keyboard input mode and this special midi controller mode obviously

---

## Assistant

To achieve this specific layout—home row for notes, upper row for +2 octaves, bottom row for controls, and a global mode toggle—you need an app that supports **modal state switching** and **key swallowing** (so keys don't type text or trigger Logic's native shortcuts when in MIDI mode).

Here are the two best ways to build this exact workflow on macOS.

Option 1: Hammerspoon (Best Free / Fully Customizable)

Hammerspoon is a lightweight macOS automation engine. It can create its own virtual MIDI port directly in code (no IAC setup required), swallow keypresses, and toggle in/out of "MIDI Mode" with a hotkey.

How it handles your spec:

**Mode Switch:** A hotkey (e.g., `Cmd + Option + M` or `Caps Lock`) enables/disables the event tap and displays an on-screen overlay (`MIDI Mode: ON`).

**Key Swallowing:** When active, intercepted QWERTY keys are blocked from reaching Logic or the OS, preventing accidental menu commands or text entry.

**Layout Mapping:**

**Home Row (`A S D F G H J K L ;`):** Base octave notes (e.g., MIDI notes 60 to 71).

**Upper Row (`Q W E R T Y U I O P`):** Identical pitch intervals offset by +24 semitones (+2 octaves).

**Bottom Row (`Z X C V B N M`):** Mapped to MIDI Control Change (CC) messages (e.g., Sustain Pedal on `Z`, Mod Wheel on `X`, Pitch Bend on `C/V`).

Sample `init.lua` Config Strategy
Lua

```
local virtualMidi = hs.midi.newVirtual("QWERTY MIDI Controller")
local midiActive = false
local alertId = nil

-- Define key mappings (Keycodes -> MIDI Note / CC)
local homeRowNotes  = { [0]=60, [1]=62, [2]=64, [3]=65, [5]=67, [4]=69, [38]=71 } -- A S D F G H J...
local upperRowNotes = { [12]=84, [13]=86, [14]=88, [15]=89, [17]=91, [16]=93, [32]=95 } -- Q W E R T Y U... (+2 Octaves)

-- Intercept keystrokes system-wide
local keyTap = hs.eventtap.new({hs.eventtap.event.types.keyDown, hs.eventtap.event.types.keyUp}, function(event)
    if not midiActive then return false end
    
    local code = event:getProperty(hs.eventtap.event.properties.keyboardEventKeycode)
    local isDown = (event:getType() == hs.eventtap.event.types.keyDown)
    
    if homeRowNotes[code] then
        virtualMidi:sendEvent({status = isDown and 0x90 or 0x80, note = homeRowNotes[code], velocity = 100})
        return true -- Swallow keypress
    elseif upperRowNotes[code] then
        virtualMidi:sendEvent({status = isDown and 0x90 or 0x80, note = upperRowNotes[code], velocity = 100})
        return true -- Swallow keypress
    end
    
    return false -- Pass other keys through
end)

-- Toggle MIDI Mode with Cmd+Opt+M
hs.hotkey.bind({"cmd", "alt"}, "M", function()
    midiActive = not midiActive
    if midiActive then keyTap:start() else keyTap:stop() end
    hs.alert.show("MIDI Controller Mode: " .. (midiActive and "ON" or "OFF"))
end)

```

Option 2: Bome MIDI Translator Pro (Best Paid / No-Code)

If you prefer a visual rule builder instead of writing Lua, **Bome MIDI Translator Pro** (~$65 USD) handles state-based MIDI translation out of the box.

How it handles your spec:

**Global Preset Toggling:** You create two Presets: `Normal QWERTY` and `MIDI Controller`. Assign a hotkey (e.g., `Option + Space`) to switch between them.

**Variable-Based Routing:** In the `MIDI Controller` preset, set rules where incoming QWERTY keys output raw MIDI bytes to Bome's virtual MIDI port.

**Dual Octave & Bottom Row Logic:**

**Home Row Translator:** Maps `Key 'A'` -> `NoteOn C3 (60)`.

**Upper Row Translator:** Maps `Key 'Q'` -> `NoteOn C5 (84)` (+24 MIDI pitch value).

**Bottom Row Translator:** Maps `Key 'Z'` -> `CC #64` (Sustain, value 127 on press, 0 on release), `Key 'X'` -> `CC #1` (Modulation), or `Key 'C'`/`Key 'V'` -> Octave Down/Up multipliers.

**Suppress Key Pass-Through:** Check the "Suppress original keypress" box in Bome so system inputs don't spill into Logic while playing.

Suggested Mapping Structure
Keyboard Row	Target Function	Example MIDI Output
**Upper Row (`Q W E R T Y...`)**	High Octave Pitch Row	C5, D5, E5, F5, G5... (+2 octaves above home)
**Home Row (`A S D F G H...`)**	Base Octave Pitch Row	C3, D3, E3, F3, G3... (Fed into Logic Transposer)
**Bottom Row (`Z X C V B...`)**	Performance Controls	`Z` = Sustain (CC 64), `X` = Mod (CC 1), `C`/`V` = Pitch Bend Down/Up
**Spacebar / CapsLock**	Global Mode Toggle	Enables/Disables QWERTY capture overlay
Next Step in Logic

Once either app sends events to its virtual MIDI output, point **Logic Pro's Scripter** to read from that virtual port. Inside Scripter, `HandleMIDI()` will receive the notes and CC commands identically to a physical hardware MIDI controller.

---
