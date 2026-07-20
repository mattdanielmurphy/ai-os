# Rules Watcher and Bidirectional Rules Sync Fix

## Goal
The user noticed the `rules-watcher` launch agent was stopped/unhealthy, and asked to clarify why `GEMINI.md`, `CLAUDE.md`, and `AGENTS.md` all exist, and make the rules sync system clear, organized, and robust.

## User Feedback & Decisions
- Confirmed that the launch agent was stopped and needs debugging.
- Unified rules management around local git-tracked repository configs while maintaining global availability at `~/.gemini/GEMINI.md`.

## Changes Made
- Modified `/Users/matt/Library/LaunchAgents/com.matt.agent.rules-watcher.plist` to run `sync_rules.sh` directly without `tmux-agent-wrapper.sh` to prevent TCC sandbox and tmux environment inheritance blocks.
- Added `/Users/matt/projects/ai-os/.gemini/GEMINI.md` to `WatchPaths` in the plist to trigger syncs on repository modifications.
- Refactored `scripts/sync_rules.sh` to perform a robust bidirectional "newer wins" sync using absolute paths.
- Replaced `AGENTS.md` with a symlink to `.gemini/GEMINI.md` to consolidate Gemini/agy rule representations inside the repo.

## What Worked
- Launch agent runs successfully and performs bidirectional sync, propagating changes made in `AGENTS.md` (which links to `.gemini/GEMINI.md`) to the global `~/.gemini/GEMINI.md`, and vice-versa.

## What Didn't Work / Known Issues
- `tmux-agent-wrapper.sh` oneshot execution is subject to sandbox restrictions when started inside launchd, preventing it from reading file directories. Running the sync script directly solves the issue.

## Architecture Notes
- `AGENTS.md` is a symlink to `.gemini/GEMINI.md`.
- `CLAUDE.md` contains Claude-specific formatting/rules and remains a separate file.
- `rules-watcher` launch agent watches both files, running `sync_rules.sh` on changes.
