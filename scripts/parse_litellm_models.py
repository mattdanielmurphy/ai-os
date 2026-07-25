#!/usr/bin/env python3
import os
import re
import json
import difflib
import argparse
from pathlib import Path

DEFAULT_CONFIG_PATH = "/Users/matt/litellm/config.yaml"

def parse_litellm_tiers(config_path=DEFAULT_CONFIG_PATH):
    path = Path(config_path)
    if not path.exists():
        return {"error": f"Config file not found: {config_path}"}

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    header = content.split("common_params:")[0] if "common_params:" in content else content
    tiers = {}
    current_tier = None

    for line in header.splitlines():
        line_str = line.strip()
        tier_match = re.search(r"TIER\s+(\d+)", line_str, re.IGNORECASE)
        if tier_match:
            current_tier = f"tier_{tier_match.group(1)}"
            tiers[current_tier] = []
            continue
        model_match = re.search(r"#\s*\d+\.\s*([\w\.\-]+)", line_str)
        if model_match and current_tier:
            tiers[current_tier].append(model_match.group(1))

    return tiers

def get_header_comment(config_path=DEFAULT_CONFIG_PATH, lines_count=30):
    path = Path(config_path)
    if not path.exists():
        return f"# Config file not found: {config_path}"

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[:lines_count]

    comment_lines = []
    for line in lines:
        if line.strip().startswith("common_params:"):
            break
        comment_lines.append(line)
    return "".join(comment_lines).strip()

def get_available_models(config_path=DEFAULT_CONFIG_PATH, exclude_fallbacks=True):
    path = Path(config_path)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    models = []
    for line in content.splitlines():
        line_s = line.strip()
        if line_s.startswith("- model_name:"):
            name = line_s.split(":", 1)[1].strip()
            if exclude_fallbacks and name.endswith("-or"):
                continue
            models.append(name)
    return models

def validate_model(requested_model, config_path=DEFAULT_CONFIG_PATH):
    available = get_available_models(config_path=config_path, exclude_fallbacks=True)
    if requested_model in available:
        return True, f"Valid model: {requested_model}", available

    matches = difflib.get_close_matches(requested_model, available, n=1, cutoff=0.3)
    closest = matches[0] if matches else None

    models_str = ", ".join(available)
    err_msg = "That's not a model name."
    if closest:
        err_msg += f" Did you mean \"{closest}\" which is the closest match we've got?"
    err_msg += f" Available models: {models_str}"

    return False, err_msg, available

def get_allowed_models(config_path=DEFAULT_CONFIG_PATH, allow_gemini_35_flash=True):
    tiers = parse_litellm_tiers(config_path)
    if "error" in tiers:
        return []

    allowed = list(tiers.get("tier_1", []))
    if allow_gemini_35_flash:
        for t_name, models in tiers.items():
            for m in models:
                if m == "gemini-3.5-flash" and m not in allowed:
                    allowed.append(m)
    return allowed

def main():
    parser = argparse.ArgumentParser(description="Parse LiteLLM config model tiers and validate models.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")
    parser.add_argument("--json", action="store_true", help="Output full JSON of tiers")
    parser.add_argument("--allowed-only", action="store_true", help="Output allowed delegation models")
    parser.add_argument("--header", action="store_true", help="Output the top comment block (~30 lines)")
    parser.add_argument("--list-models", action="store_true", help="List available model names (excluding fallbacks)")
    parser.add_argument("--validate", type=str, help="Validate if a given model name exists in config.yaml")

    args = parser.parse_args()

    if args.header:
        print(get_header_comment(args.config))
    elif args.list_models:
        print("\n".join(get_available_models(args.config)))
    elif args.validate:
        valid, msg, _ = validate_model(args.validate, args.config)
        print(msg)
        if not valid:
            exit(1)
    elif args.allowed_only:
        print(" ".join(get_allowed_models(args.config)))
    else:
        tiers = parse_litellm_tiers(args.config)
        print(json.dumps(tiers, indent=2))

if __name__ == "__main__":
    main()
