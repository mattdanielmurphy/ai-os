#!/usr/bin/env bash
# Start / stop / check TypeWhisper dictation without keypresses (no hotkey, no focus change).
# Usage: scripts/dictate.sh [start|stop|toggle|status]   (default: status)
#
# How: TypeWhisper's local HTTP API (127.0.0.1 only, default port 8978). It must be switched on
# once in TypeWhisper > Settings > Advanced > API server. While it runs, TypeWhisper writes its
# port and bearer token to an owner-only discovery file, read here (never printed).
# Text lands in whatever field is focused when dictation stops, like the hotkey.
# Every action prints TypeWhisper's status JSON at the end; stop waits until the text is pasted.
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
status() { call GET status; }
recording() { status | grep -Eq '"is_recording" *: *true'; }
# After stop, TypeWhisper transcribes then pastes; wait (max 10s) until it's back to idle so the text
# has landed before the caller moves focus. Prints the final status either way.
settle() { for _ in $(seq 40); do s="$(status)"; grep -Eq '"state" *: *"(processing|inserting)"' <<<"$s" || break; sleep 0.25; done; status; }

case "$action" in
  start)  recording || call POST start >/dev/null; status ;;   # idempotent; prints status JSON
  stop)   ! recording || call POST stop >/dev/null; settle ;;  # returns once the text is pasted
  status) status ;;
  toggle)
    if recording; then call POST stop >/dev/null; settle; else call POST start >/dev/null; status; fi ;;
  *) echo "usage: $0 [start|stop|toggle|status]" >&2; exit 64 ;;
esac
