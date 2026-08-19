---
title: "Screen Capture to Gemini Workflow"
date: "2026-08-13"
conversation_id: "7361a9f8-9b5b-5a3d-82b2-d8a0ec62a247"
source: "antigravity"
---

# Screen Capture to Gemini Workflow

## USER_EXPLICIT (2026-08-13T18:54:11.014564)

new idea: I want a way to very quickly take a screenshot of something, type in a query, and have that open a new chat in gemini.google.com with that screenshot attached.

An extension of that:

I can take a sort of pseudo screen recording, where I set an area of my screen, and the end result is the agent sees a series of images, representing things changing over time (could be a new tab of the interface, or anything which has motion to it). So it's like it gets a flipbook of what's actually happening on screen. Conceivably you could expose some options of like, how detailed the capture should be or whatever, but ideally somehow the tool determines based on the content what an appropriate "framerate" is.

But of course the key is: we don't want to attach like a video or something (idk if that's even possible) or 24fps of images especially when nothing's actually changing frame to frame.

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-09 20:11" -->

---
## MODEL (2026-08-13T18:54:11.014567)

That is an excellent workflow concept, particularly for reducing token bloat and keeping context highly relevant. Sending a standard video file or a raw 30fps image dump introduces massive overhead, whereas an intelligent "flipbook" or variable-framerate image sequence gives the model exactly what it needs to see changes over time without the noise.

Because you are working within the macOS ecosystem and have a highly automated, keyboard-driven environment, you can build this using standard CLI tools, structural shell scripts, and an automation wrapper like Raycast, Alfred, or Keyboard Maestro.

Here is a breakdown of how both phases of this idea can be structurally implemented.

Phase 1: Quick Screenshot + Custom Query Link

The web interface for Gemini (`gemini.google.com`) doesn't officially expose a URL scheme or public query parameter that accepts an arbitrary file path attachment via a simple `open` command. However, you can achieve a seamless workflow by leveraging the **system clipboard**.

When you copy an image directly to your macOS clipboard, you can open Gemini via a URL, paste your query, and manually hit `⌘V` to attach the image.

The Shell Blueprint

You can wrap this logic into a single script triggered by a global hotkey:

Bash

```
#!/bin/bash

# 1. Define temporary file path
TEMP_IMG="/tmp/gemini_capture.png"

# 2. Trigger interactive screenshot (select area) and save to temp file
screencapture -i "$TEMP_IMG"

# 3. If the user cancelled the screenshot, exit cleanly
if [ ! -f "$TEMP_IMG" ]; then
    exit 0
fi

# 4. Copy the image file data directly to the macOS clipboard
osascript -e "set the clipboard to (read (POSIX file \"$TEMP_IMG\") as JPEG picture)"

# 5. Clean up the temp file
rm "$TEMP_IMG"

# 6. Prompt user for text query (Example using basic AppleScript; can be replaced by Raycast UI)
QUERY=$(osascript -e 'display dialog "Enter your Gemini Query:" default answer "" buttons {"OK"} default button 1' -e 'text returned of result')

# 7. Encode the query for the URL
ENCODED_QUERY=$(php -r "echo urlencode('$QUERY');")

# 8. Open Gemini with the query pre-filled in the URL parameters
open "https://gemini.google.com/app?q=${ENCODED_QUERY}"

# Note: Once the browser opens, simply press Cmd+V to paste the image into the prompt box.

```

Phase 2: The Variable-Framerate "Flipbook" Engine

To capture motion without creating massive files or sending duplicate frames, you need a **perceptual hashing** or **frame-differencing** mechanism. Instead of a fixed frame rate, the capture loop takes a screenshot, compares it to the previous one, and only retains it if the visual difference exceeds a specific threshold.

Structural Logic for the Capture Loop

**Initialization:** The user selects a screen boundary (using `screencapture -R`).

**The Sampling Loop:** Captures a frame every X milliseconds (e.g., every 200ms to allow a responsive max framerate of 5fps).

**The Delta Check:** Compares `Frame_N` to `Frame_N-1`.

If the structural difference is below a specific percentage (e.g., < 2% change), the frame is discarded.

If the difference is above the threshold, it means a meaningful change happened (a menu opened, text appeared, a tab switched). The frame is saved to a sequence directory.

**The Compilation:** When the user stops recording, the script bundles the remaining unique frames.

Lightweight Tools for Frame Comparison

