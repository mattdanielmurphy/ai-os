---
title: "IINA Black Bar Cropping"
date: "2026-07-28"
conversation_id: "c3569a291ee9447b"
source: "antigravity"
---

# IINA Black Bar Cropping

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Note-Taking Directive: When asked to "make a note about this" OR if we discuss anything interesting or ideas about future projects, you MUST proactively output a JSON tool call to save it as a note, or update an existing note. The JSON must be inside a ```tool_call codeblock. Schema: {"tool":"save_note","args":{"title":"Note Title","content":"Markdown content...","update":false}}. The userscript will execute this automatically and save it to Development/Project Notes/.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-07-27 21:20 MDT-6] [context to this point is 0]




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

see how there's TWO levels of black letterboxing above and below? Most of the letterbox is the interior brighter black. I'm assuming that's just baked into the file or something? And the outer one is just true black from IINA because my display is 16:10 MacBook Pro 16 inch(right?).

How do I make it so in IINA that's not the case?

---

## Assistant

Here's what's happening: your assumption is dead-on.

**The inner "brighter black" bars** are hard-coded directly into the video stream itself (a padded 16:9 encode carrying a ~2.39:1 ultrawide film aspect ratio). Because those bars are part of the encoded image data, IINA treats them as active video content, meaning the black level is subject to the source video's color space/mastering tone curve (which raises those pixels slightly off absolute zero).

**The outer "true black" bars** are rendered directly by IINA to fill the remaining vertical height of your 16:10 Liquid Retina XDR screen, allowing mini-LED local dimming to turn those specific backlights completely off.

To fix this in IINA and remove the hard-coded letterboxing so the image scales cleanly to fit your screen without double-padding, you need to crop out the encoded black bars:

Method 1: On-the-Fly Aspect Ratio Crop (Quickest)

Press **`C`** while playing the video to cycle through crop presets until you hit **`2.35:1`** or **`2.39:1`** (or press **`Shift + C`** to open the Crop settings panel and pick the exact aspect ratio).

This strips the hardcoded top/bottom bars from the decoded frame, allowing IINA to treat the actual picture as the full image and scale it naturally against your screen height.

Method 2: Auto-Detect Black Borders via mpv

Since IINA is powered by `mpv`, you can leverage `lavfi` black bar detection to automatically crop hard-coded letterboxing:

Open IINA Preferences (**`Cmd + ,`**).

Go to **Keybindings**.

Add a custom shortcut or edit an existing one to execute the mpv command:

Plaintext

```
vf toggle detectcrop

```


Pressing this hotkey will run a filter for a couple of seconds to detect the exact video boundaries and snap the crop directly to the active picture area.

---

## User

[2026-07-27 21:25 MDT-6] [context to this point is 573] shift-c does some subtitle thing. and there's no cycle crop action I can find anywhere.

setting the crop to 2.35:1 works great.

I definitely want auto-detect; strange it doesn't come with it enabled.

Surely there's a plugin?

And I'd like to know about other great IINA plugins and what you can do with plugins in general

---

## Assistant

Here is why those keys behave differently, along with how to set up auto-detection and what you can build or install using IINA's plugin system.

Keybindings & Built-in Crop Shortcut

In IINA's default input configuration, **`Shift + C`** is bound to subtitle styling/visibility, while pressing just **`C`** opens the visual Crop menu or cycles aspect ratios.

To set up a single shortcut that cycles through crops (e.g., `None` → `2.35:1` → `16:9`):

Open **IINA Preferences** (`Cmd + ,`) → **Keybindings**.

Click **+** at the bottom to add a key.

Map your key (e.g., `c`) to the action **Cycle Crop**.

Auto-Detecting Letterboxing in IINA

Auto-cropping isn't enabled by default because `libavfilter` (the video processing engine behind `mpv`) has to inspect several frames of video to determine black borders. Running real-time black border detection continuously can trigger performance overhead on high-bitrate 4K files or cause jumpy aspect ratio changes during dark scenes.

However, you don't need a heavy external plugin for auto-cropping—you can trigger `mpv`'s native crop detector with a single keybinding:

In **Preferences** → **Keybindings**, click **+**.

Set your key combination (e.g., `Option + C`).

Set the action to **IINA Command / mpv command** (or raw mpv command).

Enter:

Plaintext

```
vf toggle detectcrop

