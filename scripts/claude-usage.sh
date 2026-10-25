#!/usr/bin/env bash
# Claude Code usage from local logs (~/.claude/projects) via ccusage.
# Costs are API-equivalent dollars, not what the subscription charges.
# Usage: scripts/claude-usage.sh [days=7]
# Plan meter (% of 5-hour / weekly limit) is not in the logs: see claude.ai
# Settings > Usage, or run scripts/claude_pace.py (weekly % + Opus/Sonnet call via CodexBar).
# Cloud sessions (e.g. the Projects coordinator) are not logged locally.
set -euo pipefail
days="${1:-7}"
since="$(date -v-"${days}"d +%Y%m%d)"
echo "== Claude daily, by model (since $since) =="
bunx ccusage@latest claude daily --since "$since" --breakdown --compact
echo
echo "== 5-hour blocks (recent) =="
bunx ccusage@latest claude blocks --recent --compact
echo
echo "== Cost by repo (worktrees folded in) =="
bunx ccusage@latest claude session --since "$since" --json 2>/dev/null | python3 -c '
import json,sys,re,collections
agg=collections.Counter()
for s in json.load(sys.stdin)["sessions"]:
    p=re.sub(r"--claude-worktrees-.*|-scratch-workspaces-.*","",s["projectPath"]).replace("-Users-matt-","")
    agg[p]+=s["totalCost"]
for p,c in agg.most_common(12): print(f"  ${c:8.2f}  {p}")
'
