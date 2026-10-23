# Explainer reels

Turns a long update into a short narrated, animated slideshow: Figma slides, a Deepgram voice, one
self-contained player page (light/dark, phone-friendly, keyboard hints on screen).

**Just for Matt for now**, built self-contained so it can go public later.

## Make a reel

1. Write `reels/<nnn-slug>/reel.json`: `title`, `eyebrow`, `voice`, `figma`, and 5–8 `beats`
   (`say`: one spoken line, ~15 words; `svg`: that beat's slide).
2. Pick or make a theme in `themes/` (fonts + colour roles, light/dark). Never the stock kit look
   (rule: No Claude-default look); `kit.json` exists only so reel 01 still builds. Design the slides in
   Figma (1280×720) with the theme's LIGHT role hexes and fonts. Name layers `a1`, `a2`, … in reveal order.
3. Export each frame with the Figma connector:
   `exportAsync({ format: 'SVG_STRING', svgOutlineText: false, svgIdAttribute: true })` → `<n>.svg`.
4. `python3 build.py reels/<nnn-slug>` → `reel.html` (voice lines cached in `audio/`).
5. Publish `reel.html` with the Artifact tool.

First reel's slides: https://www.figma.com/design/xg900viuh141OazDkdNbWF

## Reels

- 01 Explainer reels (stock kit look, kept as the before): https://claude.ai/artifact/LSFodxqvScqba6UcY5xUxg
- 02 Your palette is waiting on you (panel theme): https://claude.ai/artifact/2oVcSYhSMspspNPSA3dWQR

## Voices

`tts.py <voice> "<text>" out.mp3` uses Deepgram Flux TTS (`flux-<voice>-en`, key `DEEPGRAM_API_KEY`
in ai-os `.env`). Non-American feminine voices: **maeve** (Irish), **gemma** (British), **sharon**
(Australian). Samples in `samples/`.

## Feel knobs

`tweaks.json` (shows in the ⌃⌥⌘T Tweaks panel): reveal spread/gap/duration/rise, beat gap and lead.
Rebuild after changing them. `voice.pace` (default 1.15) is baked into new takes; the player's
Pace button switches Normal / Quick / Gentle (gentle is for hard or unfamiliar topics).

## Player

Space pause · ←/→ beats · R replay · S pace (Normal / Quick / Gentle) · F full screen · tap a segment.
Captions brighten as the line is spoken. Lock-screen next/previous via Media Session.
