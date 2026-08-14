#!/bin/bash
# gemini-ingest-watch.sh — Watch gemini-archive threads dir and auto-ingest into Hermes FTS5.
#
# Runs inside tmux session via tmux-agent-wrapper.sh (keepalive mode).
# Attach: tmux attach -t agent-gemini-ingest
#
# Uses fswatch to monitor the archive directory for new/modified markdown files,
# then runs the idempotent Python ingester (which skips already-ingested sessions).

set -euo pipefail

ARCHIVE_DIR="$HOME/Documents/gemini-archive/threads"
INGESTER="$HOME/projects/ai-os/scripts/ingest_gemini_archives.py"
FSWATCH_BIN="/opt/homebrew/bin/fswatch"
LOG="$HOME/Library/Logs/launch-agents/gemini-ingest.log"

cd "$HOME/projects/ai-os"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Validate dependencies
if [ ! -d "$ARCHIVE_DIR" ]; then
    log "ERROR: Archive directory not found: $ARCHIVE_DIR"
    exit 1
fi

if [ ! -f "$INGESTER" ]; then
    log "ERROR: Ingester script not found: $INGESTER"
    exit 1
fi

# Initial ingestion on startup
log "Starting initial ingestion..."
python3 "$INGESTER" --write 2>&1 | tee -a "$LOG"
python3 "$HOME/projects/ai-os/scripts/gemini_antigravity_bridge.py" --days 90 2>&1 | tee -a "$LOG"

# Watch for changes — fswatch fires on Created/Updated events
log "Watching $ARCHIVE_DIR for changes..."
"$FSWATCH_BIN" -0 --event Created --event Updated "$ARCHIVE_DIR" 2>/dev/null \
    | while read -d "" event_path; do
        # Filter: only process .md files
        case "$event_path" in
            *.md)
                log "Detected change: $(basename "$event_path")"
                python3 "$INGESTER" --write 2>&1 | tee -a "$LOG"
                python3 "$HOME/projects/ai-os/scripts/gemini_antigravity_bridge.py" --file "$event_path" 2>&1 | tee -a "$LOG"
                ;;
            *)
                # Ignore non-markdown changes (.DS_Store, etc.)
                ;;
        esac
    done

# If fswatch exits unexpectedly, keep the process alive for wrapper crash-detection
log "ERROR: fswatch exited unexpectedly. Restarting..."
exit 1