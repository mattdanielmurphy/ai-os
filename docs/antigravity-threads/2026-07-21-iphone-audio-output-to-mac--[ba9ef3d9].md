---
title: "iPhone Audio Output to Mac"
date: "2026-07-21"
conversation_id: "ba9ef3d905241f25"
source: "antigravity"
---

# iPhone Audio Output to Mac

## User

I can't seem to get audio from my iPhone to my Mac using Audio MIDI Setup and a lightning cable.

It showed up on the list and I clicked enable, but I can't see it as an input devices anywhere I look.

---

## Assistant

To see what CoreAudio is registering under the hood, run this in Terminal to copy your current system audio device state to your clipboard, then paste the output back here:

Bash

```
system_profiler SPAudioDataType | pbcopy

```

---

## User

[Attached Context: gemini-run-1784599509524]

```text

Running command in gemini-run-1784599509524...




/Users/matt/Documents/gemini-archive/threads/.gemini-run-1784599509524.sh: line

5: system_profiler: command not found




Press Enter to close...


























































```

you see this?

---

## Assistant

Ah, the shell path in that environment wrapper is missing standard system binaries like `/usr/sbin`.

Let's run it with the explicit system path so it hits the binary directly and copies the audio tree to your clipboard:

Bash

```
/usr/sbin/system_profiler SPAudioDataType | pbcopy

```

---

## User

Audio:




    Devices:




        USB Audio CODEC :




          Output Channels: 2

          Current SampleRate: 48000

          Transport: Unknown

          Output Source: Default




        USB Audio CODEC :




          Input Channels: 2

          Current SampleRate: 48000

          Transport: Unknown

          Input Source: Default




        Matt‚Äôs iPhone 14 Pro Max Microphone:




          Input Channels: 1

          Manufacturer: Apple Inc.

          Current SampleRate: 48000

          Transport: Unknown

          Input Source: Default




        BlackHole 16ch:




          Input Channels: 16

          Manufacturer: Existential Audio Inc.

          Output Channels: 16

          Current SampleRate: 48000

          Transport: Virtual

          Input Source: Default

          Output Source: Default




        External Headphones:




          Default Output Device: Yes

          Default System Output Device: Yes

          Manufacturer: Apple Inc.

          Output Channels: 2

          Current SampleRate: 48000

          Transport: Built-in

          Output Source: External Headphones




        MacBook Pro Microphone:




          Default Input Device: Yes

          Input Channels: 1

          Manufacturer: Apple Inc.

          Current SampleRate: 48000

          Transport: Built-in

          Input Source: MacBook Pro Microphone




        MacBook Pro Speakers:




          Manufacturer: Apple Inc.

          Output Channels: 2

          Current SampleRate: 48000

          Transport: Built-in

          Output Source: MacBook Pro Speakers




        Microsoft Teams Audio:




          Input Channels: 1

          Manufacturer: Microsoft Corp.

          Output Channels: 1

          Current SampleRate: 48000

          Transport: Virtual

          Input Source: Microsoft Teams Audio Device

          Output Source: Microsoft Teams Audio Device




        Jump Desktop Microphone:




          Input Channels: 8

          Manufacturer: Phase Five Systems LLC

          Output Channels: 8

          Current SampleRate: 48000

          Transport: Virtual

          Input Source: Default

          Output Source: Default




        Jump Desktop Audio:




          Input Channels: 8

          Manufacturer: Phase Five Systems LLC

          Output Channels: 8

          Current SampleRate: 48000

          Transport: Virtual

          Input Source: Default

          Output Source: Default

---

## Assistant

Your iPhone is currently being registered as a **Continuity Camera microphone** ("Matt’s iPhone 14 Pro Max Microphone", 1-channel wireless/AirPlay input) rather than a **wired 2-channel Lightning USB audio input**.

When Continuity Camera or AirPlay audio claims the phone, macOS suppresses the wired Lightning audio interface—even though Audio MIDI Setup shows the "Enable" button pressed.

Step 1: Execute the Reset Script

Run this execution block in Terminal. It automatically backs up your coreaudio user preferences and restarts `coreaudiod` and `com.apple.cmio.registerassistants` (which handles Continuity Camera) to force macOS to re-enumerate wired USB audio interfaces.

Bash

```
cp ~/Library/Preferences/com.apple.audio.AudioMIDISetup.plist ~/Library/Preferences/com.apple.audio.AudioMIDISetup.plist.bak 2>/dev/null || true && sudo killall coreaudiod com.apple.cmio.registerassistants 2>/dev/null || true

```

Terminal Output (tmux: gemini-run-1784599548107)
+ Context

```
Running command in gemini-run-1784599548107...

Password:

Press Enter to close...




















```

Send

*To revert your MIDI preferences backup if needed:*

Bash

```
cp ~/Library/Preferences/com.apple.audio.AudioMIDISetup.plist.bak ~/Library/Preferences/com.apple.audio.AudioMIDISetup.plist 2>/dev/null || true

```

Step 2: Re-bind the Lightning Audio Connection

Unplug the Lightning cable from your Mac.

On your iPhone, go to **Settings > General > AirPlay & Handoff** and toggle **Continuity Camera** to **OFF** (this stops iOS from defaulting to the wireless mic interface).

Open **Audio MIDI Setup** on your Mac (`Cmd + Space` -> `Audio MIDI Setup`).

Reconnect the Lightning cable. If prompted on the iPhone, select **Trust This Computer**.

Find **iPhone** in the left sidebar of Audio MIDI Setup and click **Enable**.

Once re-bound, you will see `iPhone` listed as a 2-channel 44.1/48 kHz input device across System Settings and your DAW/apps.

---
