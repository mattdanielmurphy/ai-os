# fswatch Watchdog Pattern (keepalive mode)

A reusable architecture for long-running directory watchers inside `tmux-agent-wrapper.sh` (keepalive mode). Used by the `gemini-ingest` agent and applicable to any auto-ingestion, auto-sync, or live-processing daemon.

## Architecture

```
launchd (KeepAlive=true)
  └─ tmux-agent-wrapper.sh keepalive agent-<name> watchdog.sh
       └─ tmux session: agent-<name>
            └─ watchdog.sh
                 ├─ Initial run on startup (full pass)
                 └─ fswatch loop: monitor dir for Created/Updated events
                      └─ On change → run worker script (idempotent)
```

## Watchdog Script Template

```bash
#!/bin/bash
# <name>-watch.sh — Watch <dir> for changes and trigger <action>.
set -euo pipefail

WATCH_DIR="$HOME/path/to/monitored/dir"
WORKER="$HOME/path/to/worker/script.py"   # or .sh
FSWATCH_BIN="/opt/homebrew/bin/fswatch"
LOG="$HOME/Library/Logs/launch-agents/<name>.log"

cd "$HOME/projects/<project>" || exit 1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Validate
for path in "$WATCH_DIR" "$WORKER"; do
    [ -e "$path" ] || { log "ERROR: $path not found"; exit 1; }
done

# Initial full pass on startup
log "Starting initial run..."
"$WORKER" 2>&1 | tee -a "$LOG"

# Watch for changes — filter to only relevant file extensions
log "Watching $WATCH_DIR for changes..."
"$FSWATCH_BIN" -0 --event Created --event Updated "$WATCH_DIR" 2>/dev/null \
    | while read -d "" event_path; do
        case "$event_path" in
            *.md|*.json|*.yaml)   # adjust extensions as needed
                log "Detected change: $(basename "$event_path")"
                "$WORKER" 2>&1 | tee -a "$LOG"
                ;;
        esac
    done

# If fswatch exits, signal parent wrapper to restart
log "ERROR: fswatch exited unexpectedly"
exit 1
```

## Key Design Decisions

| Concern | Solution |
|---|---|
| **Initial state** | Run a full pass on startup — catch any files added while the agent was off |
| **Idempotency** | Worker script must be safe to run repeatedly (check PK / content hash before insert) |
| **Noise filtering** | Filter by extension in the `case` block — skip `.DS_Store`, temp files, etc. |
| **Crash recovery** | `exit 1` — tmux-agent-wrapper detects session death, restarts on KeepAlive |
| **Log visibility** | `tee -a` to log file AND stdout (visible in tmux) |
| **Script edit restarts** | tmux-agent-wrapper's own fswatch on the watchdog script auto-restarts on modification |

## fswatch Flags

- `-0` — nul-delimited output (safe for filenames with spaces)
- `--event Created` — new files
- `--event Updated` — modifications to existing files
- Pipe with `read -d ""` to consume nul-delimited events

## Plist Integration

```xml
<key>ProgramArguments</key>
<array>
    <string>~/Library/Scripts/tmux-agent-wrapper.sh</string>
    <string>keepalive</string>
    <string>agent-<name></string>
    <string>/path/to/watchdog.sh</string>
</array>
<key>KeepAlive</key><true/>
<key>WorkingDirectory</key>
<string>/Users/matt/projects/ai-os</string>
<key>StandardOutPath</key>
<string>/Users/matt/Library/Logs/launch-agents/<name>.log</string>
<key>StandardErrorPath</key>
<string>/Users/matt/Library/Logs/launch-agents/<name>.log</string>
```

## Verification Checklist

- `launchctl list com.matt.agent.<name>` — PID present, LastExitStatus=0
- `tmux has-session -t agent-<name>` — session exists
- Log shows initial run + "Watching" message
- Drop a matching test file → log shows detection + worker run within ~2 seconds
- Delete test file → agent idle (no crash)