To do this locally and instantly on macOS without heavy video editing software, you can use binary utilities via Homebrew:

**`ImageMagick` (`compare` utility):** You can run a quick metric check between two consecutive temp files:

Bash

```
compare -metric RMSE frame1.png frame2.png null: 2>&1

```


This outputs a distortion value. If it's `0` (or close to it), nothing changed.

**Python + `opencv-python` / `Pillow`:** A tiny, background Python daemon can poll the screen coordinate area, calculate the Mean Squared Error (MSE) or Structural Similarity Index (SSIM) between frames in memory, and only dump files to disk when a threshold is breached.

Feeding the Multi-Image Prompt to Gemini

Since the web interface requires manual uploading/pasting of multiple files, a multi-image "flipbook" approach shines brightest when interacting directly with the **Gemini API** via an agent harness or custom CLI tool.

The API natively accepts an array of inline data blocks (`image/jpeg` or `image/png`) inside the contents payload. Passing an array of 4–8 mathematically distinct images mapping out a timeline works beautifully:

JSON

```
{
  "contents": [
    {
      "parts": [
        {"inline_data": {"mime_type": "image/jpeg", "data": "BASE64_FRAME_1"}},
        {"inline_data": {"mime_type": "image/jpeg", "data": "BASE64_FRAME_2"}},
        {"inline_data": {"mime_type": "image/jpeg", "data": "BASE64_FRAME_3"}},
        {"text": "Analyze this sequence of events on my screen. Why did the build fail between step 2 and step 3?"}
      ]
    }
  ]
}

```


This ensures the model receives a highly compressed, purely chronological representation of the action without wasting tokens on static states.

How do you envision managing the controls for the recording state—would you prefer a global keyboard shortcut toggle to start/stop the capture, or an interactive overlay?

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-10 00:17" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.014569)

can you describe what this feature IS exactly? I did it in my prompt of course but not as well as you could I'm sure

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-10 00:17" -->

---
## MODEL (2026-08-13T18:54:11.014570)

This feature can be described as **Perceptual Frame-Differencing Capture** (or colloquially, an **Intelligent Context Flipbook**).

At its core, it is a content-aware, non-linear screen recording workflow designed specifically for Multimodal Large Language Models (LLMs). Instead of recording time continuously, it records **state changes**.

Here is the exact breakdown of what this feature is, how it behaves, and why it is fundamentally different from traditional screen recording:

1. Perceptual vs. Temporal Sampling

Traditional video capture is **temporal**—it takes a snapshot every 1/24 or 1/60 of a second, completely blind to whether the pixels actually changed.

This feature is **perceptual**. It uses a lightweight vision algorithm in the background to monitor a bounded coordinate space. It only hits the "shutter" when it detects a mathematical variance above a specific threshold between the current live screen state and the last saved frame.

**The Result:** If you are staring at a static line of code for two minutes thinking, the tool captures exactly **one frame**. If you click a dropdown menu, execute a command, and switch tabs over the span of three seconds, it captures **three or four frames** in rapid succession to map out the action.

2. State-Driven Variable Framerate

The system effectively treats your user interface as a state machine. The "framerate" is entirely fluid, scaling from **0 fps** during idle periods up to a pre-defined ceiling (like **5 fps**) during high-activity UI transitions. It filters out human latency (pauses, reading time, typing delays) and isolates the mechanical transitions of the software.

3. Token-Optimized Chronological Storyboarding

Instead of forcing an LLM to parse a heavy, lossy video file containing thousands of redundant frames, this feature outputs a lightweight, chronologically ordered **storyboard** of distinct images.

Because LLMs process images as flat grids of visual tokens, omitting identical frames saves massive amounts of context window space. It presents the model with a dense, noise-free timeline: *State A → Action → State B → Outcome.*

The Workflow in Action

Imagine trying to debug an intermittent UI bug or a multi-step installation process:

You drag a bounding box over your terminal or browser window.

You perform the actions. The script quietly samples the screen, dropping 95% of the frames because they contain no new visual information.

You stop the capture.

The tool instantly compiles a clean sequence of 5 perfectly distinct images capturing the exact progression of the error, bundles them with your text query, and ships them directly to the model's context.

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-10 00:18" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.014571)

Ok, but what's just like phase 2. I can also just do a simple screenshot.

And I described how I want the UI to be, and you haven't done that.

