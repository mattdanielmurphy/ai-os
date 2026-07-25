#!/usr/bin/env python3
"""
parse_litellm_models.py - Extracts model tiers from LiteLLM config header comments.
"""

import os
import re
import json
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
    parser = argparse.ArgumentParser(description="Parse LiteLLM config model tiers.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")
    parser.add_argument("--json", action="store_true", help="Output full JSON of tiers")
    parser.add_argument("--allowed-only", action="store_true", help="Output allowed delegation models")
    
    args = parser.parse_args()
    
    if args.allowed_only:
        print(" ".join(get_allowed_models(args.config)))
    else:
        tiers = parse_litellm_tiers(args.config)
        print(json.dumps(tiers, indent=2))

if __name__ == "__main__":
    main()
