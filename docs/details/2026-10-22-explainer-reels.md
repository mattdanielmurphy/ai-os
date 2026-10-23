# Explainer reels (2026-10-22)

## 21:20 Pitch

What Matt asked (via the coordinator): an idea, explore and pitch, don't build. Claude turns a long update
into a short animated slideshow with a good voiceover and diagrams, reusable for learning (e.g. studying)
and for presenting anything. Graphics made in Figma. The Figma connector failed in a recent session.

---

### Sketch it first

This is open UX (how a reel should feel: pace, voice, how much text on screen, can you interrupt it).
Per the think-alone-first rule: Matt sketches how he'd want it to feel before reading the rest, so his
picture isn't anchored to mine. Questions worth sketching against: how long is a good reel (30s? 2 min?),
does it play on its own or does he tap through, does he want to ask a question mid-reel, phone or Mac.

---

### Figma connector works now

Checked tonight: the Figma connector answered `whoami` as Matt, on a **Starter** team plan (admin, full seat).
Risk: Figma limits MCP tool calls hard on Starter plans (reported as a handful per month; I have not
verified the current number). One reel needs many calls (build frames, fill text, export). So Figma may
be fine for designing the *template* once, but not for every reel. Verify the limit before building.
The connector also has `export_video` (renders an animated Figma frame to MP4 server side), which is the
nicest path if the limit allows.

---

### How it would work

1. **Script**: Claude cuts the update into 5–8 beats. Each beat = one spoken line (~15 words) + one visual
   (a diagram, a big number, a before/after, a 3-word headline).
2. **Graphics**: a Figma template file Matt (or Claude, once) designs: a handful of beat layouts (headline,
   diagram, compare, list, number). Claude fills slots per reel rather than designing from scratch, so every
   reel looks like the suite and colours come from the shared palette.
3. **Voice**: one audio clip per beat; beat length = clip length, so visuals stay in sync automatically.
4. **Playback**: an Artifact player page (works on phone): auto-plays, tap to pause, ← replays a beat,
   captions on. MP4 export (ffmpeg, already installed) for sharing/presenting.
5. **Triggers**: "make a reel of this" in any thread; later automatic for long replies (rule: proactive
   over skills).

---

### Graphics fallback

If Figma's limits bite: build the same templates as HTML and render with HyperFrames (HTML → MP4; skill
already installed) or Manim (good for maths/logic diagrams, e.g. PHIL 120). Figma stays the design
source; HTML is the renderer. Rejected as the default only because Matt asked for Figma.

---

### Voice options

No TTS key is set in ai-os `.env` today. Options: [ElevenLabs](https://elevenlabs.io) (best, natural,
paid), [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) (good, cheap), Gemini TTS
(good, cheap), macOS `say` premium voices (free, flatter). Recommend ElevenLabs for quality. Matt adds the
key; agents never read it.

---

### Existing tools checked

[NotebookLM](https://notebooklm.google.com) "Video Overviews" already turns sources into a narrated slide
video. Free, decent, but Google's look, no Figma, no control over beats, not automatable from threads.
Worth trying once as a feel reference. Gamma/Synthesia: presentation/avatar tools, wrong shape.

---

### Just for Matt or for the world

For the world, potentially: "turn any long AI answer into a 60-second explainer" is a product. Start just
for Matt; keep it self-contained so it can grow.

Untested: everything; nothing built. Undo: remove the IDEAS.md entry.

## 21:45 Read Aloud as the narrator

What Matt asked: instead of a paid voice key, spawn a chat with the cheapest Claude model, prompt
"repeat this back verbatim: <text>", press Read Aloud, and stream/record the audio, maybe on the VPS.
Pitch only, no build.

---

### Terms of service risk

Anthropic's consumer terms forbid accessing the Services "through automated or non-human means, whether
through a bot, script, or otherwise", except via an API key. Driving claude.ai with a script (on the VPS
or the Mac) to press Read Aloud and capture audio is exactly that. The risk is his **main** Claude account
(the one all his threads, projects and connectors run on) getting flagged or suspended. That outweighs a
few cents of TTS per reel. Not a lawyer's read; this is the plain wording of the consumer terms.

---

### Feasibility if ignored

Technically doable: a headless browser logged in as Matt, send the message, click Read aloud, capture the
audio network response (or record the tab's audio). Problems: needs his claude.ai session cookie on the
VPS (a credential sitting on a server), every reel costs a chat message from his plan's usage, the UI and
endpoint change without notice so it breaks silently, and "verbatim" isn't guaranteed (the model may tweak
wording, so captions drift from audio). Read Aloud has no API and no auto-read setting (checked
2026-10-17).

---

### Free voice instead

