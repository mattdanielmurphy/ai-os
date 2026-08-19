---
title: "Keyboard-Centric App Framework Concept"
date: "2026-08-01"
conversation_id: "082fad0c6e4155c0"
source: "antigravity"
---

# Keyboard-Centric App Framework Concept

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-01 10:09 MDT-6] [context to this point is 0]




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

I made this really nifty onscreen qwerty midi controller with dynamic UI...

And I realized; this is such a great way to make a piece of software: design it AROUND the keyboard as the focal point.

Everything you can do in the app, you can do via the keyboard by holding modifiers etc. You don't have to learn any keyboard shortcuts because they're just right in front of you.




Before I make this into a modular thing so I can make any app I want with this... surely this must exist already?

---

## Assistant

While elements of this concept exist across a few different domains, an **application framework built entirely around a dynamic 1:1 physical keyboard surface as its core runtime UI** is surprisingly rare as a general-purpose paradigm.

Here is how existing software touches on this idea, along with where your approach diverges:

Existing Prior Art
1. Keyboard Configuration & Layer Tools (QMK / VIA / VIAL / Chrysalis)

**What they do:** These utilities render a 1:1 interactive visual model of your physical keyboard. As you switch layers or hold modifiers (like `Fn` or `Space Cadet`), the keycap labels update live on screen to reflect the assigned keys or macros.

**How it differs:** They are configuration tools for hardware firmware rather than runtime application UIs. They map keycodes, but they don't host application logic, sliders, or dynamic audio/data engines inside the keys themselves.

2. Accessibility & OSK Overlays

**What they do:** Native macOS Accessibility Keyboards and software like *Key-Mon* or *Showkey* display a virtual QWERTY layout that updates keycap labels when `Shift`, `Option`, or `Cmd` are held.

**How it differs:** They are passive input visualizers or system-level typing tools, not self-contained feature rich applications.

3. DAWs & Tracker Software (Renoise, SunVox, Ableton, FL Studio)

**What they do:** Trackers (like Renoise) and DAWs lean heavily on QWERTY input for pitch and parameter manipulation. Tracker UIs in particular treat the keyboard as a primary instrument interface.

**How it differs:** Their visual interfaces remain standard desktop UIs (track views, mixers, plugin racks). The keyboard mapping is functional under the hood, but the UI itself isn't a rendered keyboard showing parameter feedback directly inside the key bounds.

4. Controller Menus & Radial Palettes (Steam Deck / Game Interfaces)

**What they do:** Games use hold-to-reveal action wheels where holding a button displays a visual menu overlay mapped directly to your physical controls, eliminating the need to memorize arbitrary bindings.

**How it differs:** Mapped to gamepads/radials rather than full QWERTY layouts with state-driven parameter displays.

Why Abstracting This is Compelling

Most desktop application frameworks treat the keyboard as a secondary accelerator for a mouse-first GUI (tooltips, menu shortcuts, `Cmd + Key`).

Your design flips this: **the physical keyboard layout is the primary GUI canvas**, where:

Keycaps act as live display cells (showing values, parameters, and states).

Modifier keys act as real-time UI view switches rather than hidden shortcuts.

The visual feedback loop completely eliminates the gap between "learning the UI" and "learning the muscle memory."

If you modularize this into a framework (e.g., a React/Svelte component library or a Rust/Tauri canvas engine), you could define app state as a declarative map of key layouts (`BaseLayer`, `ShiftLayer`, `OptionLayer`) where each key binds both an execution handler and a reactive UI renderer.

What stack or framework are you planning to use to modularize this?

---

## User

[2026-08-01 10:16 MDT-6] [context to this point is 982]




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

I mean, I feel like there's a lot of potential for this.

Even just for making music...

I love hardware synths, but I'm too cheap to buy one.

I think this app is just starting to give me a taste of that, and I think a key is the fact that things are constrained (I often just spawn this not even with Logic in the foreground), and right under your fingers.

It's like a self-contained piece of hardware, except obviously it's utilizing your qwerty keyboard.

Now, it IS a real shame about the fact that most keyboard manufacturers cheap out with the wiring so you can't hold any combo you want...

That's something I need to work out formally and design around. But I realized I need to learn more heavily into chord buttons instead of manually holding down chords with my fingers. That way I can only hold say 3 keys at once instead of 5 or 6. The more keys at once, the greater the risk of the keyboard wiring fucking us.

But yeah... what else was I thinking would be nice to use this for?

Well, frankly I feel like most apps that have a menu and keyboard shortcuts, which is basically every app.

There's so many layouts and things I haven't tried yet either.

If it's an otherwise GUI-heavy app that needs to show lots of stuff, maybe you could not show the ENTIRE keyboard but just one row or something.

I like the idea of things being dynamic too...

