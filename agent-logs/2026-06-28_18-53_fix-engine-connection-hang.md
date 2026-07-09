## Goal
Fix an issue where returning to the app occasionally results in an endless "Connecting to Engine session at..." message.

## Changes Made
- Modified `trigger_tmux_refresh` in `src-tauri/src/main.rs` to stop passing a specific session name to `tmux refresh-client -t`.
  - The `-t` parameter in `refresh-client` is intended for specifying the *client*, not the session. Passing a session name was causing tmux to fail with "client not found" and ignore the redraw request.
  - Removed the `-t` argument entirely, which safely causes tmux to redraw for all active clients, ensuring that the PTY immediately receives the screen contents from tmux.

## What Worked
- Omitting the `-t` parameter allows `tmux refresh-client` to work properly. When a user returns to the app, the frontend buffer gets instantly populated with the current pane contents, overwriting the "Connecting..." message.

## What Didn't Work / Known Issues
- Initially considered capturing the pane text, but refreshing the client natively transmits the full ANSI escape sequences needed to rebuild the xterm.js UI, which is better.

## Architecture Notes
- Tauri keeps the backend process running while windows can be suspended or reloaded. This means `sessions` state is retained, but the frontend needs a push (`tmux refresh-client`) to redraw the session state when it reconnects.
