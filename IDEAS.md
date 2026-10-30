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
voiceover per beat (Deepgram Aura TTS on Matt's existing credits; Kokoro free fallback; Read Aloud automation rejected: ToS risk) → plays as an Artifact player page (pause, replay a beat, captions), MP4 export to share.
Full pitch: docs/details/2026-10-22-explainer-reels.md. Status: first reel BUILT 2026-10-22 (Matt 👍): `services/reels/`, voice Maeve; next: automatic reels for long replies.

## Clipboard manager with agent integration (2026-10-22) — IDEA, NOT STARTED
Matt (Explainer reels thread): his clipboard manager gets "a really sick integration with agents".
1. A subtle animation whenever something lands on the clipboard.
2. Every item shows its source: the app, and whether Matt copied it, an agent copied it on his behalf, or
   something else did; a click opens the source thread an agent copy came from.
3. Delete, pin and edit clipboard items.
Related: `~/.hammerspoon/modules/clipboard.lua` (duplicate-line cleaner); agents already take the
claude-control queue before clipboard writes, which is a natural place to record "agent copied, from
thread X". Status: idea; build on Matt's 👍 (needs its own thread).

## Claude-made generative ambient music (2026-10-22) — IDEA, NOT STARTED
Matt (Explainer reels thread): ambient background music for reels, and in general, made by Claude
driving real instruments, not "AI music": e.g. Arturia Augmented GRAND PIANO, or generative patches in
Cardinal (he has it instead of VCV Rack) with a good creative control scheme. Wants the lightest way on
his Mac: a minimal Ableton set (his default set idles at ~2.1 GB; the big one is only for Launchkey
jams), or a headless/scriptable host (Reaper? Cardinal?). Separate project that reels will use.
Ties into Slub (company with his brother, audio software). Status: idea; needs its own thread.

## Reels: fresh generated music every reel (Matt, 2026-10-23) — IDEA
Matt: "I want to have different music every time, always generated." Each reel gets its own newly made
ambient bed (from the claude-ambient project) instead of a reused loop. Not built yet.

## Reels: leaner slide authoring (Matt, 2026-10-23) — IDEA
Overhead today is mostly the slides (~15 KB of hand-written SVG ≈ 4–5k output tokens per reel vs ~300
for a text reply). Streamline: a shared slide kit of layouts (title+points, queue/flow, stat row,
compare, timeline) so an agent writes a short JSON spec per beat and the kit draws it (~1k tokens).

## Slub Utils: onboarding picker, gradual rollout (2026-10-24)
Idea, not a build request. First run shows a picker of utilities with a sensible default selection already ticked.
A gentle caution says not to enable too much at once. New utilities are then introduced gradually later, not all on day one.
Goal: power users, or people who installed for one specific utility, can enable anything on day one. But changing too much about how the Mac behaves at once is confusing, so the app recommends starting with a couple and introduces more once they are used to those.
Matt note: the auto-delineator text-selection wrapper is the only one he can think of that might confuse people, though what it does should be apparent immediately.
Questions still unanswered:
- Which utilities make up the default selection?
- How are new utilities introduced later: a quiet "new" badge, or a prompt?
- Should the auto-delineator be left out of the default selection, given it is the likeliest to confuse?
Status: idea; build on Matt 👍.

## Slub Utils: command palette with inline shortcut setting (2026-10-24)
Idea, not a build request. Inspired by the command palette in Rex (terminal app): set or change an action's keyboard shortcut right inside the palette, via a clickable icon on the row.
Matt likes the whole implementation, and that it does not open with a wall of obscure commands the way VS Code sometimes does.
Shape: opens short and curated (useful actions only), search reveals the rest; each row shows its shortcut and an icon to rebind it in place.
Status: idea; build on Matt 👍.

## Robust minimal component library (Matt, 2026-10-24) — IDEA

- **A small, minimalist component library** that's easy to get right and super robust, with clever guards built in (first one: no orphans).
- **Orphans:** shrinking text to fit was rejected (several headings at different sizes look bad). Cheap layers first: `text-wrap: balance`/`pretty` and binding the last two words; then a script that detects leftover orphans (`ui-mixer/orphans.cjs`) and asks a cheap model to rephrase just that line so it fits, like hand-tuned man pages.
- Matt: "It could be extremely cheap in theory, so why not?"

## Slub: live walking-tour app (Matt, 2026-10-25) — IDEA, Tyler might like this

Matt's words: "An app that gives you live dynamic walking tours of wherever you are. Uses location tracking and acceleration to know exactly where you are, to give you directions (if you want! Could also just be: as I'm walking here point out stuff that's cool and tell me about it) and show you cool shit about the place you're in.

You could ask an AI clarifying questions, or say: I don't care about that stuff, talk more about XYZ. Or like, 'can we check out the colosseum?' And then it changes the tour right there and heads for the colosseum."

Tags: Slub, Tyler-might-like, mobile, location, AI.
Status: idea; build on Matt 👍.

### Walking-tour app: follow-up notes (Matt, 2026-10-25)
- **You lead, it follows.** Pre-recorded tours make someone else the leader. Here you explore on your own and find things nobody has seen.
- **Fully context-aware.** Say "heading into this coffee shop" and it goes quiet until you step out and say "continue the tour".
- **Make it really, really nice to use.** Smart about when to speak and when to shut up.
- **Camera as a second sense.** Phone sits in your shirt pocket with the camera peeking out (like in *Her*). Every so often it captures the scene and tells you cool things it sees, especially off the beaten path.

## Life OS: organize everything with an overseer + specialists (Matt, 2026-10-25) — IDEA, discussing
- Matt: "I know that things are going to get missed because there's just too much. And there's not one centralized place."
- One "everything" project he talks to; one overseer agent for his life at a broad level; specialist agents per area (too much for one agent's context).
- Areas he named: school; Slub / software dev; money (budget with all non-negotiable monthly expenses; worried he'll run out); health (physical, mental); part-time job (own category; he thinks working part-time would help a lot, money included); personal notes + old projects on his Mac (biggest cleanup); Mac inventory (every file/folder/app/tool that differs from a stock Mac, documented, so a breakage has a place to start).
- Guardrails: resist building more global Mac tools or a custom AI harness ("Claude is good enough"); discipline on testing and buttoning up tools, since with ~10+ custom tools he can't tell which one broke.
- CEO rhythm: he gives instructions at set times, agents work, he checks back at set times on a few things. The current projects view isn't clicking.
- Things get lost from past Claude threads, even this week's.
- Discussion thread: "Getting life organized" (2026-10-25). Build nothing until he 👍s.

## Programmable smartwatch (Matt, 2026-10-23) — IDEA
- Wants total control over a watch: own "Hey Claude", now-playing controls that show at once for phone *and* Mac music, one-tap favourite (Apple buries it in a submenu).
- Options voice Claude named: Bangle.js (JS), PineTime (open source), LilyGo T-Watch (mic + Wi-Fi). Apple Watch apps can't have an always-on wake word; Vocal Shortcuts (iOS 18 / Sequoia) isn't on watchOS.
- Source: voice call "Building a custom smartwatch with Claude". Build nothing until he 👍s.

## Calm browser: gradual friction for Instagram/TikTok (Matt, 2026-10-22) — IDEA, product
- Minimal WKWebView browser, pitched as "the calm way to open Instagram": ads hidden day one, mobile web made as good as the app, then friction turned up so slowly you barely notice; a month later you use it a fraction as much.
- No self-imposed limits by default ("install it, use Instagram normally, we'll handle the rest"); settings exist but are framed as "we recommend you never open this".
- Onboarding: delete the Instagram app, or universal links send you back to it. Quiet weekly "20% less" note.
- App Store: disclose it as a digital-wellbeing feature (avoid 2.5.19 bait-and-switch); WebKit satisfies 2.5.6. Safari-extension route rejected (enable flow too clunky for normal people).
- Source: voice call "Browser to curb social media addiction". Build nothing until he 👍s.

## Live call transcript with Claude listening (Matt, 2026-10-23) — IDEA / in progress
- Calls with Tyler: Audio Hijack splits his mic (channel 0 = Matt) and FaceTime output (channel 1 = Tyler) → Deepgram streaming (multichannel, own end-of-speech timing) → an always-current transcript file any model can read; "what do you think, Claude?" sends it. Voice (Deepgram Aura) later.
- A setup task was sent from that call; check its thread before building.

## Tweaks panel: hover a knob to highlight its UI element (Matt, 2026-10-27)
- Hovering a control in the ⌃⌥⌘T Tweaks panel outlines the matching UI element in the app, when there is one.
- Feasibility: doable. Knobs (hud-kit `Tweaks.swift`, `modules/tweaks.lua`) have no link to a UI element yet. Add an optional `target` id per knob, and have the panel send "hover <app> <target>" to the app (a small IPC file or distributed notification). Each app then draws a brief outline on that element; the shared Knobs component would own the outline helper so apps just register targets. Knobs with no visible element (timings, curves) get no highlight.
- Status: idea; parked in Linear. Build nothing until he 👍s.

## Coordinator of coordinators (Matt, 2026-10-28) — BUILDING
- Every project gets its own coordinator session; the pinned central Coordinator is the front desk that forwards project asks via SendMessage and keeps the big picture. Project coordinators own ground-floor detail (worker side threads). Coordinators can tell each other "you deal with this". One shared registry (`coordinator/threads.json`, `coordinator` owner field).
- Honest take: good fit; it keeps the central context light and gives a per-project view in the sidebar. Risks: messages bouncing between coordinators (extra tokens, slower), registry write races, and idle coordinator sessions for quiet projects. Start coordinators only for projects with ongoing work. Instructions: `docs/coordinator/project-coordinator.md`.

## Sing with live auto-tune as pitch feedback (Matt, 2026-10-28)
Practice singing while hearing your own voice auto-tuned, as instant "this is the target pitch" feedback.
**Honest take:** fun and motivating, but hard tuning hides your errors, so you can learn to lean on it. Better as a pitch display or gentle/partial correction you fade out over time. Cheap to try with existing apps.

## Read-aloud: skip forward by sentence or by message (Matt, 2026-10-28, parked)
Buttons to jump ahead a sentence, or to the next queued reply, while Claude reads aloud.
**Honest take:** skipping to the next message is easy and useful (stop the current one, read the next queued one). Skipping by sentence is hard: Claude's Read aloud exposes only play/pause, no position, so it would need our own timing guesses and would often land mid-word. Build "next message" first if wanted; small.

## 2026-10-29 · Rules as context-triggered hooks (Matt)
Idea: most rules should be hooks, not text the agent reads once and tries to remember. Maybe a third layer of agents that watch the workers and inject the right hook at the right moment.
Honest take: the first half is strong. Today's misses (size checks, summaries, lost handoffs) were all "remembered rule" failures. The watcher-agent layer is weak: it's another LLM that can forget, costs tokens on every step, and needs hooks of its own. Better: deterministic triggers. Each rule gets a trigger (tool name, file path, keywords in the prompt or reply), and a hook injects just that rule at that moment, or blocks outright when it's a hard rule. Claude Code PreToolUse/UserPromptSubmit/Stop hooks already support this. The QMD-notes and thread-size hooks are working examples. Size: medium; start by tagging the ~20 most-broken rules with triggers.

## Big prompts go to a sub-coordinator (Matt, 2026-10-29) — built
Hook `scripts/hooks/big_prompt_guard.py`: in the Coordinator only, prompts ≥500 words (≥900 when pace is CAREFUL, off when it says Sonnet) get handed to a fresh Opus medium/low sub-coordinator that returns a thread plan. Honest take: worthwhile; a dedicated context plans long dumps better than a crowded one. Thresholds are guesses; tune after a few weeks of real use. Pace-aware pattern should be reused by other cost-heavy rules.
