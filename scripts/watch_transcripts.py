#!/usr/bin/env python3
import os
import time
import argparse
import subprocess
from pathlib import Path

# Path to the brain directory
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
GEN_SCRIPT = Path("/Users/matt/projects/ai-os/scripts/gen_conversation_md.py")

def get_active_convs():
    """Finds all conversation IDs with a transcript.jsonl file."""
    active_convs = {}
    if not BRAIN_DIR.exists():
        return active_convs

    for conv_dir in BRAIN_DIR.iterdir():
        if conv_dir.is_dir():
            transcript_path = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript_path.exists():
                active_convs[conv_dir.name] = transcript_path.stat().st_mtime
    return active_convs

def process_updates(last_mtimes):
    """Checks for updates and triggers re-rendering."""
    current_convs = get_active_convs()
    
    for conv_id, mtime in current_convs.items():
        if conv_id not in last_mtimes or mtime > last_mtimes[conv_id]:
            print(f"Update detected in {conv_id}. Re-rendering...")
            try:
                subprocess.run(["python3", str(GEN_SCRIPT), conv_id], check=True)
                print(f"Successfully re-rendered {conv_id}.")
            except subprocess.CalledProcessError as e:
                print(f"Error re-rendering {conv_id}: {e}")
            last_mtimes[conv_id] = mtime
            
    # Clean up removed convs
    for conv_id in list(last_mtimes.keys()):
        if conv_id not in current_convs:
            del last_mtimes[conv_id]

def main():
    parser = argparse.ArgumentParser(description="Watch conversation transcripts and auto-render markdown.")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous loop")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    last_mtimes = get_active_convs()

    if args.once:
        process_updates(last_mtimes)
    elif args.daemon:
        print(f"Watching {BRAIN_DIR} for changes...")
        try:
            while True:
                process_updates(last_mtimes)
                time.sleep(2)
        except KeyboardInterrupt:
            print("Stopping...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
