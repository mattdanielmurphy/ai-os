# Handoff: read-aloud mod + action bar (2026-10-28)

Earlier thread: local_53e8f57e-cb3b-4929-9877-d88fd0d46250 ("Mod: read the coordinator's replies aloud"), started by the Coordinator (local_cc656186-…).

## What exists
- **read-aloud mod** (`mods/read-aloud`, v0.3.0): on in the Coordinator (id in `coordinator/session.txt`), toggled with /read-aloud; band shows on/off and "Dictate after" (/dictate-after). On a finished main-thread reply (`reason === 'answer'` only, so stopped turns read nothing) it calls `hs -c 'require("modules.claude_read_aloud").replyDone()'`; typing or sending calls `cancel()`. Stays silent during a live call (uses `scripts/hooks/live_call.py`).
- **Hammerspoon `modules/claude_read_aloud.lua`**: presses Claude's OWN "Read aloud" AXButton (never the macOS voice; Matt banned it twice). Only fires when the "Coordinator" heading is on screen and Claude is frontmost; otherwise it plays a soft sound and waits for the app to come forward. Checks every 0.15 s (press lands ~0.4 s after the reply). When reading ends it starts TypeWhisper dictation (`scripts/dictate.sh start`) under `claudeControl.withInput`. Knobs: `~/.hammerspoon/tweaks/claude_read_aloud.json`. Debug: `M.status()`; logs print `claude_read_aloud:` to the console.
- **action-bar mod** (v0.3.0): hides the `Actions:` line from the drawn reply; " | " marks either/or (no "All of these"; pairs never get it); one pill style; no gap when alone.
- **live_call hook**: a call counts as live only if its transcript changed in the last 10 min; installed copies in `~/.local/share/call-transcript/` are symlinks to ai-os `scripts/`.
- **call-transcript**: stops itself after 15 min of silence; no-arg run prints usage. Oct 27 gap 15:04–15:43 recovered from the Audio Hijack mp3 (linear time fit) into the transcript, Obsidian and slub-hq.

## Open / untested
- Dictation after read-aloud hasn't been confirmed on a real reply. Its draft-in-prompt skip was removed as the likely cause; check the console logs the next time Matt says it fails.
- Unknown whether Claude's Read aloud reads the hidden Actions line (it may read the stored text).
- Band spacing hasn't been looked at on screen, in light or dark mode.
- Refused: a "go-queue" mod that submits messages as Matt to get around the app's rule that only he can start sessions.

## Keep in mind
- After a mod edit: bump the version, run `plugin marketplace update ai-os-mods` + `plugin update <mod>@ai-os-mods` (the app's bundled claude binary), then restart the app.
- Never the system voice; take claude-control clearance for any test that presses or plays something.
