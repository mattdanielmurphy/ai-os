#!/bin/bash
# Query companion runner, supervised by macOS launchd.

set -euo pipefail

export HOME="/Users/matt"
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/Users/matt/.bun/bin:/Users/matt/.cargo/bin:/Users/matt/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# The query companion owns only its HTTP bridge. It must not interfere with a
# Vite dev server that happens to use port 1420.
STALE_PIDS=$(lsof -ti :3031 2>/dev/null || true)
if [ -n "$STALE_PIDS" ]; then
    echo "[run_aios_server] Clearing stale process on port 3031: $STALE_PIDS"
    echo "$STALE_PIDS" | xargs kill -9 2>/dev/null || true
    sleep 0.5
fi

LOG_DIR="$HOME/.ai-os/logs"
mkdir -p "$LOG_DIR"

QUERY_COMPANION="/Users/matt/projects/ai-os/target/release/query-aios-companion"

if [ ! -x "$QUERY_COMPANION" ]; then
    echo "[run_aios_server] Missing release binary: $QUERY_COMPANION" >&2
    exit 1
fi

echo "[run_aios_server] Starting AIOS Query Companion at $(date)..."
exec caffeinate -s -i "$QUERY_COMPANION"
