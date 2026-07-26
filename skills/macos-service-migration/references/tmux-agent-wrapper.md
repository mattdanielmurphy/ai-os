# tmux-agent-wrapper Architecture

After migrating or configuring launch agents, wrap them in `tmux-agent-wrapper.sh` to make every scripted service accessible via tmux, with auto-restart on file modification and macOS notifications.

## Core Script

`~/Library/Scripts/tmux-agent-wrapper.sh` — unified wrapper, invoked from launchd plist `ProgramArguments`.

### Syntax

```
tmux-agent-wrapper.sh <keepalive|oneshot> [--no-watch] <session-name> <script-path> [args...]
```

### Modes

| Mode | When to use | File-watch mechanism | Restart trigger |
|---|---|---|---|
| `keepalive` | Long-running daemons (scripts) | `fswatch --event Updated` on the script file | Script edit → osascript notification + tmux restart |
| `keepalive --no-watch` | Long-running binaries (Chrome, node, python) | None — polls `tmux has-session` every 3s | Process crash → tmux session dies → wrapper re-creates it |
| `oneshot` | Event/schedule-driven services | launchd `WatchPaths` in plist (script path added as watched path) | launchd kills + re-launches wrapper when file changes |

### Notification

Every restart fires: `osascript -e 'display notification "Restarting <session>..." with title "⚡ <script>" subtitle "Script modified"'` — auto-dismisses on macOS.

## Plist Structure Convention

### KeepAlive daemon (script)
```xml
<key>ProgramArguments</key>
<array>
    <string>~/Library/Scripts/tmux-agent-wrapper.sh</string>
    <string>keepalive</string>
    <string>agent-<short-name></string>
    <string>/path/to/script.sh</string>
</array>
<key>KeepAlive</key><true/>
```

### Binary daemon (no file-watch)
```xml
<key>ProgramArguments</key>
<array>
    <string>~/Library/Scripts/tmux-agent-wrapper.sh</string>
    <string>keepalive</string>
    <string>--no-watch</string>
    <string>agent-<short-name></string>
    <string>/path/to/binary</string>
    <string>--arg1</string>
    <string>--arg2</string>
</array>
<key>KeepAlive</key><true/>
```

### Oneshot (event/schedule)
```xml
<key>ProgramArguments</key>
<array>
    <string>~/Library/Scripts/tmux-agent-wrapper.sh</string>
    <string>oneshot</string>
    <string>agent-<short-name></string>
    <string>/path/to/script.sh</string>
</array>
<key>WatchPaths</key>
<array>
    <string>/path/to/script.sh</string>     <!-- auto-restart on edit -->
    <string>/path/to/watched/resource</string>  <!-- original watch target -->
</array>
```

For `StartInterval` services, the wrapper runs in oneshot mode, launches the script in tmux, and exits. launchd re-fires on the interval. Adding the script path to WatchPaths (alongside StartInterval) lets launchd restart on edit.

## Logging

All logs consolidated: `~/Library/Logs/launch-agents/<service-name>.log`

Set in the plist:
```xml
<key>StandardOutPath</key>
<string>~/Library/Logs/launch-agents/<service>.log</string>
<key>StandardErrorPath</key>
<string>~/Library/Logs/launch-agents/<service>.log</string>
```

## Helper Script

`~/Library/Scripts/tmux-agents.sh` — prints status of all running agent tmux sessions, their descriptions, and quick-attach commands. Run it directly or alias in `.zshrc`:
```bash
alias agents='~/Library/Scripts/tmux-agents.sh'
```

## Migration Steps (from direct plist to tmux-wrapper)

1. Create `~/Library/Scripts/tmux-agent-wrapper.sh` and `tmux-agents.sh`
2. Unload old agents: `launchctl bootout gui/$(id -u)/<old-label>`
3. Write new plists with `com.matt.agent.<name>` labels and `com.matt.agent.*.plist` filenames
4. Load new agents: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.matt.agent.<name>.plist`
5. Archive old plists: `mv ~/Library/LaunchAgents/<old-name>.plist ~/Library/LaunchAgents/Archive/`
6. Verify: `launchctl list com.matt.agent.<name>` and `tmux has-session -t agent-<name>`

## Pitfalls

1. **Old tmux sessions from previous script versions**: If the old script managed its own tmux session (e.g., `run_litellm.sh` used `tmux new-session -s litellm`), that old session persists after migration. Kill it with `tmux kill-session -t <old-name>`.

2. **`--no-watch` for binaries only**: The `--no-watch` flag skips fswatch but keeps the wrapper alive by polling `tmux has-session`. Use it for Chrome, node, python — anything the user won't be editing.

3. **Oneshot mode expects the script to exit**: Don't use oneshot for long-running processes. Use `keepalive` (or `keepalive --no-watch`) so the wrapper stays alive and fswatch/restart works.

4. **fswatch must be installed**: `brew install fswatch`. The wrapper falls back to stat-based polling (every 2s) if fswatch isn't available, but this is less efficient.

5. **`com.matt.agent.*` naming convention**: New plists use `com.matt.agent.<name>` labels and `com.matt.agent.<name>.plist` filenames to clearly distinguish from plain `com.matt.*` services.

6. **Stale services with missing binaries**: When a referenced binary or env wrapper doesn't exist (e.g., `ai.openclaw.gateway` after migration), the agent exits with non-zero status and KeepAlive keeps retrying. Identify these and remove/archive the plist.