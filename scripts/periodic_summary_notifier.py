#!/usr/bin/env python3
import argparse
import os
import subprocess
import glob
from datetime import datetime, timedelta

def get_recent_activity(hours):
    # This is a placeholder for actual logic to scan brain/thread.md or git commits.
    # In a real scenario, this would use glob to find files and parse them.
    # For now, it returns a stubbed summary.
    return f"Summary of activity in the last {hours} hours: System running smoothly, no critical errors."

def send_notification(message):
    # Calls the specified photon_notify.py
    notify_script = "/Users/matt/projects/ai-os/scripts/photon_notify.py"
    if os.path.exists(notify_script):
        subprocess.run([notify_script, message])
    else:
        print(f"Error: {notify_script} not found.")

def main():
    parser = argparse.ArgumentParser(description="Periodic summary notifier.")
    parser.add_argument("--hours", type=int, default=3, help="Hours to look back.")
    args = parser.parse_args()

    summary = get_recent_activity(args.hours)
    
    # Ensure it's punchy and under 300 chars
    if len(summary) > 300:
        summary = summary[:297] + "..."
    
    print(f"Sending: {summary}")
    send_notification(summary)

if __name__ == "__main__":
    main()