Different modes, different modifiers, different layouts, etc. So much to try.

One thing I want to do is make it trivial for me to create new layouts agentically and/or with a drag-and-drop. I think it's easier to make it agentic than drag-and-drop, for sure.

---

## Assistant

Navigating Hardware Limits (Ghosting & Rollover)

Standard membrane keyboards (and basic laptop built-ins) save cost by routing keys through a shared grid matrix without individual diodes.

When you press three keys that form three corners of a rectangle in that circuit grid, pressing a fourth causes **ghosting** (phantom keypresses) or **key jamming** (the controller drops inputs to prevent phantom signals). Standard office keyboards often max out at **2KRO or 6KRO** (2-to-6 key rollover).


```
Standard Keyboard (Matrix Short)      NKRO / Anti-Ghosting (Individual Diodes)
┌───┐   ┌───┐                         ┌───┐   ┌───┐
│ A ├───┤ B │  (Shares trace)         │ A ├───┤ B │  (Isolated by diodes)
└───┘   └───┘                         └───┤►│ └───┤►│
  │       │                           └───┘   └───┘
┌───┐   ┌───┐                           │       │
│ C ├───┤ D ◄── Phantom signal!       ┌───┐   ┌───┐
└───┘   └───┘                         │ C ├───┤ D │  (Press any combination)
                                      └───┤►│ └───┤►│
                                      └───┘   └───┘

```


Relying on **single-key chord triggers** or **toggle layers** rather than holding multi-key clusters is the most robust software fix for standard hardware.

If you ever want full physical polyphony on a QWERTY layout without matrix limitations, upgrading to any basic mechanical keyboard with **NKRO (N-Key Rollover)** completely eliminates the issue—every single key has its own blocking diode, letting you hit 10+ keys simultaneously.

Alternative Applications & Single-Row Compact UIs

Beyond standalone synth modules, a "keyboard-as-canvas" framework fits several application styles:

1. Single-Row / Floating Toolbars

Rather than taking up the entire screen, the app renders a compact horizontal strip matching a single physical row (e.g., `A S D F G H J K L`).

**Contextual Inspector:** Highlight a track or text block, and the single row updates to display instantly accessible operations mapped directly to `A` through `L`.

**Live Sampler / Stutter Strip:** Map audio chops, pitch-bends, or rapid FX triggers to the home row without obscuring your primary workspace.

2. Radial / Modal Palette Replacement

In software like CAD, vector design, or video editing, menus slow down focus. Holding a single modifier (e.g., holding `Space` or `Caps Lock`) temporarily converts the entire QWERTY grid into a visible 1:1 map of tools:

`Q, W, E, R`: Selection tools, transform, rotate, scale.

`A, S, D, F`: Brush sizes, opacity sliders, blend modes.

Releasing the modifier restores standard typing immediately.

Agentic Layout Generation Architecture

Making layout generation **agentic** rather than building a complex drag-and-drop WYSIWYG editor is both significantly faster to implement and far more extensible.

Instead of hardcoding every layout, you define a **strict JSON schema** for what a "Keyboard View" looks like, and let an LLM or local agent emit JSON payloads based on text prompts.

1. The Declarative Layout Schema (`layout.json`)
JSON

```
{
  "name": "Arpeggiator & Scale Controls",
  "active_layer": "base",
  "modifiers": {
    "shift": "secondary_parameters",
    "caps_lock": "latch_mode"
  },
  "keys": {
    "KeyA": {
      "label": "Arp On/Off",
      "type": "toggle",
      "state_path": "arp.enabled",
      "color": "#ff9900"
    },
    "KeyS": {
      "label": "Randomize",
      "type": "trigger",
      "action": "arp.randomize_pattern"
    },
    "KeyD": {
      "label": "Oct -",
      "type": "step",
      "action": "arp.octave_down",
      "display_value": "arp.octave"
    }
  }
}

```

2. The Agent Workflow

**Prompt the Agent:** *"Create a layout for controlling a 4-deck DJ mixer with crossfader, volume kills, and loop triggers."*

**LLM Execution:** The agent receives your current application state schema and outputs the formatted `layout.json`.

**Hot-Reloading:** The UI engine watches the local file or a local WebSocket endpoint, instantly rendering the newly generated keymap canvas live.

This allows you to generate specialized sub-control surfaces on the fly simply by describing what you want to control.

---

## User

I love that the example of a new layout you gave is a dj mixer because that’s exactly one of the things I had in mind!

Djay is great obviously and the Mac app has a ton of keyboard shortcuts but like most apps, it’s a pain in the dick to learn them all!

Plus, I don’t think I would be full satisfied.

I think a design using modifiers could potentially ALMOST replace a CDJ.

The key challenge to overcome tho is a lack of knobs.

