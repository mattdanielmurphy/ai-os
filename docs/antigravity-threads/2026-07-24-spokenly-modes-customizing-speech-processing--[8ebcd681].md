---
title: "Spokenly Modes: Customizing Speech Processing"
date: "2026-07-24"
conversation_id: "8ebcd681f6e5f8f7"
source: "antigravity"
---

# Spokenly Modes: Customizing Speech Processing

## User

why different modes?

---

## Assistant

Based on the documentation, **Modes** in Spokenly let you create distinct dictation profiles so you can instantly adapt how your speech is processed, transcribed, and inserted based on what you are doing—without having to reconfigure your settings every time.

Here is why you would use different modes:

Key Benefits

**Custom AI Instructions for Different Tasks:** You can set custom prompts for specific workflows (e.g., one mode for verbatim transcription, one for fixing grammar/tidying up thoughts, one for summarizing, or one for translating your speech into another language).

**Tailored Transcription Models & Providers:** Different tasks require different balances of speed and accuracy. You can configure individual modes to use specific transcription engines (e.g., Whisper, Deepgram Nova, Apple Speech Analyzer) or AI LLM providers (e.g., OpenAI, Anthropic, or custom local models via BYOK).

**Context-Aware Output Actions:** You can choose what happens to the processed text per mode—such as auto-inserting text directly into your cursor, copying it to your clipboard, or automatically pasting and hitting Enter (useful for chat apps).

**Selective Context:** You can configure a mode to pull in additional context like your active browser URL, the currently focused app, surrounding text, or clipboard content to make the AI's output more relevant.

**Automation & Agentic Actions:** Modes on macOS can trigger automated actions right after dictating, such as running a Google Search or executing bash scripts.

Seamless Switching

Rather than manually opening the app settings to change configurations, you can switch modes on the fly using:

**Trigger Words:** Prefixing your speech with a trigger word (e.g., saying *"email hey John..."* automatically routes that dictation through your "Email" mode).

**App or Website Auto-Activation:** Automatically switching modes when you focus on specific applications (e.g., Slack vs. VS Code) or active web pages.

**Custom Keyboard Shortcuts:** Setting dedicated shortcuts with trigger styles like push-to-talk, toggle, or double-tap.

---

## User

Right so to do an action, I need to make a new mode that puts it into: action mode? Kind of thing?

---

## Assistant

Exactly. You don't trigger "actions" directly from a generic dictation button—instead, you create a dedicated **Mode** that has that specific action attached to it.

When you create or edit a mode in Spokenly, you can configure it so that as soon as your dictation finishes, it triggers an **Agentic Action** (like running a Google Search or executing a custom bash script).

How to set it up:

**Create a Mode:** Set up a new mode (e.g., call it *"Search"* or *"Run Script"*).

**Attach the Action:** Under that mode’s settings, enable the desired **Agentic Action** or **Bash Script**.

**Trigger It On the Fly:** Whenever you want to execute that action, invoke that specific mode using any of these methods:

**Trigger Word:** Say *"search best coffee shops near me"* (it strips the word "search", formats your query, and opens Google Search).

**Dedicated Shortcut:** Bind a unique keyboard shortcut directly to that action mode.

**App/Site Auto-Activation:** Set the mode to automatically turn on whenever you switch to a specific app.

---

## User

is it possible to have an always listening trigger word like "hey siri"?

---

## Assistant

No, Spokenly doesn't support an always-listening voice wake-word like "Hey Siri" or "OK Google."

Instead, **trigger words** in Spokenly work within an active dictation session:

You press your dictation hotkey (or push-to-talk button) to start recording.

You speak the trigger word at the very beginning of your sentence (e.g., *"Search best coffee shops near me"*).

Spokenly strips the trigger word ("Search") from the text and routes the remaining dictation through that specific mode.

To start dictating without touching a key, you'd still need an external system-level trigger (like macOS Voice Control or a Siri Shortcut) to initiate the Spokenly dictation shortcut hands-free.

---

## User

There is some way to make that happen though, right?

---

## Assistant

_No text extracted._

---

## User

some kind of way to run a daemon on your Mac that always listens for a phrase and then activates certain things.

---

## Assistant

