#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title ai-os Triage Launcher
# @raycast.mode compact
# @raycast.packageName ai-os
#
# Optional parameters:
# @raycast.icon 🤖
# @raycast.argument1 { "type": "text", "placeholder": "Ask ai-os or give command...", "optional": false }

QUERY="$1"

if [ -z "$QUERY" ]; then
    echo "No query provided."
    exit 1
fi

# Route query through ai-os triage router
python3 /Users/matt/projects/ai-os/scripts/triage_router.py "$QUERY"
