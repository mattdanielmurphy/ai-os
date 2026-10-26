#!/bin/bash
# Nightly restart to clear swap and leaky background processes (Matt, 2026-10-21).
# Run by ~/Library/LaunchAgents/com.matt.agent.nightly-restart.plist at 04:30,
# with retries every 15 min until 05:45.
#
# Skips when:
#   - it's outside 04:25-06:00 (launchd fires missed jobs on wake, e.g. at 9am)
#   - the Mac restarted less than 3 hours ago (an earlier try already worked)
#   - Claude is really working: a Claude Code transcript was written in the last
#     10 min, or a Claude Bash command younger than an hour is still running.
#     (Not the Claude app's "Electron" NoIdleSleep assertion: the app holds that
#     for days with nothing running, which blocked every night on Oct 24-25.)
#     The next retry tries again.
# The restart asks every app to quit, like Apple menu > Restart (windows reopen
# after login). An app with unsaved work (Ableton) cancels it and keeps its save
# prompt up, so nothing is lost. Two minutes later, if the Mac is still up, it
# logs loginwindow's reason (which app cancelled) so the next retry and the
# morning check can say why.
#
# Morning check: `nightly_restart.sh check` (com.matt.agent.nightly-restart-check,
# 09:00, runs on wake if missed) toasts Matt when the Mac didn't restart overnight,
# with the last reason from the log.
#
# Test without restarting: DRY_RUN=1 FORCE_WINDOW=1 scripts/nightly_restart.sh
#                          DRY_RUN=1 scripts/nightly_restart.sh check

set -u
LOG="$HOME/Library/Logs/launch-agents/nightly-restart.log"
NOTIFY="$HOME/.hammerspoon/bin/claude-notify"
log() { echo "$(date '+%F %T') $*"; }

# "{ sec = 1792..., usec = 123 }": anchor on "{ sec", or the greedy match grabs usec.
boot=$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*/\1/')
up=$(( $(date +%s) - boot ))

if [ "${1:-}" = "check" ]; then
  # Restarted since 04:00 today? Then last night worked.
  since=$(date -j -f '%F %T' "$(date +%F) 04:00:00" +%s)
  if [ "$boot" -ge "$since" ]; then
    log "check: ok, restarted at $(date -r "$boot" '+%H:%M')"
    exit 0
  fi
  reason=$(grep "^$(date +%F)" "$LOG" 2>/dev/null | grep -v ' check: \| dry run: \| outside the ' | tail -1 | cut -d' ' -f3-)
  [ -z "$reason" ] && reason="it never ran (the Mac was probably asleep at 4:30)"
  msg="Up $((up / 3600)) h. Last try: $reason"
  log "check: no restart overnight. $msg"
  if [ -n "${DRY_RUN:-}" ]; then
    log "dry run: would toast \"The Mac didn't restart last night\""
  else
    "$NOTIFY" "The Mac didn't restart last night" "$msg" --kind needs
  fi
  exit 0
fi

now=$((10#$(date +%H) * 60 + 10#$(date +%M)))
if [ -z "${FORCE_WINDOW:-}" ] && { [ "$now" -lt $((4 * 60 + 25)) ] || [ "$now" -gt $((6 * 60)) ]; }; then
  log "skip: outside the 04:25-06:00 window"
  exit 0
fi

if [ "$up" -lt $((3 * 3600)) ]; then
  log "skip: restarted $((up / 60)) min ago"
  exit 0
fi

# Real Claude work: a transcript written recently, or a young Bash tool command
# (a child `eval` of the claude CLI, as in scripts/tool_watchdog.py). Old
# background commands (dev servers) don't count, or they'd block forever.
busy=$(find "$HOME/.claude/projects" -name '*.jsonl' -mmin -"${BUSY_MIN:-10}" 2>/dev/null | head -1)
if [ -n "$busy" ]; then
  log "wait: a Claude thread wrote $(basename "$(dirname "$busy")") in the last ${BUSY_MIN:-10} min; retrying at the next slot"
  exit 0
fi
# etime under an hour is "MM:SS"; "HH:MM:SS" and "D-HH:MM:SS" are older.
cmd=$(ps -axo pid=,ppid=,etime=,command= | awk '
  NR == FNR { if ($0 ~ /claude-code\/.*\/claude( |$).*--output-format/) cli[$1] = 1; next }
  ($2 in cli) && /-c .*eval/ && $3 ~ /^[0-9]+:[0-9]+$/ { print $1; exit }
' <(ps -axo pid=,command=) -)
if [ -n "$cmd" ]; then
  log "wait: a Claude command is running (pid $cmd); retrying at the next slot"
  exit 0
fi

if [ -n "${DRY_RUN:-}" ]; then
  log "dry run: would restart now (up $((up / 3600)) h)"
  exit 0
fi

log "restarting (up $((up / 3600)) h, swap: $(sysctl -n vm.swapusage | awk '{print $6}'))"
# The Claude app "failed to quit" and stopped the Oct 23 restart (loginwindow's
# dialog). Nothing is running (checked above), so quit it first, then force it.
if pgrep -x Claude > /dev/null; then
  osascript -e 'quit app "Claude"' > /dev/null 2>&1
  for _ in $(seq 30); do pgrep -x Claude > /dev/null || break; sleep 1; done
  if pgrep -x Claude > /dev/null; then
    log "Claude didn't quit in 30 s; killing it"
    pkill -TERM -x Claude; sleep 10; pkill -KILL -x Claude
  fi
fi
# aevtrrst = Restart without the "Are you sure?" dialog. aevtrest only showed that
# dialog, so the Mac never restarted (up 4 days, swap 20 GB, 2026-10-23). Apps
# with unsaved work can still cancel it.
if ! err=$(osascript -e 'tell application "loginwindow" to «event aevtrrst»' 2>&1); then
  log "restart failed: $err"
  "$NOTIFY" "Nightly restart failed" "$err" --kind error
  exit 1
fi
# Still here after 2 min = something cancelled it. Ask loginwindow who.
sleep 120
why=$(/usr/bin/log show --last 3m --style compact --predicate 'process == "loginwindow"' 2>/dev/null |
  grep 'final Title:' | tail -1 | sed -E 's/.*final Title: //' | cut -c1-200)
log "restart cancelled: ${why:-no reason in the loginwindow log}"
# Claude was quit for nothing: bring it back so threads keep working. Launching
# an app takes the input queue like any automation (claude-control lock).
if ! pgrep -x Claude > /dev/null && t=$("$HOME/.hammerspoon/bin/claude-control" lock "nightly-restart"); then
  open -a Claude
  "$HOME/.hammerspoon/bin/claude-control" done "${t#granted }"
fi
