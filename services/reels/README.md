# Explainer reels

Turns a long update into a short narrated, animated slideshow: Figma slides, a Deepgram voice, one
self-contained player page (light/dark, phone-friendly, keyboard hints on screen).

**Just for Matt for now**, built self-contained so it can go public later.

## Make a reel

1. Write `reels/<nnn-slug>/reel.json`: `title`, `eyebrow`, `voice`, `figma`, and 5–8 `beats`
   (`say`: one spoken line, ~15 words; `svg`: that beat's slide).
2. Design the slides in Figma (1280×720 frames, page-kit light colours, fonts Bricolage Grotesque /
   Source Serif 4 / JetBrains Mono). Name layers `a1`, `a2`, … in the order they should appear.
3. Export each frame with the Figma connector:
   `exportAsync({ format: 'SVG_STRING', svgOutlineText: false, svgIdAttribute: true })` → `<n>.svg`.
4. `python3 build.py reels/<nnn-slug>` → `reel.html` (voice lines cached in `audio/`).
5. Publish `reel.html` with the Artifact tool.

First reel's slides: https://www.figma.com/design/xg900viuh141OazDkdNbWF

## Voices

`tts.py <voice> "<text>" out.mp3` uses Deepgram Flux TTS (`flux-<voice>-en`, key `DEEPGRAM_API_KEY`
in ai-os `.env`). Non-American feminine voices: **maeve** (Irish), **gemma** (British), **sharon**
(Australian). Samples in `samples/`.

## Feel knobs

`tweaks.json` (shows in the ⌃⌥⌘T Tweaks panel): reveal spread/gap/duration/rise, beat gap and lead.
Rebuild after changing them.

## Player

Space pause · ←/→ beats · R replay · S speed (1, 1.25, 1.5, 0.85×) · F full screen · tap a segment.
Captions brighten as the line is spoken. Lock-screen next/previous via Media Session.