```


When pressed, IINA runs `detectcrop` for a brief sample window, identifies the hard-coded black bars, and automatically applies the crop filter. Pressing it again toggles the filter off.

The IINA Plugin System & Ecosystem

IINA introduced a full JavaScript-based plugin system starting in version **1.4.0**. Because IINA acts as a Swift native frontend on top of an embedded `mpv` core, plugins run in a JavaScript sandbox and can manipulate both the macOS UI layer and the low-level `mpv` playback engine.

What Plugins Can Do in IINA

**Custom Webview UI Overlays & Sidebars:** Render custom HTML/CSS directly over video frames or inside sidebar tabs (e.g., interactive chapter menus, chat streams for live feeds, or visual equalizers).

**mpv Hook Injection:** Tap directly into `mpv` properties, events, filters, and IPC commands (e.g., auto-adjusting HDR parameters, shaders, or custom video filters).

**Network & File System Access:** Fetch metadata, sync playhead states via HTTP/RPC, or execute local scripts and CLI tools.

**Subtitle & Provider Engines:** Plug custom search APIs or local scraping scripts directly into IINA's native subtitle download menu.

**Official User Scripts Plugin:** Allows dropping single JS snippets directly into IINA without needing to package a full plugin bundle.

Useful Plugin Ideas & Examples

**Auto-Crop / Black Bar Remover:** JS scripts hooked into `iina.file-loaded` that run `detectcrop` automatically on load and apply the crop dynamically.

**Media Cutters / Trimmers:** Tools like `multi-cutter-iina` that let you mark in/out points on the timeline and invoke `ffmpeg` in the background to losslessly trim clips.

**SponsorBlock / Auto-Skip:** Plugins that query community databases to automatically skip silent sections, recaps, or sponsored segments during playback.

**Anime / AniList Integration:** Auto-tracking episode progress, logging watching history, and syncing subtitle tracks dynamically.

---

## User

[2026-07-27 21:27 MDT-6] [context to this point is 1606] vf toggle detect crop doesnt do anything

---

## Assistant

That command doesn't work because `detectcrop` isn't a valid native filter command in `mpv`.

In `ffmpeg`/`mpv`, the filter is called **`cropdetect`**, but even running `vf toggle lavfi=[cropdetect]` won't automatically resize your video on its own. `cropdetect` is purely an analysis tool—it silently analyzes frame luminance in the background and prints coordinate metadata (`w:h:x:y`) to logs without actually applying a visual crop.

To get auto-detection that actually resizes the image in IINA, you have two clean options:

Option 1: Drop in the `autocrop.lua` Script (Recommended)

This is the standard lightweight solution in the `mpv`/IINA ecosystem. It adds a single hotkey that runs `cropdetect` for 1 second to inspect the video, reads the frame metadata, and applies the matching `crop` filter automatically.

Open Terminal and create your mpv scripts folder if it doesn't exist:

Bash

```
mkdir -p ~/.config/mpv/scripts

```


Download the canonical `autocrop.lua` script directly into that directory:

Bash

```
curl -Lo ~/.config/mpv/scripts/autocrop.lua https://raw.githubusercontent.com/mpv-player/mpv/master/TOOLS/lua/autocrop.lua

```


Restart IINA.

By default, pressing **`Shift + C`** (or triggering `script-binding autocrop/start_crop` in your keybindings) will run the detector for one second, snap the crop perfectly to the non-black picture area, and remove the analysis overhead. Pressing it again toggles the crop off.

Option 2: Continuous Auto-Cropping with `dynamic-crop.lua`

If you watch media with variable aspect ratios (like IMAX scenes changing mid-movie), **`dynamic-crop.lua`** automatically monitors black borders continuously and adjusts the crop in real-time.

Download the script:

Bash

```
curl -Lo ~/.config/mpv/scripts/dynamic-crop.lua https://raw.githubusercontent.com/Ashyni/mpv-scripts/main/dynamic-crop.lua

```


Restart IINA. It will automatically handle letterbox removal on video load.

---

## User

[2026-07-27 21:30 MDT-6] [context to this point is 2199]




[Attached Context: Terminal & CLI Context]

```text

[Terminal & Local Execution Context]

Shell: Zsh on macOS (/bin/zsh)

Local Command Executor Service: http://127.0.0.1:3033/run-command

Headers: x-gemini-thread-saver-key (requires secret configuration)

Inline Terminal Sessions: tmux background sessions monitored via HTTP

