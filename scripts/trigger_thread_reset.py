#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def copy_to_clipboard(text: str):
    try:
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)
        return False

def generate_handoff():
    project_root = Path(__file__).resolve().parent.parent
    handoff_script = project_root / "scripts" / "context_handoff.py"
    if handoff_script.exists():
        print("Generating context handoff...")
        res = subprocess.run([sys.executable, str(handoff_script)], cwd=str(project_root), capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout.strip())
        else:
            print(f"Warning: context_handoff.py returned exit code {res.returncode}: {res.stderr.strip()}")
    else:
        print("Warning: context_handoff.py not found.")

def trigger_antigravity_reset():
    applescript = '''
    tell application "Antigravity" to activate
    delay 0.4
    tell application "System Events"
        keystroke "o" using {command down, shift down}
        delay 0.5
        keystroke "v" using {command down}
    end tell
    '''
    try:
        print("Triggering Antigravity thread reset via AppleScript...")
        subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True, check=True)
        print("Antigravity thread reset triggered successfully (Cmd+Shift+O sent, /resume pasted).")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error triggering Antigravity reset via osascript: {e.stderr.strip()}", file=sys.stderr)
        return False

def main():
    print("=== Antigravity Thread Reset Trigger ===")
    generate_handoff()
    if copy_to_clipboard("/resume"):
        print("Copied '/resume' to macOS clipboard.")
    trigger_antigravity_reset()

if __name__ == "__main__":
    main()
