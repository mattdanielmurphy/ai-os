---
title: "Does this have a velocity setting? Seems to have no dynamic "
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "47679fa5-84d5-515c-a1fa-b6611a3e2a83"
url: ""
---

# Does this have a velocity setting? Seems to have no dynamic 

> [!NOTE]
> Archived Gemini Thread: [Does this have a velocity setting? Seems to have no dynamic ]() | Date: 2026-08-13

## User

Does this have a velocity setting? Seems to have no dynamic range currently

---

## Gemini

Based on the image, you have a Yamaha P-series digital piano (likely a P-85 or P-95). These models definitely support touch sensitivity (velocity), but it sounds like yours might be set to a "Fixed" or "Hard" touch response curve.


To adjust the velocity settings without a screen, you’ll need to use a combination of the Grand Piano/Function button and the keys on the keyboard.


How to Adjust Touch Sensitivity

* Hold down the Grand Piano / Function button (the one used for selecting voices).

* While holding it, press one of the following keys at the far left of the keyboard (usually the lowest A, A#, B, or C):

* Lowest A (A-1): Fixed (No dynamic range; every note plays at the same volume).

* Lowest A# (A#-1): Soft (Easy to get a loud sound).

* Lowest B (B-1): Medium (The standard default).

* Lowest C (C0): Hard (Requires a very strong strike to get a loud sound).





Why it might feel "flat"

* Organ/Harpsichord Modes: If you are using the Organ or Harpsichord voices, these instruments are historically non-velocity sensitive, so the keyboard will mimic that behavior by default.

* Fixed Setting: It’s very common for these to accidentally get toggled into "Fixed" mode, which effectively turns off velocity.


If you switch it to Medium and still feel no difference, there could be a sensor issue, but usually, the key-combination reset fixes it.


Since you’re working with VSTs and MIDI, you might also check if your DAW or VST host has a MIDI filter or "velocity compressor" active that’s flattening the input signal before it hits your piano libraries.

---

## User

It’s a p60

---

## Gemini

For the Yamaha P-60, the process is similar but uses specific keys to toggle through the sensitivity presets. If it feels like there is no dynamic range, the "Touch Sensitivity" is likely set to Fixed.


How to Change Velocity Settings
To change the setting, hold down the [GRAND PIANO] button and press one of the following keys at the far left of the keyboard:



* A-1 (Lowest A): Fixed — Velocity is disabled; every note plays at the same volume regardless of how hard you hit the key.

* A#-1: Soft — The volume responds easily to a light touch; good for players with a lighter strike.

* B-1: Medium — This is the standard "normal" setting.

* C0: Hard — Requires a very heavy strike to reach maximum volume; provides the widest expressive range for experienced players.


Troubleshooting the Dynamic Range

* Voice Limitations: If you are using the Harpsichord or Pipe Organ voices, the P-60 intentionally disables velocity to match the mechanics of the real instruments.

* MIDI/VST Use: Since you mentioned piano VSTs in the past, ensure your MIDI velocity curve in your DAW isn't accidentally set to a "flat" or "fixed" profile.

* Reset: If the key combinations don't seem to take, you can perform a factory reset by holding down the rightmost white key (C7) while turning the power on.


Does switching to the Medium or Hard key setting bring the dynamics back?

---

## User

There is no grand piano button. Demo and voice are the only buttons

---

## Gemini

Since the Yamaha P-60 lacks a dedicated "Grand Piano" button, it uses the [SETTING/VOICE] button (the one next to the Demo button) to access these secondary functions.


How to Toggle Touch Sensitivity

* Hold down the [SETTING/VOICE] button.

* While holding it, press one of the following lowest keys on the keyboard:

* Lowest A (A-1): Fixed (Velocity is off).

* Lowest A# (A#-1): Soft.

* Lowest B (B-1): Medium (Default).

* Lowest C (C0): Hard.





Why it feels "flat"

* Voice Choice: If you have selected the Harpsichord or Church Organ, the keyboard automatically disables velocity to simulate how those instruments actually work.

* MIDI setup: If you are using this as a controller for your macOS setup or piano VSTs, check that your software isn't overriding the velocity curve.


If the keys don't respond to these changes, you can try a factory reset by holding the highest white key (C7) while turning the power on.

---

