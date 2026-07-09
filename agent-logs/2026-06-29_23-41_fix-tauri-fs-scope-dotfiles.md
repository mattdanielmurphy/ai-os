## Goal
Fix Tauri filesystem scope violation when trying to read `.ai-os/output.md` in the preview pane.

## Changes Made
1. Modified `src-tauri/tauri.conf.json`: Added `$HOME/**/.ai-os/*`, `$HOME/**/.ai-os/**/*`, `$HOME/projects/**/.ai-os/*`, and `$HOME/projects/**/.ai-os/**/*` to the allowed `fs` scopes.
2. Updated `memory/agent-quirks-and-workarounds.md`: Described the root cause (Tauri filesystem scope glob patterns omitting hidden dotfiles/folders by default) and the resolution.

## What Worked
- Tauri's configuration was updated, and frontend assets rebuilt successfully.

## What Didn't Work / Known Issues
- Because Tauri configuration files are compile-time/startup settings, the user must restart the Tauri application/dev process for these changes to take effect.