Like I'm trying to fill in another agent here who knows nothing of this

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-10 00:18" -->

---
## MODEL (2026-08-13T18:54:11.014572)

Here is a precise, standalone feature specification you can hand directly to another agent or developer to build Phase 2.

Feature Spec: Perceptual Screen-Capture "Flipbook" Engine
Objective

Create a macOS automation utility that allows a user to select an area of the screen, record a series of UI state changes over time, and output a token-optimized sequence of unique images (a "flipbook") instead of a video file. This sequence, along with a user text query, is then packaged and sent to an LLM.

1. User Interface & Workflow Experience

**Trigger:** The user invokes the feature via a global hotkey or system shortcut.

**Area Selection:** An interactive crosshair appears (similar to macOS `⌘⇧4`), allowing the user to drag and define a bounding box over a specific target area of their screen (e.g., a terminal window or a browser layout).

**Capture Controls:** A minimal UI overlay or menu bar icon indicates recording is active, displaying options to adjust sensitivity ("Capture Detail") or manually stop the recording.

**Query Input:** Upon stopping the recording, a text input modal appears where the user types their prompt or query for the AI.

**Output Delivery:** The tool bundles the unique image sequence and the text prompt together, opening a new session with the model where the chronological storyboard is fully attached.

2. Core Engine: Content-Aware Variable Framerate

The engine eliminates token bloat and redundant frames by utilizing **perceptual frame-differencing** instead of a fixed temporal frame rate.

**The Sampling Loop:** The background process captures the target screen area at a frequent interval (e.g., a max ceiling of 5 frames per second, or every 200ms).

**The Delta/Threshold Mechanism:** Every newly sampled frame (Frame
N
	​

) is immediately compared in memory to the last saved frame (Frame
N−1
	​

) using a lightweight visual distance metric (like Mean Squared Error or Structural Similarity).

**Static States (Idle):** If the visual difference falls below a user-configured threshold (e.g., < 2% pixel change), the frame is instantly discarded. The effective frame rate drops to **0 fps**.

**Dynamic States (Action):** If a menu opens, text prints, or a tab changes, the visual difference spikes above the threshold. The frame is committed to the sequence. The frame rate dynamically scales up to capture the motion.

**The Storyboard Array:** When execution halts, the user is left with a tightly compressed, perfectly ordered array of 3–8 highly distinct image frames that cleanly map out the timeline of events without any duplicate "dead air."

Why This Design Matters to the Receiving Agent

Traditional video files introduce massive computational overhead, or are outright unsupported by simple chat interfaces. Dumping a standard 24fps sequence wastes massive context windows on identical images.

This engine acts as an intelligent pre-filter, optimizing the context window so the receiving agent gets a dense, sequential storyboard: **State A → Trigger Event → State B → Outcome.**

How would you like to refine this spec for the other agent?
Generate the technical stack implementation details
Create a specific system prompt for the receiving agent

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-10 00:24" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.014574)

ok, let's take a step back and talk about this.

I think this is POSSIBLE and would be quite cool, but it's out of scope right now.

I think we want is:

1. start new chats with a screenshot extremely fast anywhere with a keyboard shortcut

2. ^ that plus you can take several successive screenshots easily, and the UI shows the screenshots you've got, and then all at once those can be attached to the agent in a way where the agent knows the order the user wants them to be.

3. the intelligent "live capture" mode




Where 2 is less important than 1, and 3 is insanely less important than 2, and doesn't offer THAT much benefit now that I think about it, especially in comparison to how hard it would be to get it to work well.




So right off the bat, I just want a high-level document describing each "phase"

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-10 00:24" -->

---
## MODEL (2026-08-13T18:54:11.014575)

Here is a high-level product blueprint that scales from the immediate, friction-free single capture up to the full sequence workflow, treating the automated "live" mode as a distant, long-term stretch goal.

Product Blueprint: Context-Driven Screen Capture for LLMs
Core Vision

To eliminate the friction of getting visual UI context into an LLM session. Instead of manually saving, dragging, dropping, and typing, this utility uses system shortcuts and a lightweight overlay to capture exactly what you see and ship it immediately to the model along with your intent.

Phase 1: High-Speed Single Capture (The Foundation)

**Goal:** Take a screenshot, type a prompt, and be inside a new Gemini chat with that image attached in under 5 seconds.

**The User Experience:**

Press a global hotkey (e.g., `⌥S`).

