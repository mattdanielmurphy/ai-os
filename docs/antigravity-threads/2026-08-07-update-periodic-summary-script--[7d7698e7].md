---
title: "Update Periodic Summary Script"
date: "2026-08-07"
conversation_id: "7d7698e7-1977-4c7a-93b2-0d2e900473b0"
source: "antigravity"
---

# Update Periodic Summary Script

## User

Please create and write the complete updated python script at both `/Users/matt/projects/jules-burner/src/scripts/periodic_summary_notifier.py` and `/Users/matt/projects/jules-burner/scripts/periodic_summary_notifier.py`:

```python
#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import json
import glob
import re
import urllib.request
import urllib.error

NOTIFY_SCRIPT = os.path.expanduser("~/projects/jules-burner/src/scripts/photon_notify.py")
if not os.path.exists(NOTIFY_SCRIPT):
    NOTIFY_SCRIPT = os.path.expanduser("~/projects/jules-burner/scripts/photon_notify.py")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_KEY:
    # Try reading from .env file
    env_path = os.path.expanduser("~/projects/jules-burner/.env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    OPENROUTER_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

def gather_raw_activity(hours=3):
    cutoff_ms = (time.time() - (hours * 3600)) * 1000
    prompts_dir = os.path.expanduser("~/projects/jules-burner/tmp/prompts")
    
    tasks = []
    if os.path.exists(prompts_dir):
        files = [f for f in glob.glob(prompts_dir + "/*.md") if os.path.getmtime(f) * 1000 >= cutoff_ms]
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read()
                    title_m = re.search(r"^# Task Specification:\s*(.+)$", content, re.M)
                    repo_m = re.search(r"- \*\*Target Repository\*\*:\s*(.+)$", content, re.M)
                    obj_m = re.search(r"## Objective & Description\s*\n([^\n]+)", content, re.M)
                    
                    title = title_m.group(1).strip() if title_m else "Task Execution"
                    repo = repo_m.group(1).strip() if repo_m else "Unknown Repo"
                    obj = obj_m.group(1).strip() if 
<truncated 3164 bytes>
"Here is the raw activity data for the last {raw_data['window_hours']} hours:\n{json.dumps(raw_data, indent=2)}"

    payload = {
        "model": "deepseek/deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            summary = res_body["choices"][0]["message"]["content"].strip()
            return summary
    except Exception as e:
        print(f"Warning: OpenRouter API request failed ({e}). Using basic fallback.", file=sys.stderr)
        return f"📊 {raw_data['window_hours']}h Work Summary:\n• Dispatched {raw_data['tasks_dispatched_in_window']} task(s).\n• Merged PRs: {len(raw_data['merged_prs'])} external bounty PR(s)."

def main():
    hours = 3
    if len(sys.argv) > 2 and sys.argv[1] == "--hours":
        try:
            hours = int(sys.argv[2])
        except ValueError:
            pass

    raw_data = gather_raw_activity(hours)
    report_text = generate_plain_english_summary(raw_data)

    print(f"Summary output:\n{report_text}")

    if "--test" not in sys.argv and os.path.exists(NOTIFY_SCRIPT):
        try:
            subprocess.run(["python3", NOTIFY_SCRIPT, report_text], check=True)
        except Exception as e:
            print(f"Failed to send notification: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
```
Make both executable (`chmod +x`).

---

## Assistant

Created At: 2026-08-06T20:20:24-06:00
Completed At: 2026-08-06T20:20:24-06:00
Created file file:///Users/matt/projects/jules-burner/src/scripts/periodic_summary_notifier.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-06T20:20:29-06:00
Completed At: 2026-08-06T20:20:29-06:00
Created file file:///Users/matt/projects/jules-burner/scripts/periodic_summary_notifier.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-06T20:20:30-06:00
Completed At: 2026-08-06T20:20:30-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-06T20:20:31-06:00
Completed At: 2026-08-06T20:20:31-06:00
Message sent to "a50c7f96-5f08-4c4e-82e3-d475dc73889b".

The `periodic_summary_notifier.py` script has been successfully created and saved at both requested locations:
- [/Users/matt/projects/jules-burner/src/scripts/periodic_summary_notifier.py](file:///Users/matt/projects/jules-burner/src/scripts/periodic_summary_notifier.py)
- [/Users/matt/projects/jules-burner/scripts/periodic_summary_notifier.py](file:///Users/matt/projects/jules-burner/scripts/periodic_summary_notifier.py)

Both files have been made executable.

---
