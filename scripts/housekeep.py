#!/usr/bin/env python3
import os
import sys
import json
import datetime
import subprocess

def run_cmd(args, check=True):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return res.stdout.strip(), res.returncode
    except subprocess.CalledProcessError as e:
        print(f"Command {' '.join(args)} failed: {e.stderr}", file=sys.stderr)
        if check:
            sys.exit(e.returncode)
        return "", e.returncode

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/housekeep.py --description <kebab-case-description>", file=sys.stderr)
        sys.exit(1)

    description = ""
    # Parse args manually to avoid external dependencies
    file_path = ""
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--description" and i + 1 < len(sys.argv):
            description = sys.argv[i+1]
        elif sys.argv[i] == "--file" and i + 1 < len(sys.argv):
            file_path = sys.argv[i+1]

    if not description:
        print("Error: --description is required", file=sys.stderr)
        sys.exit(1)

    # 1. Read log content
    if file_path:
        print(f"Reading log content from {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            log_content = f.read().strip()
    else:
        print("Reading log content from stdin...")
        log_content = sys.stdin.read().strip()
    if not log_content:
        print("Error: Log content cannot be empty", file=sys.stderr)
        sys.exit(1)

    # 2. Find transcript pointer
    transcript_pointer = ""
    metadata_str = os.environ.get("ANTIGRAVITY_SOURCE_METADATA")
    if metadata_str:
        try:
            metadata = json.loads(metadata_str)
            conv_id = metadata.get("tool", {}).get("conversationId")
            if conv_id:
                paths = [
                    f"/Users/matt/.gemini/antigravity/brain/{conv_id}/.system_generated/logs/transcript.jsonl",
                    f"/Users/matt/.gemini/antigravity-ide/brain/{conv_id}/.system_generated/logs/transcript.jsonl",
                    f"/Users/matt/.gemini/antigravity-cli/brain/{conv_id}/.system_generated/logs/transcript.jsonl"
                ]
                for p in paths:
                    if os.path.exists(p):
                        transcript_pointer = f"\n\n[Full Transcript for this conversation](file://{p})\n"
                        break
        except Exception as e:
            print(f"Warning: Failed to parse metadata or locate transcript: {e}", file=sys.stderr)

    if transcript_pointer:
        log_content += transcript_pointer

    # 3. Create agent-logs/ directory if needed
    os.makedirs("agent-logs", exist_ok=True)

    # 4. Generate filename YYYY-MM-DD_HH-MM_<description>.md
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    filename = f"agent-logs/{timestamp}_{description}.md"

    # 5. Write log file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(log_content)
    print(f"Log written to {filename}")

    # 6. Run auto_commit.py
    # We stage the log file first
    run_cmd(["git", "add", filename])

    print("Running auto_commit.py...")
    # Run auto_commit.py (this stages other files and commits them all)
    stdout, code = run_cmd(["python3", "scripts/auto_commit.py"], check=False)
    print(stdout)
    if code != 0:
        print("Warning: auto_commit.py exited with non-zero status", file=sys.stderr)
        sys.exit(code)

    # Trigger background review asynchronously if transcript pointer exists
    if metadata_str:
        try:
            conv_id = json.loads(metadata_str).get("tool", {}).get("conversationId")
            if conv_id:
                t_path = f"/Users/matt/.gemini/antigravity/brain/{conv_id}/.system_generated/logs/transcript.jsonl"
                if os.path.exists(t_path):
                    print("Launching background review extractor...")
                    subprocess.Popen(["python3", "scripts/background_review.py", t_path, os.getcwd()])
        except Exception as e:
            print(f"Notice: background review trigger skipped ({e})", file=sys.stderr)

    print("Housekeeping finished successfully!")

if __name__ == "__main__":
    main()