You are absolutely on the right track! While Spokenly doesn't have a native wake-word feature, you can definitely set up a background daemon or use existing macOS tools to create an always-listening trigger. For instance, you could use macOS Voice Control or a custom script paired with a local speech-to-text model to monitor your microphone and activate Spokenly whenever it hears your phrase. Would you like to explore how you might set that up?

---

## User

absolutely

---

## Assistant

Here are the primary ways to set up an always-listening wake-word daemon on macOS to trigger actions or initiate dictation without relying on native support inside an app like Spokenly:

1. Using Built-In macOS Voice Control (No Coding Required)

macOS includes a native accessibility feature called **Voice Control** that continuously runs in the background and listens for custom commands.

**How it works:** You define a custom phrase (e.g., *"Activate Spokenly"*) and tell macOS to trigger a keypress, run a Shortcut, or launch a script when it hears it.

**Setup:**

Go to **System Settings → Accessibility → Voice Control**.

Turn **Voice Control** ON.

Click **Commands…** → click the **`+`** button to add a custom command.

Set **When I say**: e.g., *"Start Dictation"*.

Set **Action**: Choose **Press Keyboard Shortcut** (and map it to your Spokenly dictation key) or **Run Shortcut**.

2. Using Local Open-Source Wake-Word Engines (Lightweight & Offline)

If you want a dedicated background daemon running in the terminal or as a `launchd` service, you can use specialized wake-word detection libraries in Python or Rust. These run locally on-device with practically zero CPU overhead until triggered.

Popular Frameworks:

**openWakeWord:** An open-source audio wake-word detection framework. It runs locally, supports custom models, and consumes very little memory/CPU.

**Porcupine (by Picovoice):** An ultra-lightweight, highly accurate wake-word engine with a free tier. It allows you to generate custom wake phrases (e.g., *"Hey Computer"*).

**Rustpotter:** An open-source, local wake-word spotter written in Rust, ideal if you want a binary daemon with low footprint.

3. How a Custom Background Daemon Architecture Works

If you want to script this yourself:

**Audio Stream Listener:** A lightweight Python/Rust process runs as a `launchd` background daemon using `PyAudio` or `cpal` to continuously sample the default microphone input in short audio chunks.

**Wake-Word Spotting:** The audio buffer is passed through `openWakeWord` or `Porcupine`.

**Execution Trigger:** Once the probability threshold is hit for your phrase, the daemon sends a system signal:

**Simulate Keypress:** Using `cliclick` or AppleScript (`osascript -e 'tell application "System Events" to key code ...'`) to trigger your dictation or mode hotkey.

**URL Scheme / AppleScript Handoff:** Trigger a native macOS event or launch an app directly.

Example Minimal Python Daemon Blueprint
Python

```
import pyaudio
import numpy as np
from openwakeword.model import Model
import os

# Initialize openWakeWord model
oww_model = Model(wakeword_models=["hey_my_app"])

# Setup audio input stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

while True:
    # Read audio chunk from mic
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    
    # Get prediction
    prediction = oww_model.predict(data)
    
    # Trigger action when wake word detected
    for wakeword, score in prediction.items():
        if score > 0.5:
            # Trigger shortcut or hotkey via AppleScript
            os.system("osascript -e 'tell application \"System Events\" to keystroke \"d\" using {control down, option down}'")
            oww_model.reset()

```


By wrapping a script like this in a `com.user.wakeword.plist` file inside `~/Library/LaunchAgents/`, macOS will keep it running automatically in the background whenever you log in.

---

## User

holy shit Voice control is super cool but there's a million commands enabled by default and I don't trust I'll not say any of them by accident.

I don't see how I can disable them all at once

---

## Assistant

It is a common headache—by default, Apple turns on literally hundreds of system overlay and navigation commands (like "Click Cancel", "Scroll down", "Open Mail") that can fire off by accident when you're just chatting near your mic.

Apple doesn't provide a single "Disable All" button in the standard GUI, but you can scrub or manage them quickly using a few straightforward methods:

Method 1: The Quick Filter Checkbox Trick (GUI)

While there isn't a master toggle, you can turn off entire **categories** at once rather than unchecking individual commands:

Open **System Settings → Accessibility → Voice Control**.