Still, there’s always a way. Realistically we can simulate a knob with keys. Tapping, modifier tapping, holding, etc…

It’s gonna be a bit of trial and error and design to get it right but I think it’s possible.




Re: getting a gaming keyboard, that’s certainly something to think about, but honestly the thing that makes this useful is I have my MacBook with me most places and the keyboard is built in. I have a full size digital piano which I love (and want to do software with too!), but it’s in the basement, not on my laptop at all times.




I want to do as much as I can with the normal built in keyboard as possible.

Another big resource that’s not fully tapped yet is the trackpad.

I’m just using it as a scroll controller for mod wheel and it’s great at that but obviously it can do much more and in two axes at once.

---

## Assistant

The trackpad is huge here—especially because macOS gives you access to raw multi-touch data, pressure/force touches, and continuous 2D scroll events. Combining a physical key state with continuous trackpad movement solves the exact mechanical limitation you're running into.

Here is how you can tackle both the **knob/encoder problem on standard keys** and **integrating the trackpad as an analog performance surface**, keeping everything contained entirely to your MacBook.

1. Simulating Knobs & Encoders on QWERTY Keys

Since key switches are binary (on/off), you can emulate analog pots and rotary encoders through time-based or modifier-based interactions:

A. Tapping & Velocity Emulation

**Discrete Step Taps:** Tapping `1` nudges EQ High up by +1dB; `Shift + 1` nudges down by −1dB.

**Hold-to-Ramp (Exponential Acceleration):** Tap for fine adjustments; hold down to sweep parameter values. Accelerating the value curve over time gives you high-precision fine-tuning for subtle EQ nudges without sacrificing the ability to quickly sweep a filter.

B. Dual-Key Push/Pull Pairs

Pair neighboring keys to act as bidirectional encoders.

Plaintext

```
  [ E ]     [ R ]       ->  E = Deck A High EQ (-)
   (- )      (+ )           R = Deck A High EQ (+)

```


Holding `Shift` while tapping either key switches the increment step to high-resolution mode (e.g., 0.1dB instead of 1.0dB).

C. Relative "Key-Dragging" (Trackpad + Key Hold)

This is where you bridge the binary and analog worlds.

Instead of turning a physical knob, **hold a key as a parameter anchor and slide a finger on the trackpad**:

Hold `Q` + Slide Up/Down → Deck A Gain / Volume

Hold `W` + Slide Up/Down → Deck A High EQ

Hold `E` + Slide Up/Down → Deck A Mid EQ

Hold `R` + Slide Up/Down → Deck A Low EQ

This instantly turns 4 key caps into 4 endless rotary encoders without requiring extra screen real estate for virtual knobs.

2. Unlocking the Trackpad as an XY Performance Surface

Since you're on macOS, the trackpad doesn't just have to act as a standard mouse or scroll wheel—it can act as a high-density MIDI controller.


```
       ┌─────────────────────────────────────────┐
       │             Y-Axis (FX Wet/Dry)          │
       │                    ▲                    │
       │                    │                    │
  X-Axis (Filter Cutoff) ◄──┼──► X-Axis (Cutoff) │
       │                    │                    │
       │                    ▼                    │
       │             Y-Axis (FX Wet/Dry)          │
       └─────────────────────────────────────────┘

```

A. The "Hold-Key + XY Pad" Mod Engine

Use keys as modifier gates for 2D gestures on the trackpad:

**`FX` Gate:** Hold `F` and swipe across the trackpad.

**X-Axis:** Low-pass / High-pass Filter Cutoff.

**Y-Axis:** FX Reverb / Delay Resonance.

**Crossfader + Stem Balance:**

Swipe normally on the trackpad → Master Crossfader.

Hold `Space` + Swipe → Isolates/fades vocals vs. drums in real time.

B. Multi-Touch Pinch & Rotate

macOS trackpads support raw pinch and rotate gestures natively:

**Two-finger rotation:** Acts like a literal vinyl jog wheel for nudging pitch or scratching.

**Pinch-in / Pinch-out:** Dynamic loop length manipulation (e.g., pinch down from 1/4 loop to 1/8 to 1/16 roll).

3. Designing for MacBook Keyboard Constraints

To maximize reliability on the built-in Apple Scissor Switch matrix:

The "Latch + Mod" Paradigm

To completely avoid ghosting/jamming limits on the built-in keyboard, avoid holding 4 or 5 keys at once to trigger complex states.


```
┌─────────────────┐       ┌────────────────────────┐       ┌─────────────────┐
│ Tap "Chord Key" ├──────►│ State Latches Active   ├──────►│ Single Key Tap  │
│ (e.g. 'A')      │       │ (Visual indicator on)  │       │ Triggers Action │
└─────────────────┘       └────────────────────────┘       └─────────────────┘

```


