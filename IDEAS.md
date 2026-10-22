# Ideas

Small ideas Matt thinks would be cool. Big-picture direction goes in VISION.md.

## Summon anything in a given state (2026-10-21)
Whenever an agent builds something visible (HUD, overlay, menu, banner, mixer feature), Matt gets a button
to summon it in a particular state, the same way agents do when they test it. Precedent:
`hammerspoon://claude-control-demo?tier=light|full` previews the take-control banner.
Proposed shape: one `hammerspoon://demo?id=<thing>&state=<state>` route backed by a small registry,
listed in a "Demos" submenu of the ⚙︎ AI-OS menu; Swift apps take `--demo <state>`. Status: proposed, awaiting Matt's OK.
