## Goal
Fix the `rules-watcher` Launch Agent which was reported as "stopped" and "missing tmux" for investigation.

## User Feedback & Decisions
- The user noticed `la` showed the agent as stopped.
- The user noted "No tmux for investigating", referring to the recent removal of the tmux wrapper.

## Changes Made
- **Modified `la` script (`/Users/matt/.local/bin/la`)**:
    - **Healthier Status**: Changed `la list` to display `oneshot` agents (like `rules-watcher`) as `watching` (green circle) instead of `stopped` (yellow circle) when they are idle but loaded with `WatchPaths`.
    - **Log Discovery**: Updated `la logs` to read `StandardOutPath` from the agent's plist. This allows `la logs rules-watcher` to work even without a tmux session.
    - **Added `la start`**: New command to manually trigger an agent (e.g., `la start rules-watcher`).
- **Fixed `com.matt.agent.rules-watcher.plist`**:
    - Added `RunAtLoad: true` to ensure an initial sync happens when the agent is loaded.
    - Repaired the plist after an accidental corruption during editing.
- **Verified Sync**: Confirmed `sync_rules.sh` is working and `~/.gemini/GEMINI.md` is in sync with `ai-os/.gemini/GEMINI.md`.

## What Worked
- The new `la` status logic correctly identifies `rules-watcher` as "watching".
- `la logs rules-watcher` successfully tails the log file at `tmp/rules_watcher.log`.
- Bidirectional sync verified by checking file timestamps and sizes.

## What Didn't Work / Known Issues
- Initial attempt to use `precision_edit.py` on the plist resulted in corruption due to multiple matches for the target string. Fixed using a python script to write a clean plist.

## Architecture Notes
- `oneshot` agents in launchd exit after running. The `la` tool now distinguishes between a "dead/crashed" agent and an "idle/watching" oneshot agent.
- `la logs` is now more robust by inspecting the plist configuration.
