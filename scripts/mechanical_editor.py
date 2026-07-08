#!/usr/bin/env python3
import sys
import argparse
import subprocess
from pathlib import Path

def parse_config_yaml(config_path):
    mappings = []
    current_name = None
    current_target = None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.startswith("- model_name:"):
                    if current_name and current_target:
                        mappings.append((current_name, current_target))
                    current_name = s.split(":", 1)[1].strip()
                    current_target = None
                elif s.startswith("model:"):
                    current_target = s.split(":", 1)[1].strip()
        if current_name and current_target:
            mappings.append((current_name, current_target))
    except Exception as e:
        print(f"Warning: Failed to parse {config_path}: {e}", file=sys.stderr)
    return mappings

def resolve_model(requested_model, mappings):
    requested_model = requested_model.lower().strip()
    
    # Try to find a match in config mappings
    matched_name = None
    for model_name, model_target in mappings:
        model_name_clean = model_name.lower().replace("*", "")
        model_target_clean = model_target.lower()
        
        # Substring match on the target model path (e.g. deepseek-v4-pro)
        if requested_model in model_target_clean or model_target_clean in requested_model:
            matched_name = model_name
            break
            
        # Match on the model name in config (e.g. fable, haiku, opus, sonnet)
        if requested_model in model_name_clean or model_name_clean in requested_model:
            matched_name = model_name
            break
            
    # Fallback to standard aliases if not resolved
    if not matched_name:
        if "pro" in requested_model or "fable" in requested_model:
            matched_name = "claude-fable"
        elif "opus" in requested_model or "gemini-pro" in requested_model:
            matched_name = "claude-opus"
        elif "sonnet" in requested_model or "gemini-flash" in requested_model:
            matched_name = "claude-sonnet"
        else:
            matched_name = "claude-haiku"
            
    # Map resolved config name to exact CLI supported choices
    matched_name = matched_name.lower()
    if "fable" in matched_name:
        return "claude-fable-5"
    elif "opus" in matched_name:
        return "claude-3-opus-20240229"
    elif "sonnet" in matched_name:
        return "claude-3-5-sonnet-latest"
    else:
        return "claude-3-5-haiku-20241022"

def main():
    parser = argparse.ArgumentParser(description="Mechanical Editor utilizing Claude Code CLI")
    parser.add_argument("filepath", help="Path to the file to modify")
    parser.add_argument("spec", help="Technical spec describing the modifications")
    parser.add_argument("--model", default="deepseek-v4-flash", help="The actual target model name (e.g. deepseek-v4-pro, deepseek-v4-flash, gemini-2.5-pro)")
    args = parser.parse_args()
    
    filepath = Path(args.filepath).resolve()
    if not filepath.exists():
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    # Parse mappings from litellm config
    config_path = Path("/Users/matt/litellm/config.yaml")
    mappings = parse_config_yaml(config_path)
    
    # Resolve requested actual model to the corresponding Claude CLI option
    anthropic_model = resolve_model(args.model, mappings)
    
    prompt = f"Apply this technical spec: '{args.spec}' to the file: '{filepath}'"
    
    cmd = [
        "claude",
        "--model",
        anthropic_model,
        "-p",
        prompt,
        "--dangerously-skip-permissions"
    ]
    
    print(f"[Mechanical Editor] Mapped requested model '{args.model}' to Claude option '{anthropic_model}' (via config.yaml).", flush=True)
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
