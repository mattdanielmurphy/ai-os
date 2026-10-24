# Explainer reels

Turns a long update into a short narrated, animated slideshow: Figma slides, a Speechify voice, one
self-contained player page (light/dark, phone-friendly, keyboard hints on screen).

**Just for Matt for now**, built self-contained so it can go public later.

## Make a reel (agents: this is the default for big replies)

**New reels use the page player** (the page is the slide; Matt picked the look in the UI Mixer, 2026-10-23).
Each beat in `reel.json` gets a `slide` object instead of an SVG; the player lays it out for desktop and phone.
Look: `look.json` (a reel may override keys under `"look"`). Layouts (`layout`):

- `cover`: `label`, `title`, `lede`, `total` (one line or a list)
- `bars`: `rows` [{`label`, `value` (number), `amount`, `note`}], `total`
- `compare`: `cards` [{`key`, `head`, `lines` [[a, b]], `total`, `once`, `tone`: good|bad}], `small`
- `list`: `lede`, `items` [{`head`, `sub`, `tone`}], `tone` (good|bad for all), `total` / `small`
- `checks`: `items` [text], `total`
- `svg`: `svg` (a file in the reel folder, e.g. a custom asset exported from Figma) plus `label` / `title`

Every layout takes `label`, `title`, `total` and `small`; wrap words in `*stars*` for the key-number highlight.
Parts appear one by one as the narration reaches them. Content that won't fit shrinks to fit. See reel 04.

Older reels (01–03) keep the SVG player (`template.html`); the steps below still describe it.

1. Copy `reels/003-air-traffic/` to `reels/<nnn-slug>/`; keep `slides.py`'s helpers (chip, title, para,
   cards…), rewrite the slides. Slides are hand-written SVG (1280×720) using theme role classes
   (`f-ink`, `f-accent`…), never hexes. Groups `a1`, `a2`, … reveal in order; inside them `draw`, `grow`,
   `flow`, `pulse`, `glow`, `spin`, `blink`, `data-count`, `data-type` animate. `python3 slides.py` writes `<n>.svg`.
   (Figma also works: export frames with `exportAsync({format:'SVG_STRING', svgOutlineText:false, svgIdAttribute:true})`.)
2. `reel.json`: `title`, `eyebrow`, `voice` + `voices` (default `pandora`, `gemma`, `maeve`), `theme` (`panel`),
   `music` (a loop path), and 5–8 `beats` (`say`: one spoken line, ~15–30 words; `svg`). The slide shows
   the facts; the voice says them conversationally. Don't repeat the narration as slide text word for word.
3. `python3 build.py reels/<nnn-slug>` (run it backgrounded; first build calls Speechify once per voice).
4. `./test.sh reels/<nnn-slug>` (backgrounded): headless, muted, checks errors, ducking, flash, fit.
   Never open a reel in the Claude browser pane.
5. Publish it as a page: `pages new <name> --from reel.html` (or copy over `~/projects/pages/site/<name>/index.html` on a rebuild), then `pages deploy`; reply with the public link plus the usual ≤ 50-word summary.

Never the stock kit look (rule: No Claude-default look); `kit.json` exists only so reel 01 still builds.

## Reels

- 01 Explainer reels (stock kit look, kept as the before): https://claude.ai/artifact/LSFodxqvScqba6UcY5xUxg
- 02 Your palette is waiting on you (panel theme): https://claude.ai/artifact/2oVcSYhSMspspNPSA3dWQR
- 03 Air traffic control (animated slides, ducked piano bed): https://claude.ai/artifact/BnqUN9XerZsqF5sepZtdy7

## Cloud sessions

Cloud sessions build reels too. The Speechify key never enters the VM: the cloud environment holds it as a
**network secret** (claude.ai/code → edit environment → Network secrets → Add secret: host
`api.speechify.ai`, header `Authorization`, prefix `Bearer`, value = the key), and Anthropic's proxy attaches
it. `tts.py` sends no key when `CLAUDE_CODE_REMOTE=true` and none is set. No system ffmpeg there:
`build.py` pip-installs `imageio-ffmpeg`. Missing music loop → `music/default.m4a`. `test.sh` installs
playwright-core with npm (bun can't fetch through the cloud proxy) and uses Playwright's Chromium.
Then publish it with `pages` as usual (on Matt's Mac; a cloud session without his Mac publishes with the Artifact tool).

## Voices

`tts.py <voice> "text" out.mp3 [speed]` uses Speechify (key `SPEECHIFY_API_KEY` in ai-os `.env`). Every
Speechify setting is a `voice.*` knob in Tweaks: rate, pitch, volume, voice id, model, loudness/text
normalization, the two pause lengths, audio format. The API returns word timings (used to cut beats and to
time the subtitles). Pauses are SSML `<break>`s.
**Speechify reads prosody percentages as a change**: `rate="100%"` doubles the speed, so rate is always sent
signed (`+10%`, `-5%`). Before 2026-10-24 reels sent `rate="115%"` (2.15× speed); `voice.rate` 1 = natural.
Old Deepgram samples in `samples/` are history.

## Feel knobs

`tweaks.json` (the ⌃⌥⌘T Tweaks panel, app "Explainer reels"; pin it there while the browser has focus):
timings, layout and subtitle knobs, bars, controls, music, and every Speechify setting.

- **Live:** open the reel's page on pages.test (e.g. http://pages.test/tv-box/). It polls
  `/__pages/tweaks` and redraws within half a second of a change. Rate and volume preview live against
  the recorded take; pitch, voice, model, normalization and pauses are heard after Apply.
- **Apply:** makes the values the defaults (commits tweaks.json), then `apply.sh` rebuilds every reel whose
  reel.json names a `page` (re-recording the voice if a voice knob changed), copies it to that page,
  republishes its mattmurphy.ca copy and deploys.
- The player's Pace button still switches Normal / Quick / Gentle on top.

## Player

Space pause (really pauses: nothing more appears until Play) · ←/→ beats · R replay · S pace (Normal / Quick / Gentle) · F full screen · tap a segment.
Subtitles show the sentence being spoken (`subtitle.mode`), words brightening on Speechify's timings. Lock-screen next/previous via Media Session.

## Music bed

`music` in reel.json (a loop path) plays under the voice, side-chain ducked in the player: knobs
`music.level`, `duck.depth/threshold/attack/release`, `music.intro/fadeIn/outro` in tweaks.json.

## Testing (agents)

**Never open a reel in the Claude browser pane**: it hung two sessions for 20+ min (2026-10-23).
Run `./test.sh reels/<nnn-slug>` instead (backgrounded): headless Chrome, `?mute` plus `--mute-audio`,
a hard 2-minute limit, and it prints the mix each second (music gain dips under the voice).
`?mute` matters for any real browser too: hearing the script before it's ready spoils the reel
(Matt, 2026-10-22). Check timing with `audio.currentTime`, not by ear.
