#!/usr/bin/env bash
# triage-launcher.sh — Superwhisper → ai-os triage launcher.
# Copy to ~/projects/ai-os/bin/triage-launcher.sh (or run straight from here).
# Fired by a superwhisper Command (script action). Receives the transcribed text in one of
# several ways (args / stdin / clipboard) and hands it to scripts/triage_router.py.
# Built & validated 2026-08-11. See also: references/triage-router-notes.md
set -u

QUERY=""

# 1) superwhisper's native shell action usually passes the transcript as args ($1, $2...).
if [ "$#" -gt 0 ]; then
  QUERY="$*"
fi

# 2) Fall back to stdin (some integrations pipe the text in).
if [ -z "$QUERY" ] && [ ! -t 0 ]; then
  QUERY="$(cat)"
fi

# 3) Last resort: pull the clipboard.
if [ -z "$QUERY" ]; then
  QUERY="$(osascript -e 'the clipboard as text' 2>/dev/null)"
fi

QUERY="$(printf '%s' "$QUERY" | awk '{$1=$1};1')"

if [ -z "$QUERY" ]; then
  echo "triage-launcher: no query captured."
  exit 1
fi

# Strip a leading trigger phrase if spoken (case-insensitive).
# "ai os open the music"  ->  "open the music"
TRIGGERS=("ai os" "ai-os" "aiyos" "a i o s" "dispatch" "triage")
for t in "${TRIGGERS[@]}"; do
  if echo "$QUERY" | grep -qiE "^${t// /[ ]}[ ,:]*"; then
    QUERY="$(echo "$QUERY" | sed -E "s/^${t// /[ ]}[ ,:]*//I" | awk '{$1=$1};1')"
    echo "triage-launcher: trigger '${t}' stripped. forwarding: ${QUERY}"
    break
  fi
done

echo "triage-launcher: → ${QUERY}"
exec python3 /Users/matt/projects/ai-os/scripts/triage_router.py "$QUERY"
