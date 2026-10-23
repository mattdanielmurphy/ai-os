# Ideas

Small ideas Matt thinks would be cool. Big-picture direction goes in VISION.md.

## Summon anything in a given state (2026-10-21)
Whenever an agent builds something visible (HUD, overlay, menu, banner, mixer feature), Matt gets a button
to summon it in a particular state, the same way agents do when they test it. Precedent:
`hammerspoon://claude-control-demo?tier=light|full` previews the take-control banner.
Proposed shape: one `hammerspoon://demo?id=<thing>&state=<state>` route backed by a small registry,
listed in a "Demos" submenu of the ⚙︎ AI-OS menu; Swift apps take `--demo <state>`. Status: proposed, awaiting Matt's OK.

- **Action buttons/links in chat (2026-10-21)**: custom clickable links or buttons in project threads, wired to commands on the Mac (e.g. "summon this HUD in state X"), so Matt can trigger things the way agents do when testing. Could unlock a lot of modding of the project page. First try: `hammerspoon://` links in a thread reply weren't clickable.

## Right-click an app → its Claude threads (2026-10-22)
Matt "really likes" this. Right-click one of his own apps (HUD, menu bar app, web app) and see the recent
Claude threads about that app, each with its state: resolved, idle, waiting for his input, cache expired.
Clicking a thread opens it. A "prod" switch hides the whole menu. Should be a shared module (next to
hud-kit) every app imports, not per-app code. Designs: docs/details/2026-10-22-app-thread-menu.md.
Status: idea; build on Matt's 👍.

## Earn Claude with a habit step (2026-10-22)
Matt: "a very powerful tool we can use is rewards. I'm addicted to Claude", so having to finish a step first is "a fantastic incentive".
Gate Claude use behind finishing today's habit step (first likely use: the afternoon logic study block).
Builds on the check-in habit ladder (`services/checkin/ladder.py`), so it stays gentle: tiny doses,
grow slowly, pull back after misses, and an escape hatch that just counts as a miss.
Refinement (Matt, 15:25): don't ask; the gate just hands him an artifact with the logic questions to do.
Options: docs/details/2026-10-22-claude-habit-gate.md. Status: idea; build on Matt's 👍.

## Capture Audio: rolling buffer of system audio (2026-10-22)
Like Ableton's Capture MIDI, but for audio: always keep the last few minutes of everything the Mac plays,
except Apple Music. After audio plays, a small HUD button appears (own slot in `~/.hammerspoon/hud_slots.json`);
clicking it opens a picker to grab a clip from the buffer. Existing-tool route first: Audio Hijack 4.5.5
(installed) can do System Audio "all except Music" + Time Shift/Recorder. Custom route: macOS 14.2+ Core Audio
process tap excluding Music.app, in-memory ring buffer, HUD + waveform picker.
Assessment: docs/details/2026-10-22-capture-audio-buffer.md. Status: on hold (Matt, 2026-10-22): custom build later, as part of his Utilities app.

## Wake-up call from an agent, in character (2026-10-22)
Matt: "having an agent CALL and speak to you seems like one of the greatest ways to get up ... Once you speak for 5s,
you're up." Do the talk half of the morning check-in as a real phone call. Each morning Sonnet invents a legitimately
funny original character (name, job, running gag), picks a matching voice, and calls; missed call → an in-character
voicemail, and the iMessage with the page link names who called, so he goes "aw, I missed the butler". Real
celebrity voices (Snoop Dogg) are out: cloning a voice you don't own breaks ElevenLabs/Deepgram ToS and personality
rights, so original characters only. Stack: his own `tools/voice-agent-tester` (Deepgram Voice Agent, 4 personas
already) + Twilio for the phone leg + Sonnet via the Max plan's monthly API credit; ~$0.40 per 5-min call.
Plan: docs/details/2026-10-22-agent-wake-up-call.md. Status: idea; build step 1 on Matt's 👍.

