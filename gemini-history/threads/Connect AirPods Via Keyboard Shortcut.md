[2026-07-07 20:58] User:
airpods connect via keyboard shortcut utlity

I was using ToothFairy but it actually sucks. I'm using an old pirated edition most likely though unless it's free.

Find a free utility that's updated semi-recently and works

---

[2026-07-07 20:58] Assistant:
Since ToothFairy is a paid app, you don't need to deal with old or unverified versions. There are two robust, completely free ways to connect your AirPods with a keyboard shortcut without adding bloat to your menu bar.

Method 1: The Native macOS Shortcuts App (Highly Recommended)

Apple's built-in **Shortcuts** app can natively handle this without installing any third-party software. It runs cleanly in the background and lets you assign a global hotkey directly.

Open the **Shortcuts** app on your Mac.

Click the **+** (plus icon) in the top right to create a new shortcut, and name it something like *Connect AirPods*.

In the right-hand search bar, look for **Set Playback Destination** and drag it into the main canvas.

Click on the faded "iPhone" or default text in that action block, and select your **AirPods** from the list.

In the right-hand sidebar under the **Shortcut Details** tab (the icon looks like three sliders), check the box for **Use as Quick Action**.

Click **Add Keyboard Shortcut** and type your preferred key combination (e.g., `Option + A`).

**Tip:** If the shortcut doesn't execute immediately from a deep sleep, you can also look up this shortcut inside custom launchers or automated productivity tools to map the hotkey there.

Method 2: `blueutil` (Open-Source CLI Utility)

If you prefer a highly reliable command-line option that executes instantly, **`blueutil`** is a popular, actively maintained open-source utility. It handles Bluetooth connections via terminal commands, making it incredibly lightweight.

1. Install `blueutil`

Open your terminal and install it using Homebrew:

Bash

```
brew install blueutil

```

2. Find Your AirPods' MAC Address

Ensure your AirPods are paired, then run:

Bash

```
blueutil --paired

```


Look for your AirPods in the output list and copy the string of numbers/letters separated by dashes or colons (e.g., `aa-bb-cc-dd-ee-ff`).

3. Create the Connection Trigger

The exact command to force a connection is:

Bash

```
blueutil --connect aa-bb-cc-dd-ee-ff

```


You can take this single-line command and bind it to a hotkey using any system-level keyboard shortcut utility or automation framework you already run. It will execute silently in a fraction of a second without launching a heavy GUI.

---

[2026-07-07 21:00] User:
there IS NOT playback destination!

unless it's new to Tahoe.

problem with blueutil (I think) is, the airpods stay connected via bluetooth, but they can be actively playing back to an iphone e.g.

---

[2026-07-07 21:00] Assistant:
That makes perfect sense—`blueutil` only handles the low-level Bluetooth connection handshake. If your iPhone has an active audio session, the hardware handshake completes, but macOS won't automatically steal the active audio engine route away from iOS.

To fully "pull" the audio connection from an iPhone to your Mac for free, you need to link the Bluetooth connection with a CoreAudio output override using `switchaudio-osx`.

1. Install the Audio Switcher Utility

Grab the command-line audio selector via Homebrew:

Bash

```
brew install blueutil switchaudio-osx

```

2. Grab Your Device Specs

Make sure your AirPods are nearby and run these two commands to get the exact strings you need:

**Get the MAC Address:**

Bash

```
blueutil --paired

```


*(Copy the address, e.g., `aa-bb-cc-dd-ee-ff`)*

**Get the Exact Audio Name:**

Bash

```
SwitchAudioSource -a

```


*(Look for your AirPods in the output list and copy the exact string, including any special characters or smart apostrophes, e.g., `Matthew’s AirPods`)*

3. The Hijack Script

Combine both actions into a clean, two-line execution block. This forces the Bluetooth handshake first, then immediately commands the macOS audio layer to drop its current output and anchor to the AirPods:

Bash

```
#!/bin/bash
# Force the physical hardware link
blueutil --connect "aa-bb-cc-dd-ee-ff"

# Force the core audio layer to switch outputs
SwitchAudioSource -s "Your AirPods Name"

```

How to Bind It Globally

Since you don't want menu bar bloat, you can wrap this script directly into a global hotkey tool you already use:

**Raycast:** Save it as a `.sh` file inside your Script Commands directory, add the Raycast metadata comments at the top, and assign your hotkey in Raycast settings.

**Hammerspoon:** Put it in your `init.lua` inside an `hs.hotkey.bind` block wrapping `hs.execute()`.

**Alfred:** Drop it into a simple Workflow triggered by a Hotkey object wired to a "Run Script" action.
