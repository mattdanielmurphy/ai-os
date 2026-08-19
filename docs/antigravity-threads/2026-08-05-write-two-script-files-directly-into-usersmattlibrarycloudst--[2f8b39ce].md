---
title: "Write two script files directly into `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/scripts/` using `write_to_file`:"
date: "2026-08-05"
conversation_id: "2f8b39ce-238b-4923-b2e4-2f75e1d81292"
source: "antigravity"
---

# Write two script files directly into `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/scripts/` using `write_to_file`:

## User

Write two script files directly into `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/scripts/` using `write_to_file`:

1. `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/scripts/photon_notify.py`:
```python
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def send_photon_message(text: str, recipient: str = "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]") -> bool:
    project_id = os.getenv("PHOTON_PROJECT_ID", "[REDACTED_SECRET:PHOTON_PROJECT_ID]")
    project_secret = os.getenv("PHOTON_PROJECT_SECRET", "[REDACTED_SECRET:PHOTON_PROJECT_SECRET]")

    escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    escaped_recipient = recipient.replace('\\', '\\\\').replace("'", "\\'")

    node_script = """
import { Spectrum, text } from 'spectrum-ts';
import { imessage } from 'spectrum-ts/providers/imessage';

async function send() {
    try {
        const app = await Spectrum({
            projectId: '""" + project_id + """',
            projectSecret: '""" + project_secret + """',
            providers: [imessage.config()],
            options: { flattenGroups: true },
            telemetry: false,
        });
        const im = imessage(app);
        const space = await im.space.create('""" + escaped_recipient + """');
        await space.send(text('""" + escaped_text + """'));
        await app.stop();
        console.log('Success');
        process.exit(0);
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
}

send();
"""

    cwd = "/home/ubuntu/projects/jules-burner"
    bun_bin = "/home/ubuntu/.bun/bin/bun"
    
    try:
        result = subprocess.run(
            [bun_bin, "eval", node_script],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"Message sent successfully to {recipient}")
            return True
        else:
            print(f"Failed to send messag
<truncated 1688 bytes>
utput=True, text=True, check=True
        )
        all_prs = json.loads(result.stdout)
        
        external_prs = []
        for pr in all_prs:
            repo_full = pr.get("repository", {}).get("nameWithOwner", "")
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
        if pr_id not in notified_prs or args.force_check:
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

---
