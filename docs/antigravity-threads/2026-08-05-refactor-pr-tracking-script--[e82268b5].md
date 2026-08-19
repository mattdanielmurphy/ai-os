---
title: "Refactor PR Tracking Script"
date: "2026-08-05"
conversation_id: "e82268b5-2fd2-417c-bb85-12ddb2a0a310"
source: "antigravity"
---

# Refactor PR Tracking Script

## User

Rewrite `/Users/matt/projects/ai-os/scripts/check_merged_prs.py` to filter out PRs in your own repositories.

Requirements:
1. Fetch current authenticated username using `gh api user --jq .login` (e.g., `mattdanielmurphy`).
2. Search merged PRs globally using `gh search prs --author "@me" --merged --json repository,number,title,url,closedAt`.
3. Filter PRs so that ONLY PRs submitted to EXTERNAL repos (where `repository['nameWithOwner']` does NOT start with `mattdanielmurphy/` / current owner) are considered bounty/external PR fulfillments.
4. Also format the PR key in `notified_prs.json` as `repo_full_name#pr_number` (e.g. `external-org/bounty-repo#42`) instead of just PR number, so PR numbers don't clash across different repos.
5. Make sure the script runs smoothly, has CLI args `--quiet` and `--force-check`, and is executable (`chmod +x`).

---

## Assistant

Created At: 2026-08-05T16:57:08-06:00
Completed At: 2026-08-05T16:57:08-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/check_merged_prs.py`
Total Lines: 65
Total Bytes: 2076
Showing lines 1 to 65
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import json
2: import subprocess
3: import argparse
4: import sys
5: import os
6: from datetime import datetime
7: 
8: STATE_FILE = "/Users/matt/.config/ai-os/notified_prs.json"
9: NOTIFY_SCRIPT = "/Users/matt/projects/ai-os/scripts/photon_notify.py"
10: 
11: def load_state():
12:     if os.path.exists(STATE_FILE):
13:         with open(STATE_FILE, 'r') as f:
14:             return set(json.load(f))
15:     return set()
16: 
17: def save_state(notified_prs):
18:     with open(STATE_FILE, 'w') as f:
19:         json.dump(list(notified_prs), f)
20: 
21: def get_merged_prs():
22:     try:
23:         # Get PRs authored by @me, state merged
24:         result = subprocess.run(
25:             ["gh", "pr", "list", "--author", "@me", "--state", "merged", "--json", "number,title,url,mergedAt"],
26:             capture_output=True, text=True, check=True
27:         )
28:         return json.loads(result.stdout)
29:     except Exception as e:
30:         print(f"Error fetching PRs: {e}", file=sys.stderr)
31:         return []
32: 
33: def main():
34:     parser = argparse.ArgumentParser(description="Check for merged GitHub PRs.")
35:     parser.add_argument("--quiet", action="store_true", help="Don't print unless new PRs found.")
36:     parser.add_argument("--force-check", action="store_true", help="Force check regardless of state (though currently logic is simple).")
37:     args = parser.parse_args()
38: 
39:     notified_prs = load_state()
40:     prs = get_merged_prs()
41:     
42:     new_prs = [pr for pr in prs if str(pr['number']) not in notified_prs]
43: 
44:     if not new_prs:
45:         if not args.quiet:
46:             print("No new merged PRs found.")
47:         return
48: 
49:     for pr in new_prs:
50:         msg = f"🎉 PR Merged: #{pr['number']} - {pr['title']} ({pr['url']})"
51:         if not args.quiet:
52:             print(f"Sending notification: {msg}")
53:         
54:         # Call notify script
55:         try:
56:             subprocess.run(["python3", NOTIFY_SCRIPT, msg], check=True)
57:             notified_prs.add(str(pr['number']))
58:         except Exception as e:
59:             print(f"Failed to send notification for PR #{pr['number']}: {e}", file=sys.stderr)
60: 
61:     save_state(notified_prs)
62: 
63: if __name__ == "__main__":
64:     main()
65: 
The above content shows the entire, complete file contents of the requested file.

---
