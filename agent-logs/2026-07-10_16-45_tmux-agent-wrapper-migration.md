## Goal
Migrate all launch agent services to run inside named tmux sessions with auto-restart on script modification. Wrap all agent scripts via `tmux-agent-wrapper.sh`, enable fswatch-based file watching with macOS notifications on restart, and consolidate logging to `~/Library/Logs/launch-agents/`.

## User Feedback & Decisions
- All launch agent scripts should be accessible via tmux
- All should auto-restart when the script files themselves are modified
- Should display a temporary notification when the launch agents restart

## Changes Made

### New Scripts Created
- **`~/Library/Scripts/tmux-agent-wrapper.sh`** — Unified wrapper that runs any launch agent inside a named tmux session. Two modes:
  - `keepalive`: Runs fswatch on the script file, auto-restarts + shows notification on modification. For long-running daemons.
  - `keepalive --no-watch`: Same but without file-watching (for binaries like Chrome).
  - `oneshot`: Runs script in tmux and exits. launchd handles scheduling/WatchPaths. Script's own path added to WatchPaths for auto-restart.
- **`~/Library/Scripts/tmux-agents.sh`** — Status overview helper: shows all agent sessions, descriptions, and quick commands.

### New Launch Agent Plists (`com.matt.agent.*`)
| Plist | session | mode |
|---|---|---|
| `com.matt.agent.irig-watcher` | `agent-irig-watcher` | keepalive |
| `com.matt.agent.litellm` | `agent-litellm` | keepalive |
| `com.matt.agent.userscript-bundler` | `agent-userscript-bundler` | keepalive |
| `com.matt.agent.chrome-debug` | `agent-chrome-debug` | keepalive --no-watch |
| `com.matt.agent.hermes-gateway` | `agent-hermes-gateway` | keepalive --no-watch |
| `com.matt.agent.rules-watcher` | `agent-rules-watcher` | oneshot (+ WatchPaths for GEMINI.md + sync_rules.sh) |
| `com.matt.agent.energy-monitor` | `agent-energy-monitor` | oneshot (+ StartInterval 300s + WatchPaths for script) |
| `com.matt.agent.notesync` | `agent-notesync` | oneshot (+ WatchPaths for Obsidian vault) |
| `com.matt.agent.backup-agents` | `agent-backup-agents` | oneshot (+ StartCalendarInterval daily 11:30) |

### Script Modified
- **`~/litellm/run_litellm.sh`** — Simplified to just run litellm directly (stripped internal tmux management since the wrapper handles it now).

### Removed / Archived
- 10 old plists archived to `~/Library/LaunchAgents/Archive/`
- `ai.openclaw.gateway` removed entirely (stale — `~/.openclaw/` directory doesn't exist, superseded by `ai.hermes.gateway`)

### Documentation
- **`MAC_ENVIRONMENT.md`** — Updated the Launch Agents table with new naming, tmux sessions, and mode descriptions.

## What Worked
- All 9 agents loaded successfully with zero exit codes and PIDs
- fswatch processes running for all keepalive script-based agents (irig-watcher, litellm, userscript-bundler)
- `--no-watch` patterns working correctly for binary-based agents (Chrome, Hermes gateway)
- Touch test on `irig_watcher.sh` confirmed: fswatch detected change, wrapper restarted tmux session, session stayed alive
- Logs consolidated to `~/Library/Logs/launch-agents/`

## What Didn't Work / Known Issues
- `.openclaw` directory didn't exist, so `ai.openclaw.gateway` was a stale agent. Removed.
- The old `litellm` tmux session (created by the old `run_litellm.sh`) conflicted briefly with the new `agent-litellm` session until the old one was manually killed.
- OpenClaw gateway's env wrapper (`ai.openclaw.gateway-env-wrapper.sh`) didn't exist at the expected path.

## Architecture Notes
- `tmux-agent-wrapper.sh` uses fswatch (1.18.3) for efficient file-watching on macOS. Falls back to stat-based polling if fswatch isn't available.
- The `oneshot` mode + WatchPaths pattern uses launchd itself to detect script modifications and restart the agent — no fswatch needed for those.
- For `--no-watch` keepalive, the wrapper polls tmux every 3s to detect crashes and auto-restart the session.
- Notifications use `osascript -e 'display notification ...'` which auto-dismisses after ~5 seconds on macOS.