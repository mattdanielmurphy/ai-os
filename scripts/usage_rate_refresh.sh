#!/bin/sh
# Refresh the usage-rate page data (run by launchd every 10 min).
cd "$(dirname "$0")/.." || exit 1
python3 scripts/usage_rate.py --json "$HOME/projects/pages/site/usage-rate/usage.json" >/dev/null
