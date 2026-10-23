# Explainer reels

Turns a long update into a short narrated, animated slideshow: Figma slides, a Deepgram voice, one
self-contained player page (light/dark, phone-friendly, keyboard hints on screen).

**Just for Matt for now**, built self-contained so it can go public later.

## Make a reel (agents: this is the default for big replies)

1. Copy `reels/003-air-traffic/` to `reels/<nnn-slug>/`; keep `slides.py`'s helpers (chip, title, para,
   cards…), rewrite the slides. Slides are hand-written SVG (1280×720) using theme role classes
   (`f-ink`, `f-accent`…), never hexes. Groups `a1`, `a2`, … reveal in order; inside them `draw`, `grow`,
   `flow`, `pulse`, `glow`, `spin`, `blink`, `data-count`, `data-type` animate. `python3 slides.py` writes `<n>.svg`.
   (Figma also works: export frames with `exportAsync({format:'SVG_STRING', svgOutlineText:false, svgIdAttribute:true})`.)
2. `reel.json`: `title`, `eyebrow`, `voice` + `voices` (default `pandora`, `gemma`, `maeve`), `theme` (`panel`),
   `music` (a loop path), and 5–8 `beats` (`say`: one spoken line, ~15–30 words; `svg`). The slide shows
   the facts; the voice says them conversationally. Don't repeat the narration as slide text word for word.
3. `python3 build.py reels/<nnn-slug>` (run it backgrounded; first build calls Deepgram once per voice).
4. `./test.sh reels/<nnn-slug>` (backgrounded): headless, muted, checks errors, ducking, flash, fit.
   Never open a reel in the Claude browser pane.
5. Publish `reel.html` with the Artifact tool; reply with the link plus the usual ≤ 50-word summary.

Never the stock kit look (rule: No Claude-default look); `kit.json` exists only so reel 01 still builds.

## Reels

- 01 Explainer reels (stock kit look, kept as the before): https://claude.ai/artifact/LSFodxqvScqba6UcY5xUxg
- 02 Your palette is waiting on you (panel theme): https://claude.ai/artifact/2oVcSYhSMspspNPSA3dWQR
- 03 Air traffic control (animated slides, ducked piano bed): https://claude.ai/artifact/BnqUN9XerZsqF5sepZtdy7

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

## Music bed

`music` in reel.json (a loop path) plays under the voice, side-chain ducked in the player: knobs
`music.level`, `duck.depth/threshold/attack/release`, `music.intro/fadeIn/outro` in tweaks.json.

## Testing (agents)

**Never open a reel in the Claude browser pane**: it hung two sessions for 20+ min (2026-10-23).
Run `./test.sh reels/<nnn-slug>` instead (backgrounded): headless Chrome, `?mute` plus `--mute-audio`,
a hard 2-minute limit, and it prints the mix each second (music gain dips under the voice).
`?mute` matters for any real browser too: hearing the script before it's ready spoils the reel
(Matt, 2026-10-22). Check timing with `audio.currentTime`, not by ear.
