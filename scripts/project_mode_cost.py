#!/usr/bin/env python3
"""API-equivalent cost of Claude Projects ("project mode") threads vs other Claude Code use.

A local session counts as project mode when it called any mcp__hearthbot__ tool
(only Projects thread sessions have those). Costs come from ccusage.
The cloud coordinator is not in local logs, so it is not counted here.
Usage: scripts/project_mode_cost.py [days=7]
"""
import glob, json, os, subprocess, sys, collections, time
from datetime import date, timedelta

days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
since = (date.today() - timedelta(days=days)).strftime("%Y%m%d")

# Each thread message (Matt's or a thread reply) wakes the cloud coordinator once.
# Rough per-wake cost on Opus 5.5 prices ($0.20/MTok cache read, $8/MTok 1h cache
# write, $20/MTok output) with a 100-200k mostly-cached coordinator context.
COORD_PER_WAKE = (0.04, 0.08)
COORD_COLD_REWRITE = 1.0   # first wake after the cache expires re-writes ~150k tokens

def scan(path):
    """(is_project_mode, human_messages, replies) for one transcript."""
    proj, human, replies = False, 0, 0
    with open(path, errors="ignore") as f:
        for line in f:
            try:
                msg = json.loads(line).get("message") or {}
            except ValueError:
                continue
            c = msg.get("content")
            if msg.get("role") == "user":
                txt = c if isinstance(c, str) else " ".join(
                    x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                if txt.lstrip().startswith("<wake") and 'from="human"' in txt:
                    human += 1
            elif msg.get("role") == "assistant" and isinstance(c, list):
                for x in c:
                    n = x.get("name", "") if x.get("type") == "tool_use" else ""
                    if n.startswith("mcp__hearthbot__"):
                        proj = True
                        replies += n == "mcp__hearthbot__reply"
    return proj, human, replies

cutoff = time.time() - days * 86400
project_ids, human_msgs, thread_replies = set(), 0, 0
for p in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    proj, h, r = scan(p)
    if proj:
        project_ids.add(os.path.basename(p)[:-6])
        if os.path.getmtime(p) >= cutoff:
            human_msgs += h; thread_replies += r

out = subprocess.run(["bunx", "ccusage@latest", "claude", "session", "--since", since, "--json"],
                     capture_output=True, text=True, check=True).stdout
sessions = json.loads(out)["sessions"]

tot = collections.Counter(); models = collections.defaultdict(collections.Counter); n = collections.Counter()
for s in sessions:
    k = "project mode" if s["sessionId"] in project_ids else "other Claude Code"
    tot[k] += s["totalCost"]; n[k] += 1
    for m in s.get("modelBreakdowns", []):
        models[k][m["modelName"]] += m["cost"]

grand = sum(tot.values()) or 1
print(f"Claude Code, API-equivalent cost since {since} (local logs only)")
for k in ("project mode", "other Claude Code"):
    print(f"  {k:18s} ${tot[k]:8.2f}  {tot[k]/grand:5.1%}  ({n[k]} sessions)")
    for m, c in models[k].most_common(3):
        print(f"      {m:28s} ${c:8.2f}")
print(f"  {'total':18s} ${grand:8.2f}")
wakes = human_msgs + thread_replies
lo, hi = wakes * COORD_PER_WAKE[0], wakes * COORD_PER_WAKE[1] + days * 4 * COORD_COLD_REWRITE
print(f"\nCloud coordinator (estimate, not in local logs): {wakes} thread messages "
      f"({human_msgs} yours, {thread_replies} thread replies) = about ${lo:.0f}-${hi:.0f}")
print("Threads that ran in the cloud are not counted either, so the real figure is higher.")
