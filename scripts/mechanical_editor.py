#!/usr/bin/env python3
import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Mechanical Editor utilizing Claude Code CLI")
    parser.add_argument("filepath", help="Path to the file to modify")
    parser.add_argument("spec", help="Technical spec describing the modifications")
    parser.add_argument("--model", default="flash", help="The target model key (e.g. flash, pro, gemini-pro, gemini-flash)")
    args = parser.parse_args()
    
    filepath = Path(args.filepath).resolve()
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    model_map = {
        "flash": "claude-3-5-haiku-20241022",
        "deepseek-v4-flash": "claude-3-5-haiku-20241022",
        "deepseek-flash": "claude-3-5-haiku-20241022",
        "haiku": "claude-3-5-haiku-20241022",
        
        "pro": "claude-fable-5",
        "deepseek-v4-pro": "claude-fable-5",
        "deepseek-pro": "claude-fable-5",
        "fable": "claude-fable-5",
        
        "gemini-pro": "claude-3-opus-20240229",
        "gemini-2.5-pro": "claude-3-opus-20240229",
        "opus": "claude-3-opus-20240229",
        
        "gemini-flash": "claude-3-5-sonnet-latest",
        "gemini-2.5-flash": "claude-3-5-sonnet-latest",
        "sonnet": "claude-3-5-sonnet-latest"
    }
    
    requested_model = args.model.lower()
    anthropic_model = model_map.get(requested_model, "claude-3-5-haiku-20241022")
    
    prompt = f"Apply this technical spec: '{args.spec}' to the file: '{filepath}'"
    
    cmd = [
        "claude",
        "--model",
        anthropic_model,
        "-p",
        prompt,
        "--dangerously-skip-permissions"
    ]
    
    print(f"[Mechanical Editor] Delegating to Claude Code agent ({anthropic_model} -> mapped from {requested_model}) for {filepath}...", flush=True)
    
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
