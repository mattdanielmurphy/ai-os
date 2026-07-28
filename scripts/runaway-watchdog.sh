#!/bin/bash
# Runaway Subagent Watchdog
# Detects and kills runaway subagent spawning (e.g. 81+ subagents from a userscript request).
# Runs as a cron job every 2 minutes.
#
# Detection criteria (any triggers alarm):
#   - More than 15 claude --bare --model processes (normal is 0-3)
#   - More than 10 tmux sessions containing "subagent" in name
#
# On alarm: kills all recently-spawned subagent processes, logs the event,
# and sends a desktop notification.

set -euo pipefail

ALARM=false
REASON=""
LOG_FILE="$HOME/projects/ai-os/agent-logs/runaway-events.log"
THRESHOLD_CLAUDE_BARE=15
THRESHOLD_SUBAGENT_TMUX=10
THRESHOLD_LANGUAGE_SERVER_AGENTS=8  # More than 8 claude procs from language_server = runaway

# Count claude --bare processes (the ones with a model flag = spawned by subagent.py)
CLAUDE_BARE_COUNT=$(pgrep -f "claude.*--bare.*--model" 2>/dev/null | wc -l | tr -d ' ')

# Count tmux sessions with 'subagent' in name (includes 'subagents' + others)
SUBAGENT_TMUX_COUNT=$(tmux list-sessions 2>/dev/null | grep -i subagent | wc -l | tr -d ' ')

# Detect runaway
if [ "$CLAUDE_BARE_COUNT" -ge "$THRESHOLD_CLAUDE_BARE" ] 2>/dev/null; then
  ALARM=true
  REASON="claude --bare --model processes: $CLAUDE_BARE_COUNT (threshold: $THRESHOLD_CLAUDE_BARE)"
elif [ "$SUBAGENT_TMUX_COUNT" -ge "$THRESHOLD_SUBAGENT_TMUX" ] 2>/dev/null; then
  ALARM=true
  REASON="subagent tmux sessions: $SUBAGENT_TMUX_COUNT (threshold: $THRESHOLD_SUBAGENT_TMUX)"
elif [ "$CLAUDE_BARE_COUNT" -ge "$THRESHOLD_LANGUAGE_SERVER_AGENTS" ] 2>/dev/null; then
  # More aggressive detection: even 8 claude procs is abnormal outside of Hermes
  ALARM=true
  REASON="language_server subagent spike: $CLAUDE_BARE_COUNT claude procs (threshold: $THRESHOLD_LANGUAGE_SERVER_AGENTS)"
fi

if [ "$ALARM" = false ]; then
  exit 0
fi

# Log the event and kill recent spawns
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
mkdir -p "$(dirname "$LOG_FILE")"

{
  echo "=== RUNAWAY DETECTED: $TIMESTAMP ==="
  echo "Reason: $REASON"
  echo "Claude bare count: $CLAUDE_BARE_COUNT"
  echo "Subagent tmux count: $SUBAGENT_TMUX_COUNT"
  echo "--- Killing recently spawned claude processes ---"
  
  # Kill claude --bare processes that have been running less than 10 minutes
  # (these are new spawns from the runaway; long-running ones are legitimate)
  for pid in $(pgrep -f "claude.*--bare.*--model" 2>/dev/null); do
    etime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
    if [ -z "$etime" ]; then
      continue
    fi
    # Parse elapsed time: formats like "01:23" (1m23s) or "02:01:45" (2h1m45s)
    if echo "$etime" | grep -qE '^[0-9]+:[0-9]+:[0-9]+$'; then
      # Hours:Minutes:Seconds - more than 10 minutes
      hours=$(echo "$etime" | cut -d: -f1)
      # Remove leading zeros
      hours=$((10#$hours + 0 2>/dev/null || echo 0))
      if [ "$hours" -ge 1 ] 2>/dev/null; then
        # Running for 1+ hours, skip
        continue
      fi
    elif echo "$etime" | grep -qE '^[0-9]+:[0-9]+$'; then
      # Minutes:Seconds format
      minutes=$(echo "$etime" | cut -d: -f1)
      minutes=$((10#$minutes + 0 2>/dev/null || echo 0))
      if [ "$minutes" -ge 10 ] 2>/dev/null; then
        # Running for 10+ minutes, skip (legitimate)
        continue
      fi
    fi
    # Kill the recent spawn
    echo "  Killing claude --bare: pid=$pid (etime=$etime)"
    kill "$pid" 2>/dev/null || true
  done
  
  echo "--- Post-kill count ---"
  echo "Remaining: $(pgrep -f 'claude.*--bare.*--model' 2>/dev/null | wc -l)"
  echo "=== END ==="
} >> "$LOG_FILE" 2>&1

# Desktop notification
osascript -e "display notification \"Runaway subagent detected: $REASON\" with title \"⚠️ Runaway Watchdog\" subtitle \"Killed excess processes\"" 2>/dev/null || true

exit 0