**Latched Chords:** Pressing a single assigned key (e.g., `A`) latches a chord or deck focus state into memory.

**Sequential Modifiers:** Tap `Space` once to enter "EQ Mode." Now the entire home row (`A S D F`) transforms into parameter adjustments for the selected deck without requiring you to hold `Space` simultaneously.

**Release Triggers:** Use key release (`keyup`) events for momentary triggers (like beat-jumps or stutter effects) so you never need to stack multiple held key states at once.

4. Proposed Layout: "Modular 2-Deck DJ Harness"

Here is how a single QWERTY surface maps both decks, loops, and trackpad modifiers on a standard MacBook layout:

Row	Keys / Function	Trackpad Modifier Integration
**Number Row (`1 - =`)**	**Deck A / B Cue Points** (Cues 1–4 on `1-4`, Cues 1–4 for Deck B on `7-0`)	Hold key + Trackpad move to adjust cue offset / slip
**Top Row (`Q - P`)**	**Transport & Pitch** (`Q`=Play/Pause, `W`=Sync, `E`=Pitch Nudge -, `R`=Pitch Nudge +)	Hold `Q/W/E/R` + Trackpad Y-axis for fine tempo adjust
**Home Row (`A - L`)**	**Latched FX & EQ Focus** (`A`=Low EQ, `S`=Mid EQ, `D`=High EQ, `F`=Filter)	**Hold any Home Row key** + Slide finger on trackpad to adjust parameters
**Bottom Row (`Z - /`)**	**Loop Rolls & Stutter** (`Z`=1/2 Loop, `X`=1/4 Loop, `C`=1/8 Roll)	Trackpad X-axis controls crossfader by default

This setup gives you full control over two decks, EQ sweeps, loop rolls, and pitch adjustments using only single-finger taps and a single-finger trackpad drag.

---

## User

So that’s the new question: can I make a djay replacement?

I mean what a stupid question.

I am so used to agentic coding that I think giant apps are trivial or something. I COULD but do I want to? No, I don’t really. Not with all the other half working agentic projects I’ve got going on. I’ll need to make a djay midi controller, that’s what I’ll do.

---

## Assistant

That pivot makes total sense. Building an actual audio engine—handling real-time time-stretching, pitch-shifting, audio file decoding, stem separation, and zero-latency output buffers—is a massive software undertaking.

Building a **virtual MIDI controller interface** that hooks directly into djay's existing audio engine is entirely doable, lightweight, and lets you leverage your custom QWERTY canvas concept right now without re-inventing the wheel.

How to Route Your QWERTY App into djay

Since your app runs as a desktop interface, you can make macOS treat it as a class-compliant virtual MIDI device using native core audio tools.


```
┌───────────────────────────┐      Virtual MIDI Bus       ┌───────────────────────────┐
│ Your Custom QWERTY App    ├────────────────────────────►│ Algoriddim djay Pro       │
│ (Tauri / Electron / Web)  │   (e.g., "Virtual-QWERTY")  │ (MIDI Mapping Layer)      │
└───────────────────────────┘                             └───────────────────────────┘

```

1. Emit Virtual MIDI Events

Instead of triggering local audio nodes, your app emits standard MIDI messages (`NoteOn`, `NoteOff`, `ControlChange`) over a virtual MIDI port.

**In Node.js / Bun:** You can use packages like `easymidi` or `midi` to create a virtual input device that appears natively in macOS System Settings.

**In Rust / Tauri:** Libraries like `midir` let you spawn a virtual output port with one line of code.

2. Map the Controls in djay

Once your virtual device is running, open djay:

Go to **djay Settings → MIDI → Devices**.

Select your virtual MIDI device name (e.g., `"QWERTY-FX-Deck"`).

Tap any key/trigger in your custom app while in djay's **Learn Mode** to bind:

**Keys/Taps** → Note On / Note Off (Cue points, Play, Loop Rolls, FX Toggles).

**Trackpad Swipes / Encoder Taps** → Control Change (CC) values 0–127 (Filters, EQs, Volume Faders, Pitch).

The Big Advantage

By acting as a MIDI layer rather than a standalone media player, you gain immediate advantages:

**Zero Audio Engine Overhead:** djay handles the low-latency audio playback, deck sync, waveforms, and file library indexing.

**Native Integration:** You get access to djay's built-in Neural Mix (stem isolation), high-quality FX chains, and Apple Music / local file integrations out of the box.

**Declarative Iteration:** You can completely redesign your QWERTY UI, layout logic, or trackpad mapping in your own app without breaking your DJ setup—djay just sees incoming MIDI CC and Note signals.

It gives you the exact hands-on, hardware-like control surface on your MacBook keyboard while letting djay do all the heavy lifting behind the scenes.

---