[Kokoro](https://huggingface.co/hexgrad/Kokoro-82M): open-source TTS, near-ElevenLabs quality on short
narration, runs locally on his Mac (Apple Silicon, faster than real time), free, no account, no ToS risk,
and could also run on the VPS. Recommended default. Paid fallback when he wants the best voice:
[ElevenLabs](https://elevenlabs.io). Cost check for scale: OpenAI TTS is about $15 per million characters,
so a 2-minute reel (~2,000 characters) is about 3 cents.

Not tested: Kokoro install and voice quality on his Mac. Undo: nothing built.

## 21:50 Voice: Deepgram

Matt: Kokoro sounds incredible for 82M params but isn't quite there; he has lots of Deepgram credits.
Decision: Deepgram's TTS (Aura) is the reel voice. Kokoro stays the free offline fallback (yes, it runs
fine on a Mac or phone CPU, faster than real time).

---

### Voice picker exists

`tools/voice-agent-tester` already lists Deepgram's 138-voice catalog with starred favourites, so the reel
voice can be one he stars there. The tester's key wasn't found by `aios-env list` in that folder; where it
lives is unchecked (not hunted, to avoid reading secret files). Untested: Aura voice quality for narration.

## 22:05 First reel built

Matt 👍'd "build a first reel" and asked for Deepgram's best voices, British/Australian/UK feminine
options, Maeve first.

---

### Voices found

Deepgram's newest voices are Flux TTS (`flux-<name>-en`, `POST /v2/speak`). Non-American feminine ones:
Maeve (Irish: upbeat, confident, gentle), Gemma (British: warm, cheerful, featured), Sharon (Australian:
calm, relaxed). Meena and Priya are Indian. Older Aura-2 also has Pandora (British) and Theia
(Australian); not sampled. Samples: `services/reels/samples/`. Matt added `DEEPGRAM_API_KEY` to ai-os
`.env` (I opened it in VS Code with clearance; never read it). The voice tester keeps its key in browser
storage, which is why it couldn't be reused.

---

### How the reel works

- **Slides**: built with the Figma connector in a new file "Explainer reels"
  (https://www.figma.com/design/xg900viuh141OazDkdNbWF), five 1280×720 frames, page-kit colours and fonts.
  Layers named a1…aN reveal in order. Exported as SVG with live text (`svgOutlineText: false`), ~1–5 KB each.
- **Light/dark**: `build.py` swaps the kit's light hexes for classes bound to kit CSS variables, so the
  same Figma slides follow the system theme. Checked both modes in the browser.
- **Voice**: one Deepgram clip per beat, cached by voice+text; beat length = clip length, so the
  animation spreads its reveals over the first ~55% of the line (tweakable).
- **Player**: one self-contained Artifact page (327 KB with audio inline). Play overlay (browsers need a
  tap before sound), caption that brightens as words are spoken (estimated by time, not true word
  timing), segment strip to jump, ← → R S F keys with visible hints, speed 0.85–1.5×, full screen for
  presenting, lock-screen next/previous.
- **Tweaks**: `services/reels/tweaks.json`, registered in the Tweaks panel; values apply on rebuild
  (the page is static, so not live).

---

### Figma limits

Starter plan, full seat: Figma's docs list no MCP limit for that seat, and writes are exempt anyway.
This reel used ~6 connector calls. Not a blocker so far.

---

### Tested and untested

Tested in the built-in browser: auto-advance across all 5 beats, staggered reveals, captions, end of
reel resets to Play, dark mode. Untested: actual sound (the browser pane can't be heard by me), the
page on his iPhone, full screen on iPhone (Safari only allows video full screen, so ⛶ may do nothing
there). Rejected: MP4 export for now (the page is enough to watch; ffmpeg export is a later add).
Undo: delete the artifact and `services/reels/`.

## 22:45 One-take voice

Matt: the voice made small mistakes ("read" said as "red") and sounded like glued fragments; each call
also winds down (softer, less energy) at its end, so per-slide calls make the whole reel sound tired.
He suggested one long call with long pauses, split by silence. He also wanted the script on his
clipboard to test voices, and dropped a clipboard-manager idea.

---

### One take, cut by words

Tried his pause idea first: ellipses (on their own lines, or inline runs) do **not** make Flux pause
noticeably longer than a normal sentence break (gaps 0.4–1.3 s either way), so splitting by silence alone
would cut mid-beat. Instead: one TTS call for the whole script (paragraphs joined by blank lines), then
Deepgram speech-to-text gives every word's timing, the script is aligned to it (difflib), and each cut
sits halfway between the last word of one beat and the first of the next. Checked by transcribing every
clip: each holds exactly its beat's line. Cost: one extra STT call per reel (cheap).
Also reworded "and I read them to you" to "and I'll read them out to you", which can't be misread.

---

### Script on clipboard

Copied the five lines (blank line between) with clearance from the take-control queue.

---

### Clipboard manager idea

Filed in IDEAS.md and passed to the coordinator for its own thread; out of this thread's scope.

Untested: how the one-take version sounds to a human ear. Undo: previous audio is in
~/.Trash/reel-old-audio; artifact version 1 still exists in its history.
