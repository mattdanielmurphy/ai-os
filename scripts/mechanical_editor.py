#!/usr/bin/env python3
import sys
import argparse
import subprocess
from pathlib import Path

def list_available_models(config_path):
    try:
        print("Available Mechanical Editor profiles:")
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("- model_name:"):
                    name = s.split(":", 1)[1].strip()
                    # Keep fallback implementations hidden from user select list
                    if not name.endswith("-or"):
                        print(f"  • {name}")
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Mechanical Editor utilizing Claude Code CLI")
    parser.add_argument("filepath", nargs="?", help="Path to the file to modify")
    parser.add_argument("spec", nargs="?", help="Technical spec describing the modifications")
    parser.add_argument("--model", default="claude-sonnet-gem-2.5-flash", help="Target LiteLLM mapped model name")
    parser.add_argument("-l", "--list", action="store_true", help="List available models from LiteLLM config")
    
    args = parser.parse_args()
    config_path = Path("/Users/matt/litellm/config.yaml")
    
    if args.list:
        list_available_models(config_path)
        sys.exit(0)
        
    if not args.filepath or not args.spec:
        parser.error("filepath and spec are required unless using --list")
        
    filepath = Path(args.filepath).resolve()
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    prompt = f"Apply this technical spec: '{args.spec}' to the file: '{filepath}'"
    
    cmd = [
        "claude",
        "--model",
        args.model,
        "-p",
        prompt,
        "--dangerously-skip-permissions"
    ]
    
    print(f"[Mechanical Editor] Delegating to Claude Code using model profile '{args.model}' for {filepath}...", flush=True)
    
    try:
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