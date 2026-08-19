---
title: "Overwrite `/Users/matt/projects/ai-os/scripts/check_merged_prs.py` with this exact implementation:"
date: "2026-08-05"
conversation_id: "5a334edd-9069-428e-82b4-cb58a6ba303e"
source: "antigravity"
---

# Overwrite `/Users/matt/projects/ai-os/scripts/check_merged_prs.py` with this exact implementation:

## User

Overwrite `/Users/matt/projects/ai-os/scripts/check_merged_prs.py` with this exact implementation:

```python
#!/usr/bin/env python3
import json
import subprocess
import argparse
import sys
import os

STATE_FILE = "/Users/matt/.config/ai-os/notified_prs.json"
NOTIFY_SCRIPT = "/Users/matt/projects/ai-os/scripts/photon_notify.py"

def get_current_user():
    try:
        res = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        print(f"Error fetching current user: {e}", file=sys.stderr)
        return None

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_state(notified_prs):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(list(notified_prs), f)

def get_external_merged_prs(username):
    try:
        # Search all merged PRs authored by @me across GitHub
        result = subprocess.run(
            ["gh", "search", "prs", "--author", "@me", "--merged", "--json", "repository,number,title,url,closedAt"],
            capture_output=True, text=True, check=True
        )
        all_prs = json.loads(result.stdout)
        
        external_prs = []
        for pr in all_prs:
            repo_full = pr.get("repository", {}).get("nameWithOwner", "")
            # Filter out PRs created on user's own repositories
            if username and repo_full.startswith(f"{username}/"):
                continue
            external_prs.append(pr)
            
        return external_prs
    except Exception as e:
        print(f"Error fetching external merged PRs: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="Check for merged bounty/external GitHub PRs.")
    parser.add_argument("--quiet", action="store_true", help="Don't print unless new PRs found.")
    parser.add_argument("--force-check", action="store_true", help="Force check regardless of state.")
    args = parser.parse_args()

    username = get_current_user()
    notified_prs = load_state()
    prs = get_external_merged_prs(username)

    new_prs = []
    for pr in prs:
        repo_name = pr.get("repository", {}).get("nameWithOwner", "")
        pr_id = f"{repo_name}#{pr['number']}"
        if pr_id not in notified_prs or args.force-check:
            new_prs.append((pr_id, pr))

    if not new_prs:
        if not args.quiet:
            print("No new external merged bounty PRs found.")
        return

    for pr_id, pr in new_prs:
        repo_name = pr.get("repository", {}).get("nameWithOwner", "")
        msg = f"🎉 Bounty PR Pulled! {repo_name}#{pr['number']} - {pr['title']} ({pr['url']})"
        if not args.quiet:
            print(f"Sending notification: {msg}")
        
        try:
            subprocess.run(["python3", NOTIFY_SCRIPT, msg], check=True)
            notified_prs.add(pr_id)
        except Exception as e:
            print(f"Failed to send notification for {pr_id}: {e}", file=sys.stderr)

    save_state(notified_prs)

if __name__ == "__main__":
    main()
```

Make sure it is executable (`chmod +x`).

---
