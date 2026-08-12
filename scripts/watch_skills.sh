#!/bin/bash
set -euo pipefail

# Directories to watch
WATCH_DIRS=(
    "$HOME/projects/ai-os/skills"
    "$HOME/.hermes/skills"
    "$HOME/.claude/skills"
    "$HOME/.agents/skills"
    "$HOME/.gemini/config/skills"
    "$HOME/.gemini/antigravity-cli/skills"
    "$HOME/.agy/skills"
    "$HOME/.gemini/antigravity/skills"
)

SYNC_SCRIPT="$HOME/projects/ai-os/scripts/sync_skills.py"
LOG="$HOME/Library/Logs/launch-agents/sync-skills.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

mkdir -p "$(dirname "$LOG")"

log "Starting sync_skills watcher..."

# Initial sync
python3 "$SYNC_SCRIPT" >> "$LOG" 2>&1

# Watch for changes
fswatch -0 "${WATCH_DIRS[@]}" | while read -d "" event; do
    log "Detected change, triggering sync."
    python3 "$SYNC_SCRIPT" >> "$LOG" 2>&1
done
