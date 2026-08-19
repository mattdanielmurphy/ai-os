---
title: "GitHub PR Notification Script"
date: "2026-08-05"
conversation_id: "e148e744-b7b0-4c11-a8c7-d70844da82c2"
source: "antigravity"
---

# GitHub PR Notification Script

## User

Create `/Users/matt/projects/ai-os/scripts/check_merged_prs.py`.

Requirements:
1. This script checks merged GitHub PRs created by the user (or Jules PRs) using `gh pr list --author "@me" --state merged --json number,title,url,mergedAt`.
2. Keep track of already notified PRs in a state file at `/Users/matt/.config/ai-os/notified_prs.json` (create dir if missing).
3. If new merged PRs are found:
   - Construct a clear, concise SMS message listing the PR title(s) and URL(s) / number(s). E.g.: "🎉 PR Merged: #18 - feat: ... (https://github.com/...)"
   - Call `/Users/matt/projects/ai-os/scripts/photon_notify.py` to send the notification to your phone!
   - Update `notified_prs.json` so duplicate notifications aren't sent.
4. Add CLI arguments: `--quiet` (don't print unless new PRs found) or `--force-check`.
5. Make sure the script is robust and prints clear logs.

---

## Assistant

Created At: 2026-08-05T16:55:30-06:00
Completed At: 2026-08-05T16:55:30-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T16:55:35-06:00
Completed At: 2026-08-05T16:55:35-06:00
Created file file:///Users/matt/projects/ai-os/scripts/check_merged_prs.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T16:55:36-06:00
Completed At: 2026-08-05T16:55:36-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T16:55:37-06:00
Completed At: 2026-08-05T16:55:37-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

The script `/Users/matt/projects/ai-os/scripts/check_merged_prs.py` has been created and set as executable. It fulfills all your requirements, including state management for notified PRs and support for `--quiet` and `--force-check` CLI arguments.

---
