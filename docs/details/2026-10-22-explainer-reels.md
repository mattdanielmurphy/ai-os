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
