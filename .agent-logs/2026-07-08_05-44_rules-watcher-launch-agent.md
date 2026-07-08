## Goal
Set up a background macOS Launch Agent watcher to automatically sync the global rules file (`~/.gemini/GEMINI.md`) into the workspace repository (`.gemini/GEMINI.md`) using the `sync_rules.sh` script whenever it gets modified.

## User Feedback & Decisions
- Configure a Launch Agent that watches `~/.gemini/GEMINI.md` and triggers the rules synchronization utility.

## Changes Made
- **[NEW] [com.mattmurphy.ai-os-rules-watcher.plist](file:///Users/matt/Library/LaunchAgents/com.mattmurphy.ai-os-rules-watcher.plist)**: Configured Launch Agent that monitors the `~/.gemini/GEMINI.md` path and automatically triggers the `/Users/matt/projects/ai-os/scripts/sync_rules.sh` executable.
- **[MODIFY] [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md)**: Documented the new Launch Agent in the active catalog of macOS custom background services.

## What Worked
- Loaded the plist successfully using `launchctl load`.
- Verification confirms it shows as loaded and waiting for changes.

## Architecture Notes
- Launchd `WatchPaths` key monitors path changes. We set the `WorkingDirectory` specifically to `/Users/matt/projects/ai-os` to guarantee that relative directory references in the sync script resolve correctly.