Click **Commands…**.

In the left sidebar, click on each category (e.g., *Basic Navigation*, *Text Editing*, *Overlays*).

Uncheck the main checkbox at the top of the category list—this disables every command in that entire group in one click.

Repeat for each category until only **Custom** (where your own commands live) remains active.

Method 2: Turn On "Overlay" or Target Specific Commands Only

If you only want Voice Control to listen for your specific wake word or custom trigger and ignore casual conversational words:

**Use precise multi-word triggers:** Name your custom commands something distinct that you'd never say in casual conversation (e.g., *"Initiate Spokenly"* or *"Engine Start"* instead of *"Start"* or *"Dictate"*).

**Enable "Attention Aware":** In the Voice Control settings, toggle on **Attention Aware** (on Apple Silicon Macs with a FaceTime camera). Voice Control will sleep when you aren't looking directly at your screen, preventing ambient room speech from triggering anything.

Method 3: Reset / Wipe via Terminal (Advanced)

Voice Control stores enabled/disabled state preferences in user defaults. If you want a clean slate without manually unchecking categories:

You can disable all built-in commands by resetting the Voice Control command plist via Terminal:

Bash

```
# Backup existing preferences first
defaults read com.apple.speech.voicecontrol.prefs > ~/vc_prefs_backup.plist

# Disable all default command sets
defaults write com.apple.speech.voicecontrol.prefs UniversalCommandsEnabled -bool false

```


**Note:** After running default overrides, toggle Voice Control off and on in System Settings for the changes to load.

---

## User

I suddenly want to try and make an actually-good Siri.

I guess right now I want SUPER fast and quite capable, able to run basic actions with my Mac.

I guess I should just make it a shortcut that triggers this Spokenly huh?

Add a "Siri" mode?

---

## Assistant

That is a great way to architect it! Using Spokenly as the **input/action engine** combined with a quick keybinding or native trigger gives you a modular, fast setup.

Here is how you can set up a "Super Siri" replacement mode:

Step 1: Create the "Siri" Mode in Spokenly

In Spokenly, add a new Mode tailored specifically for quick system commands and intelligence:

**Name:** `Siri` (or `Assistant`)

**Transcription Engine:** **Groq** (using Whisper Large V3 / Llama) or **Deepgram Nova 2**. Both feature lightning-fast inference times (often sub-200ms).

**AI Provider:** **Groq** (e.g., `llama-3.3-70b-versatile`) or **OpenAI** (`gpt-4o-mini`). These give near-instant responses compared to heavier reasoning models.

**AI Instructions:** Give it a concise system prompt so it returns short, direct, actionable text without fluff:

*"You are a fast macOS voice assistant. Be direct and extremely concise. If the user asks for a calculation or factual answer, output only the answer. If the user asks to perform an action, format the intent clearly."*

**Output Action:** Set to **Copy to Clipboard** or **Auto-insert** depending on where you want the answer to go.

Step 2: Wire Up Mac Actions

To handle local system control (opening apps, running scripts, controlling audio), take advantage of Spokenly's built-in hooks:

Option A: Use Spokenly's Agentic Actions / Bash Scripts

Inside your new "Siri" mode settings, turn on **Agentic Actions** or attach custom **Bash Scripts**. This lets Spokenly execute terminal commands or AppleScripts directly after it finishes processing your voice prompt.

Option B: Route via macOS Shortcuts App

You can create a custom Apple Shortcut:

Create a Shortcut named **"Ask Siri"**.

Add the action **"Dictate with Spokenly"** (selecting your new *Siri* mode).

Pass the resulting text into a **"Run Shell Script"** or **"Run AppleScript"** block.

Step 3: Triggering It

You can bind your new "Siri" mode in a couple of ways:

**Keyboard Shortcut:** Assign a global hotkey directly to the *Siri* mode inside Spokenly (e.g., `Option + Space` or a double-tap).

**Raycast / Alfred Integration:** If you use Raycast, you can map a hotkey to trigger the Spokenly dictation shortcut or run the Apple Shortcut wrapper.

**Trigger Word:** If you are already dictating, you can simply start your sentence with *"Siri ..."* to temporarily switch to this mode on the fly.

---
