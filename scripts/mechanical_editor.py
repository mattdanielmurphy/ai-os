#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: mechanical_editor.py <filepath> <spec>", file=sys.stderr)
        sys.exit(1)
        
    filepath = Path(sys.argv[1]).resolve()
    spec = sys.argv[2]
    
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    prompt = f"Apply this technical spec: '{spec}' to the file: '{filepath}'"
    
    cmd = [
        "claude",
        "-p",
        prompt,
        "--dangerously-skip-permissions"
    ]
    
    print(f"[Mechanical Editor] Delegating to Claude Code agent for {filepath}...", flush=True)
    
    try:
        # Redirect stdin from devnull to skip the 3-second stdin wait
        with open("/dev/null", "r") as devnull:
            result = subprocess.run(cmd, stdin=devnull, capture_output=True, text=True, check=True)
            print(result.stdout)
            print("Success: Mechanical Editor delegation completed.")
            sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Claude Code delegation:\nExit Code: {e.returncode}\nStderr:\n{e.stderr}\nStdout:\n{e.stdout}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
