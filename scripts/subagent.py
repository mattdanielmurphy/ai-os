#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path
from parse_litellm_models import validate_model, get_available_models, DEFAULT_CONFIG_PATH

def main():
    models_str = ", ".join(get_available_models(DEFAULT_CONFIG_PATH))
    epilog_str = f"Available Models (excluding fallbacks):\n  {models_str}"

    parser = argparse.ArgumentParser(
        description="Invoke subagents with strict model validation against LiteLLM config.yaml.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_str
    )
    
    parser.add_argument("-p", "--prompt", type=str, required=True, help="Prompt / task description for the subagent.")
    parser.add_argument("-m", "--model", type=str, default="deepseek-v4-flash", help="Model name as defined in litellm config.yaml")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")

    args = parser.parse_args()

    valid, msg, available = validate_model(args.model, config_path=args.config)
    if not valid:
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    print(f"[Subagent Invoker] Model: {args.model} | Prompt length: {len(args.prompt)} chars")
    
    cmd = ["claude", "--model", args.model, "-p", args.prompt]
    try:
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    except Exception as e:
        print(f"Execution Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
