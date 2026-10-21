#!/bin/bash
# Nightly restart to clear swap and leaky background processes (Matt, 2026-10-21).
# Run by ~/Library/LaunchAgents/com.matt.agent.nightly-restart.plist at 04:30,
# with retries every 15 min until 05:45.
#
# Skips when:
#   - it's outside 04:25-06:00 (launchd fires missed jobs on wake, e.g. at 9am)
#   - the Mac restarted less than 3 hours ago (an earlier try already worked)
#   - a Claude Code turn is running (the Claude app holds its "Electron"
#     keep-awake assertion during turns); the next retry tries again
# The restart asks every app to quit, like Apple menu > Restart (windows reopen
# after login). An app with unsaved work (Ableton) cancels it and keeps its save
# prompt up, so nothing is lost. A failure leaves a toast (claude_notify).
# Test without restarting: DRY_RUN=1 scripts/nightly_restart.sh

set -u
log() { echo "$(date '+%F %T') $*"; }

now=$((10#$(date +%H) * 60 + 10#$(date +%M)))
if [ -z "${FORCE_WINDOW:-}" ] && { [ "$now" -lt $((4 * 60 + 25)) ] || [ "$now" -gt $((6 * 60)) ]; }; then
  log "skip: outside the 04:25-06:00 window"
  exit 0
fi

boot=$(sysctl -n kern.boottime | sed -E 's/.*sec = ([0-9]+).*/\1/')
up=$(( $(date +%s) - boot ))
if [ "$up" -lt $((3 * 3600)) ]; then
  log "skip: restarted $((up / 60)) min ago"
  exit 0
fi

if pmset -g assertions | grep -q 'Claude): .*NoIdleSleepAssertion named: "Electron"'; then
  log "wait: a Claude Code turn is running; retrying at the next slot"
  exit 0
fi

if [ -n "${DRY_RUN:-}" ]; then
  log "dry run: would restart now (up $((up / 3600)) h)"
  exit 0
fi

log "restarting (up $((up / 3600)) h, swap: $(sysctl -n vm.swapusage | awk '{print $6}'))"
if ! err=$(osascript -e 'tell application "loginwindow" to «event aevtrest»' 2>&1); then
  log "restart failed: $err"
  printf 'Nightly restart failed\n%s\n' "$err" > "$HOME/projects/ai-os/tmp/notify/.nightly-restart.txt" &&
    mv "$HOME/projects/ai-os/tmp/notify/.nightly-restart.txt" "$HOME/projects/ai-os/tmp/notify/nightly-restart.txt"
fi
