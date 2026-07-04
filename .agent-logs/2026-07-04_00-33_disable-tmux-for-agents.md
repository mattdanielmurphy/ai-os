## Goal
The user requested to reduce the number of tmux sessions. Specifically, they were annoyed by quota limits forcing them to re-authenticate across many individual tmux sessions for agent processes (since tmux sessions outlive the app, retaining stale environment state/API keys). They requested 1-2 sessions: one for user interaction, one sterile for the agent.

## Changes Made
- Modified `src-tauri/src/main.rs`:
  - `spawn_single_pty`: Changed to only utilize `tmux` when spawning the `"mini"` terminal type.
  - `ensure_engine_pty`: Removed tmux session termination commands for `"claude"` and `"agy"`.
  - `is_engine_running_proc`: Simplified to only search by `shell_pid` without checking tmux panes for `"claude"` and `"agy"`.
  - `prepare_spare_engine`: Stubbed to do nothing, preventing unused spare tmux sessions.
  - `spawn_fresh_engine`: Removed logic for cycling/replacing tmux sessions.
  - `close_project_session`: Only kills the `"mini"` tmux session upon project close.

## What Worked
- Disabling tmux for `claude` and `agy` allows them to run directly under a raw PTY. They are inherently "sterile" processes that will cleanly inherit environment variables and not outlive the main application session context.
- We reduced the number of tmux sessions generated per project from three down to just one (the `mini` terminal, preserving scrollback state).
- The rust code successfully compiled with the changes.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The GUI previously relied on tmux to manage scrollback buffers for everything including CLI execution agents. However, agent interactions are primarily surfaced through UI messaging rather than purely scrolling terminal logs, so losing background scrollback retention for the agents across app restarts isn't an issue.
- With tmux removed for agent processes, updating an API key globally will be easier as the user can simply restart the agent without battling persistent detached tmux environments.
