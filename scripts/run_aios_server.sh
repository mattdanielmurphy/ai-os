#!/bin/bash
# AI-OS Companion Server Runner
# Supervised by macOS launchd via ~/.local/bin/la

set -euo pipefail

export HOME="/Users/matt"
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/Users/matt/.bun/bin:/Users/matt/.cargo/bin:/Users/matt/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Clean up any lingering process on 3031 before startup
STALE_PIDS=$(lsof -ti :3031 2>/dev/null || true)
if [ -n "$STALE_PIDS" ]; then
    echo "[run_aios_server] Clearing stale process on port 3031: $STALE_PIDS"
    echo "$STALE_PIDS" | xargs kill -9 2>/dev/null || true
    sleep 0.5
fi

LOG_DIR="$HOME/.ai-os/logs"
mkdir -p "$LOG_DIR"

echo "[run_aios_server] Starting AI-OS Companion App at $(date)..."
cd /Users/matt/projects/ai-os/apps/gemini-companion

exec bun tauri dev
