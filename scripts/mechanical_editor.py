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
    parser.add_argument("filepath", nargs="?", help="Path to the file to modify, or a technical spec if --spec is not provided")
    parser.add_argument("--spec", help="Technical spec describing the modifications")
    parser.add_argument("--model", default="deepseek-v4-flash-low", help="Target LiteLLM mapped model name")
    parser.add_argument("-l", "--list", action="store_true", help="List available models from LiteLLM config")

    args = parser.parse_args()
    config_path = Path("/Users/matt/litellm/config.yaml")

    if args.list:
        list_available_models(config_path)
        sys.exit(0)

    filepath_arg = None
    spec_arg = None

    if args.filepath and not args.spec:
        # Case 1: filepath provided, spec not provided
        potential_path = Path(args.filepath)
        if potential_path.exists():
            parser.error('A technical spec is required when editing an existing file.')
        else:
            spec_arg = args.filepath
            filepath_arg = None # Ensure filepath_arg is None if it's treated as a spec
    elif args.filepath and args.spec:
        # Case 2: both provided
        filepath_arg = args.filepath
        spec_arg = args.spec
    elif not args.filepath and args.spec:
        # Case 2.5: only spec provided without filepath (handled by filepath_arg = None and spec_arg = args.spec)
        spec_arg = args.spec
    elif not args.filepath and not args.spec:
        # Case 3: neither provided
        parser.error('A technical spec or task description is required.')

    if filepath_arg:
        filepath = Path(filepath_arg).resolve()
        if not filepath.exists():
            print(f"Error: File {filepath} does not exist.", file=sys.stderr)
            sys.exit(1)
        prompt = f"Apply this technical spec: '{spec_arg}' to the file: '{filepath}'"
    else:
        prompt = spec_arg

    cmd = [
        "claude",
        "--model",
        args.model,
        "-p",
        prompt,
        "--dangerously-skip-permissions"
    ]

    target_desc = filepath_arg if filepath_arg else "workspace"
    print(f"[Mechanical Editor] Delegating to Claude Code using model profile '{args.model}' for {target_desc}...", flush=True)

    # Define paths for rules files
    gemini_md = Path.home() / ".gemini" / "GEMINI.md"
    claude_md = Path.home() / ".claude" / "CLAUDE.md"

    # Pre-check: auto-recover from hard crashes where .bak exists but original doesn't
    for md_path in [gemini_md, claude_md]:
        bak_path = md_path.with_name(md_path.name + ".bak")
        if bak_path.exists() and not md_path.exists():
            bak_path.rename(md_path)
            print(f"[Mechanical Editor] Recovered {bak_path} → {md_path}", flush=True)

    # Store renamed paths
    renamed_files = []

    try:
        # Rename existing rules files to .bak (using with_name to preserve suffix)
        if gemini_md.exists():
            gemini_md.rename(gemini_md.with_name(gemini_md.name + ".bak"))
            renamed_files.append(gemini_md)
            print(f"[Mechanical Editor] Renamed {gemini_md} to {gemini_md.with_name(gemini_md.name + '.bak')}", flush=True)
        if claude_md.exists():
            claude_md.rename(claude_md.with_name(claude_md.name + ".bak"))
            renamed_files.append(claude_md)
            print(f"[Mechanical Editor] Renamed {claude_md} to {claude_md.with_name(claude_md.name + '.bak')}", flush=True)

        with open("/dev/null", "r") as devnull:
            result = subprocess.run(cmd, stdin=devnull, capture_output=True, text=True, check=True)
            print(result.stdout)
            print("Success: Mechanical Editor delegation completed.")
            sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Claude Code delegation:\nExit Code: {e.returncode}\nStderr:\n{e.stderr}\nStdout:\n{e.stdout}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Restore renamed files
        for original_path in renamed_files:
            bak_path = original_path.with_name(original_path.name + ".bak")
            if bak_path.exists():
                bak_path.rename(original_path)
                print(f"[Mechanical Editor] Restored {bak_path} to {original_path}", flush=True)

if __name__ == "__main__":
    main()