The screen dims slightly; you drag a bounding box over the target area.

As soon as you release the mouse, a minimal text input modal pops up right at your cursor.

You type your query and hit `Enter`.

**Behind the Scenes:** * The tool saves the image to a temporary path and copies it straight to the macOS clipboard.

It URL-encodes your text prompt and opens the browser directly to `gemini.google.com/app?q=Your+Query`.

*Note:* Because browser security sandboxes prevent direct file injection via URL parameters, you simply hit `⌘V` once the page loads to drop the image right into the prompt box.

Phase 2: Manual Storyboard Sequence (The Sweet Spot)

**Goal:** Capture a multi-step user flow or chronological sequence manually, ensuring the agent understands the exact order of events without overwhelming the chat interface.

**The User Experience:**

Press the global hotkey to enter "Sequence Mode".

You drag a bounding box over a persistent target area.

A small, unobtrusive overlay or floating tray appears at the edge of your screen. Every time you hit a capture shortcut (or click a "Snap" button), a thumbnail of the new state drops into the tray sequentially (e.g., Frame 1, Frame 2, Frame 3).

The tray allows you to quickly re-order or delete frames if you slipped up.

You type your master query into the tray's text field and hit submit.

**Behind the Scenes:**

The utility numbers the files chronologically on disk (`frame_01.png`, `frame_02.png`).

Because sending multiple files cleanly to the standard web UI via clipboard is brittle, this phase is optimized for a custom developer harness or CLI tool hitting the **Gemini API**.

The tool constructs a single API payload containing the array of images in their explicit array order, appended with your text prompt, ensuring the model reads the chronological timeline perfectly.

Phase 3: Perceptual Live Capture (The Future Stretch Goal)

**Goal:** Completely automate Phase 2 for hands-free documentation of complex or rapid motion, running only when things actually change.

**The User Experience:**

You select an area of the screen and hit "Record".

You interact with your app naturally (switching tabs, running a terminal command, opening a drop-down).

You hit "Stop" and type your prompt.

**Behind the Scenes:**

Instead of making you manually snap every frame, a background engine samples the bounding box at a high frequency (e.g., every 200ms).

It uses a lightweight pixel-differencing metric to discard static frames. If nothing changes while you read a line of text, it captures nothing. If a menu opens, it snaps a frame.

It outputs the exact same clean, ordered image array as Phase 2, but completely automates the capture logic.

By prioritizing Phase 1 and Phase 2, you solve 95% of the workflow friction immediately using basic macOS automation hooks, leaving the complex computer-vision engineering of Phase 3 as an optional optimization down the road.

<!-- /gemini-message -->

---

<!-- gemini-message index=9 role=user timestamp="2026-07-10 00:26" -->

---
## USER_EXPLICIT (2026-08-13T18:54:11.014576)

ok so let's go way higher level. This is going to be PART of my app. I'm building the scaffolding for the app, and I want to fill the agent in on our plans.

I don't have to give it all this detail, especially bc phases 2 and especially 3 are a long way off, but I want it to know what's coming, kind of. Maybe an architectural decision would really help or hamper these planned features, who knows?

So yeah, just in a few sentences, what do we want to do and what does it entail

<!-- /gemini-message -->

---

<!-- gemini-message index=10 role=assistant timestamp="2026-07-10 00:26" -->

---
## MODEL (2026-08-13T18:54:11.014577)

We are implementing an incremental, context-driven **Screen Capture Engine** into the application framework. The roadmap scales from instant single-frame captures to complex, chronological multi-frame state tracking.

Architecturally, this requires setting up a decoupled, flexible **Context Assembly Pipeline** right now:

**What we are doing:** Designing a system that captures bounded screen regions, pairs those visual states with user intent (text queries), and structures them into sequential payloads for multimodal LLM consumption.

**The phased progression:** It begins as an immediate, hotkey-driven single screenshot utility (Phase 1), expands into a manual sequential multi-image storyboarding tray (Phase 2), and eventually integrates a background perceptual frame-differencing loop to automate sequence tracking based on active UI state changes (Phase 3).

**Architectural requirements:** To prevent major refactors down the line, the app’s internal prompt-building layer must treat visual context as a **chronologically ordered array of images** from day one, rather than a single static file. The capture module must also decouple coordinates and sampling logic from the output delivery system so we can easily swap a manual trigger for a background polling daemon when moving to later phases.

<!-- /gemini-message -->

---
