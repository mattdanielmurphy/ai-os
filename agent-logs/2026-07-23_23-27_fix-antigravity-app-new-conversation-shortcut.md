## Goal
Update `launch_antigravity_app` in `triage_router.py` to use `Shift + Cmd + O` twice to trigger a new unattached global conversation in `/Applications/Antigravity.app`.

## User Feedback & Decisions
- The shortcut to create a new unattached conversation in `Antigravity.app` is `Shift + Cmd + O` pressed twice.

## Changes Made
- Updated AppleScript sequence in `launch_antigravity_app`:
  - Activates `/Applications/Antigravity.app`.
  - Sends `Shift + Cmd + O`, delays 0.2s, sends `Shift + Cmd + O` again.
  - Sends `Cmd + V` (paste prompt from system clipboard).
  - Sends `Return` (key code 36) to submit.

## What Worked
- Tested keystroke automation via AppleScript on `/Applications/Antigravity.app`.
- `test_triage.py` unit checks passed.
