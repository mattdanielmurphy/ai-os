#!/usr/bin/env bash
# Start / stop / check TypeWhisper dictation without keypresses (no hotkey, no focus change).
# Usage: scripts/dictate.sh [start|stop|toggle|status]   (default: status)
#
# How: TypeWhisper's local HTTP API (127.0.0.1 only, default port 8978). It must be switched on
# once in TypeWhisper > Settings > Advanced > API server. While it runs, TypeWhisper writes its
# port and bearer token to an owner-only discovery file, read here (never printed).
# Text lands in whatever field is focused when dictation stops, like the hotkey.
#
# start/stop/toggle turn on Matt's mic: that is Mac input, so agents take clearance first:
#   t=$(~/.hammerspoon/bin/claude-control ask "Start dictation to <why>" 3 --light) && scripts/dictate.sh start
#   ~/.hammerspoon/bin/claude-control done "${t#granted }"
set -euo pipefail
action="${1:-status}"
disc="$HOME/Library/Application Support/TypeWhisper/api-discovery.json"

if [[ ! -r "$disc" ]]; then
  echo "TypeWhisper API is off: turn on Settings > Advanced > API server" >&2; exit 2
fi
port="$(/usr/bin/plutil -extract port raw -o - "$disc" 2>/dev/null || echo 8978)"
token="$(/usr/bin/plutil -extract token raw -o - "$disc")"
base="http://127.0.0.1:$port/v1/dictation"
call() { curl -fsS -X "$1" -H "Authorization: Bearer $token" "$base/$2"; echo; }

case "$action" in
  start)  call POST start ;;
  stop)   call POST stop ;;
  status) call GET status ;;
  toggle)
    if call GET status | grep -Eq '"(is_)?recording" *: *true'; then call POST stop; else call POST start; fi ;;
  *) echo "usage: $0 [start|stop|toggle|status]" >&2; exit 64 ;;
esac
