#!/usr/bin/env bash
# bin/triage-launcher.sh
# Superwhisper -> ai-os triage launcher.
# Fired by a superwhisper Command (script action). It receives the transcribed
# text (which superwhisper passes in one of several ways) and hands it to
# scripts/triage_router.py for classification + routing.
#
# If a trigger phrase precedes the real query, we strip it so the prompt
# that reaches triage is clean (e.g. spoken "ai os open safari" -> "open safari").
set -u

QUERY=""

# 1) superwhisper's native shell action usually passes the transcript as args
#    ($1, $2, ...). Join them back into a single string.
if [ "$#" -gt 0 ]; then
  QUERY="$*"
fi

# 2) If empty, fall back to stdin (some integrations pipe the text in).
if [ -z "$QUERY" ] && [ ! -t 0 ]; then
  QUERY="$(cat)"
fi

# 3) If still empty, pull the clipboard as a last resort.
if [ -z "$QUERY" ]; then
  QUERY="$(osascript -e 'the clipboard as text' 2>/dev/null)"
fi

QUERY="$(printf '%s' "$QUERY" | awk '{$1=$1};1')"

if [ -z "$QUERY" ]; then
  echo "triage-launcher: no query captured."
  exit 1
fi

# Strip a leading trigger phrase if the user spoke one (case-insensitive).
# Example: "ai os open the music"  ->  "open the music"
TRIGGERS=("ai os" "ai-os" "aiyos" "a i o s" "dispatch" "triage")
for t in "${TRIGGERS[@]}"; do
  # shell-agnostic lowercase compare
  if echo "$QUERY" | grep -qiE "^${t// /[ ]}[ ,:]*"; then
    QUERY="$(echo "$QUERY" | sed -E "s/^${t// /[ ]}[ ,:]*//I" | awk '{$1=$1};1')"
    echo "triage-launcher: trigger '${t}' stripped. forwarding: ${QUERY}"
    break
  fi
done

echo "triage-launcher: → ${QUERY}"
exec python3 /Users/matt/projects/ai-os/scripts/triage_router.py "$QUERY"
