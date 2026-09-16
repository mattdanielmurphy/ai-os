#!/usr/bin/env bash
set -euo pipefail

# Kill any existing triage proxy and hermes serve instances on these ports
pkill -f "triage_proxy.py" || true
pkill -f "hermes serve --port 9120" || true
pkill -f "hermes serve --port 9119" || true
sleep 1

echo "[+] Starting Hermes Agent backend on port 9120..."
export HERMES_DASHBOARD_SESSION_TOKEN="ai_os_secret_token_123456"
~/.local/bin/hermes serve --port 9120 &
HERMES_PID=$!

echo "[+] Starting Triage Proxy on port 9119 -> 9120..."
python3 -m pip install websockets || true
python3 "$(dirname "$0")/triage_proxy.py" --port 9119 --target 9120 &
PROXY_PID=$!

echo "[+] Ready! Hermes Triage Proxy is running. Press Ctrl+C to stop."

# Wait for both processes and kill both on exit
trap 'kill $HERMES_PID $PROXY_PID 2>/dev/null' EXIT
wait $HERMES_PID $PROXY_PID