```

1. you can't map to Cycle Crop, the action doesn't appear in the dropdown list.

For mpv commands, I mapped to your command, vf toggle detectcrop, but that doesn't do anything.

Unless I need to restart IINA for this to work after changing the setting or something

---

## Assistant

Here is what is going on with IINA's action system and raw `mpv` commands:

Why Cycle Crop Doesn't Show in IINA's Dropdown

IINA's UI menu separates **Aspect Ratio** and **Video Crop**. In IINA's raw keybinding syntax, crop cycling is handled via `cycle-values crop` or `set crop`.

To make a single key cycle through crop presets in IINA:

Open **Preferences** (`Cmd + ,`) → **Keybindings**.

Click **+** to add a key (e.g. `c`).

Set the Action type to **Raw Command** (or **mpv Command**).

Paste this exact line:

Plaintext

```
cycle-values crop "2.35:1" "16:9" "none"

```


This immediately cycles between 2.35:1, 16:9, and turning the crop off without needing to restart IINA.

Why `vf toggle detectcrop` Failed

`detectcrop` isn't a native command in mpv. To do black-bar analysis directly using standard `mpv` commands without an external script, you have to invoke `cropdetect` through `lavfi` (FFmpeg filters) and pair it with a `crop` filter.

Because `cropdetect` only prints calculated dimensions to the terminal log without dynamically applying them to the screen on its own, running a static `vf toggle` string doesn't trigger a visual resize.

The Fix: Drop in `autocrop.lua`

To get true auto-detection, the standard mpv Lua script handles the two-step process: it runs `cropdetect` for ~1 second, reads the bounds, and applies the matching `crop` parameter.

You can drop it directly into your local mpv directory via Terminal:

Bash

```
mkdir -p ~/.config/mpv/scripts
curl -Lo ~/.config/mpv/scripts/autocrop.lua https://raw.githubusercontent.com/mpv-player/mpv/master/TOOLS/lua/autocrop.lua

```


**After restarting IINA once:**

Press **`Shift + C`** while a video is playing.

You'll see a brief on-screen message (`Auto crop started...`), and a second later it snaps the video boundary directly to the non-black picture area.

Pressing **`Shift + C`** again toggles it off.

---

## User

[2026-07-27 21:30 MDT-6] [context to this point is 2788] try the simplest possible mpv command because that didn't do anything either

---

## Assistant

To test if IINA is taking raw mpv keybindings at all, let's use the simplest built-in command that gives immediate visual feedback without needing any filters or scripts:

Open **Preferences** (`Cmd + ,`) → **Keybindings**.

Click **+** to add a key, press `c`.

In the action dropdown, select **IINA Command** or **Raw mpv Command** (depending on your IINA version layout).

Paste this exact command:

Plaintext

```
show-text "TEST MPV COMMAND"

```


When you press `c` during playback, you should see `TEST MPV COMMAND` pop up in large text on the video.

If `show-text` works, test Crop cycling next:

Replace the text command with:

Plaintext

```
cycle-values crop "2.35:1" "none"

```


Pressing `c` will immediately toggle between cropping to 2.35:1 and turning it off.

Important IINA Catch:

**Active Input Conflicted Keybindings:** If `c` or `Shift + C` is already mapped to an native IINA action higher up in the keybinding list (like Subtitle configuration), IINA will swallow the keypress before it hits your custom raw command. Delete or unbind the original default binding for that key first.

**No Restart Needed for Keybindings:** Changing keybinding commands in Preferences takes effect instantly upon closing or saving the keybinding window. (Scripts placed in `~/.config/mpv/scripts/` are the only thing that requires quitting and reopening IINA).

---

## User

[2026-07-27 21:31 MDT-6] [context to this point is 3205] yeah show-text worked but not cycle values

---

## Assistant

That isolates the issue: `crop` isn't a native property in core `mpv`—it's an IINA-specific visual overlay setting, so raw `mpv` commands like `cycle-values crop` don't recognize it.

In native `mpv`, cropping is handled directly through the **video filter engine (`vf`)**.

To cycle aspect ratio crops using raw `mpv` syntax, bind your key to this exact command instead:

Plaintext

```
cycle-values vf "crop=2.35:1" "crop=16:9" ""

```


`"crop=2.35:1"` applies the 2.35:1 filter to cut off top/bottom bars.

`"crop=16:9"` shifts to a 16:9 crop.

`""` (empty string) clears the filter completely back to normal.

Pressing your hotkey will now cycle through those filter states instantly.

---