## Shortcut registry: air traffic control for hotkeys (2026-10-22)
One global registry of keyboard shortcuts so Matt's apps (Hammerspoon modules, trackpad-mixer, lidstay,
launcher, etc.) never grab the same combo. Same idea as `hud_slots.json` for screen space: a shared JSON
(e.g. `~/.hammerspoon/hotkeys.json`) each app reads to claim its keys, plus a test that fails on any clash.
Should be a shared module every app imports. Status: idea; build on Matt's 👍.

## Live-tweak layer for every app (2026-10-22)
Every app agents build exposes its feel knobs (fade curves, timings, sizes, colours) in one
`tweaks.json`, hot-reloaded with no side effects, so Matt turns knobs without reading code.
Status: built 2026-10-22 (hud-kit Tweaks.swift, Hammerspoon modules/tweaks.lua, ⌃⌥⌘T panel). Details:
docs/details/2026-10-22-live-tweak-config.md

## Blind two drafts (2026-10-21)
Keep Matt's design ideas un-anchored while still working with Claude: Matt jots his own rough take first
into a sealed file; a separate Claude session drafts its own from a one-line problem statement without
opening it; then both go side by side and get merged. Competitor research comes last, only as a
"did we miss anything?" check. Born in the Claude vision HUD thread, split out 2026-10-22.
Details: docs/details/2026-10-22-blind-two-drafts.md. Status: now a standing rule (core_safety 1j): agents suggest it on open design tasks; no skill.

## Cool GIFs, not Facebook GIFs (2026-10-22) — BUILT
Matt wants a GIF picker that serves funny/weird/cool GIFs instead of the bland mom-on-Facebook ones
Giphy/Tenor push. Existing tool first: [Raycast GIF Search](https://www.raycast.com/josephschmitt/gif-search)
(Giphy, Klipy, The Finer Gifs Club, favourites). Small build option: a Raycast/Hammerspoon picker that
pulls top posts from r/HighQualityGifs, r/reactiongifs and Finer Gifs Club plus his own starred stash.
Options: docs/details/2026-10-22-cool-gif-sources.md. Status: built 2026-10-22 as a suite utility
(Matt: no Raycast extension), `~/.hammerspoon/modules/gif_picker.lua`, ⌃⌥⌘G.
Next idea (Matt, 2026-10-22): audience "Areas". The GIF you'd send a good buddy differs from one you'd send
your mom, so separate areas (e.g. Buddies, Family, Work) each with their own sources and vibe, and stars filed
per area. Status: idea; build on Matt's 👍.

## Anti-sycophancy AI therapist harness (2026-10-22) — DECIDED, NOT STARTED
From a voice call: Matt uses Claude as a pseudo-therapist (no filter with it, maybe better than a therapist
he could get) but wants a harness that fights sycophancy. Pieces he named: multiple passes, possibly across
different models; invert his argument and combine both answers; a blind judge that only sees the reply
abstracted to agree/disagree symbols; and a reliable sycophancy test set. Open question he raised: does a
top model beat a lesser one for therapy-style talk? A handoff doc was written during the voice call.
Source: vault `Voice calls/2026-10-22 2016 Pickleball partner, anti-sycophancy harness idea.md`.
Status: filed only; build on Matt's 👍.

## Explainer reels: long update → short animated narrated slideshow (2026-10-22) — PITCHED, NOT STARTED
Matt (via coordinator): Claude turns a long update into a short animated slideshow with a good voiceover
and diagrams; reusable for learning and for presenting anything. Graphics made in Figma.
Pitch: Claude writes 5–8 beats (one narration line + one visual each) → fills a Figma template file →
voiceover per beat → plays as an Artifact player page (pause, replay a beat, captions), MP4 export to share.
Full pitch: docs/details/2026-10-22-explainer-reels.md. Status: pitched; build on Matt's 👍.
