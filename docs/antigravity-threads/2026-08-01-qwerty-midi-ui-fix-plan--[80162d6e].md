---
title: "QWERTY MIDI UI Fix Plan"
date: "2026-08-01"
conversation_id: "80162d6e-05ef-4136-8c07-9c0a3edfd030"
source: "antigravity"
---

# QWERTY MIDI UI Fix Plan

## User

Write an implementation plan to /Users/matt/.gemini/antigravity/brain/8a68576b-bf2e-41c5-bd4e-152ee6473fd0/implementation_plan.md for resolving the QWERTY MIDI UI failure loop.

Contents of plan:
# QWERTY MIDI UI Creation & Reload Loop Fix

Fixing the infinite UI crash/reload loop caused by watch script self-triggering and stale webview watchdog state.

## User Review Required

> [!IMPORTANT]
> The fix requires two key changes:
> 1. Updating `bin/watch_src.sh` to exclude `src/ui_html.lua` from `fswatch` monitoring so bundling does not trigger infinite Hammerspoon reloads.
> 2. Resetting `lastHeartbeat = os.time()`, `evalFailCount = 0`, and guarding JS updates in `src/hud.lua` until `domReady` is received.

## Proposed Changes

### Build Watcher

#### [MODIFY] [bin/watch_src.sh](file:///Users/matt/projects/qwerty-midi-hammerspoon/bin/watch_src.sh)
- Add `--exclude "src/ui_html.lua"` to `fswatch` arguments so that writing the compiled HTML Lua module does not re-trigger the watch script and reload Hammerspoon.

### Webview HUD Lifecycle

#### [MODIFY] [src/hud.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/src/hud.lua)
- Reset `lastHeartbeat = os.time()` and `evalFailCount = 0` at the start of `createMidiWebview()`.
- Add a `domIsReady` flag in `createMidiWebview()` set to `true` when `body.type == "domReady"` is received.
- In `safeEvaluateJS` / `performWebviewHudUpdate`, check `domIsReady` before running `evaluateJavaScript` to prevent false positive JS evaluation errors.

### Monolithic Bundle

#### [MODIFY] [qwerty_midi.lua](file:///Users/matt/projects/qwerty-midi-hammerspoon/qwerty_midi.lua)
- Run `bin/bundle_and_reload.sh` after updating `src/` to compile the single-file distribution bundle.

## Verification Plan

### Automated Tests
- Syntax check modified Lua files using `luac -p src/hud.lua src/init.lua`.

### Manual Verification
- Execute `bin/bundle_and_reload.sh`.
- Inspect `/tmp/midi_startup.log` to confirm no recurring `Start init.lua` or `Watchdog detected dead webview` logs.
- Verify HUD webview opens cleanly and stays persistent.

---

## Assistant

Created At: 2026-07-31T22:07:46-06:00
Completed At: 2026-07-31T22:07:46-06:00
Created file file:///Users/matt/.gemini/antigravity/brain/80162d6e-05ef-4136-8c07-9c0a3edfd030/implementation_plan.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
Note: You have just created an artifact and requested user feedback. Stop calling tools to end your turn, and allow the user to review the artifact, approve it, or provide feedback

Created At: 2026-07-31T22:07:47-06:00
Completed At: 2026-07-31T22:07:47-06:00
Message sent to "8a68576b-bf2e-41c5-bd4e-152ee6473fd0".

The implementation plan for fixing the QWERTY MIDI UI creation and reload loop has been created. I have notified the parent agent.

---
