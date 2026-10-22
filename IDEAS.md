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
Assessment: docs/details/2026-10-22-capture-audio-buffer.md. Status: idea; awaiting Matt's pick.
