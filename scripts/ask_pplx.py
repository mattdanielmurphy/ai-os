#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys

EXCLUDES = [
    "node_modules", ".env", ".git", "dist", "build", "*.lock", 
    "package-lock.json", "yarn.lock", "__pycache__", "*.pyc", 
    "venv", ".venv", ".next"
]

def is_excluded(d):
    for exc in EXCLUDES:
        if exc.replace("*", "") in d:
            return True
    return False

def get_files():
    files = []
    for root, dirs, filenames in os.walk('.'):
        dirs[:] = [d for d in dirs if not is_excluded(d)]
        for f in filenames:
            if not is_excluded(f):
                path = os.path.join(root, f)
                if os.path.isfile(path) and not os.path.islink(path):
                    try:
                        with open(path, "tr", encoding="utf-8") as file:
                            file.read(1024)
                        files.append(path)
                    except Exception:
                        pass
    return sorted(files)

def estimate_tokens(file_path):
    try:
        return os.path.getsize(file_path) / 4
    except OSError:
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--include", nargs='+', type=int)
    args = parser.parse_args()

    files = get_files()

    if args.include:
        selected_files = [files[i-1] for i in args.include if 1 <= i <= len(files)]
        cmd = ["code2prompt"] + selected_files
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        with open("/tmp/context.md", "w") as f:
            f.write(output)
        print(f"Run the `ask_perplexity` MCP tool with message: '{args.prompt}' and files: ['/tmp/context.md']")
    else:
        tokens = sum(estimate_tokens(f) for f in files)
        
        if tokens > 100000:
            print("Context too large (> 100k tokens). Run `ask_pplx.py 'prompt' --include <numbers>`")
            for i, f in enumerate(files):
                print(f"{i+1}: {f} (~{int(estimate_tokens(f))} tokens)")
        else:
            cmd = ["code2prompt", "."]
            for exc in EXCLUDES:
                cmd.extend(["--exclude", exc])
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
            with open("/tmp/context.md", "w") as f:
                f.write(output)
            print(f"Run the `ask_perplexity` MCP tool with message: '{args.prompt}' and files: ['/tmp/context.md']")

if __name__ == "__main__":
    main()
