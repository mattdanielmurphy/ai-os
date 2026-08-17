#!/usr/bin/env python3
"""
compile_dynamic_prompt.py - Dynamic System Prompt Compiler for ai-os

Assembles a minimal, tailored system prompt based on role (orchestrator vs leaf),
platform, and active rule toggles from config/rules_config.json.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
RULES_DIR = PROJECT_ROOT / ".rules"
CONFIG_PATH = PROJECT_ROOT / "config" / "rules_config.json"

def load_rules_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load {CONFIG_PATH}: {e}", file=sys.stderr)
    return {"rules": {}, "settings": {}}

def apply_rule_filters(content: str, config: dict) -> str:
    rules = config.get("rules", {})
    settings = config.get("settings", {})

    # Filter out disabled rule blocks
    for rule_id, rule_info in rules.items():
        tag = rule_info.get("tag")
        if not tag:
            continue
        is_enabled = rule_info.get("enabled", True)
        pattern = rf"<!--\s*RULE:{tag}\s*-->[\s\S]*?<!--\s*/RULE:{tag}\s*-->\n*"
        if not is_enabled:
            content = re.sub(pattern, "", content)
        else:
            # Strip the comment tags but keep the content
            content = re.sub(rf"<!--\s*RULE:{tag}\s*-->\n?", "", content)
            content = re.sub(rf"<!--\s*/RULE:{tag}\s*-->\n?", "", content)

    # Clean up any leftover unmatched RULE tags if any exist
    content = re.sub(r"<!--\s*/?RULE:[A-Z0-9_]+\s*-->\n?", "", content)

    # Dynamic settings interpolation
    high_reasoning_setting = settings.get("high_reasoning_model_default", {}).get("value", "perplexity")
    if high_reasoning_setting == "perplexity":
        engine_str = "`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity` (ai-os Perplexity) by default, with `Gemini 3.7 Flash (High)` as a fallback"
    elif high_reasoning_setting == "flash_high":
        engine_str = "`Gemini 3.7 Flash (High)` via `agymcp`"
    elif high_reasoning_setting == "sonnet":
        engine_str = "Claude 3.7 Sonnet via Proxima"
    else:
        engine_str = str(high_reasoning_setting)

    content = content.replace("{HIGH_REASONING_ENGINE}", engine_str)

    # Clean up excessive blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()

def read_rule(name: str, config: dict) -> str:
    path = RULES_DIR / f"{name}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            return apply_rule_filters(raw, config)
    return ""

def compile_stub(platform: str = "antigravity") -> str:
    return """# Antigravity Dynamic Context Stub
Run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` at session start to retrieve your full system directive if not already provided.
"""

def compile_prompt(role: str = "orchestrator", platform: str = "antigravity", prompt_text: str = "", stub: bool = False) -> str:
    if stub and role.lower() != "leaf":
        return compile_stub(platform)

    config = load_rules_config()
    sections = []
    
    # Always include core safety
    core_safety = read_rule("core_safety", config)
    if core_safety:
        sections.append(core_safety)

    if role.lower() == "leaf":
        leaf_path = Path("/Users/matt/.gemini/config/rules/03-subagent.md")
        if leaf_path.exists():
            with open(leaf_path, "r", encoding="utf-8") as f:
                sections.append(apply_rule_filters(f.read().strip(), config))
        return "\n\n".join(sections)

    # Orchestrator mode: add protocols
    git_proto = read_rule("git_protocol", config)
    if git_proto:
        sections.append(git_proto)

    agent_logs = read_rule("agent_logs", config)
    if agent_logs:
        sections.append(agent_logs)

    # Platform specific rules
    if platform.lower() == "antigravity":
        gemini_rules = read_rule("gemini_only", config)
        if gemini_rules:
            sections.append(gemini_rules)
    elif platform.lower() == "claude":
        claude_rules = read_rule("claude_only", config)
        if claude_rules:
            sections.append(claude_rules)
    elif platform.lower() == "hermes":
        hermes_rules = read_rule("hermes_only", config)
        if hermes_rules:
            sections.append(hermes_rules)

    # Dynamic context based on prompt keywords
    p_lower = prompt_text.lower()
    if any(kw in p_lower for kw in ["mac", "hammerspoon", "tcc", "shortcut", "launchagent"]):
        mac_rules = read_rule("mac_env", config)
        if mac_rules:
            sections.append(mac_rules)

    return "\n\n".join(sections)

def main():
    parser = argparse.ArgumentParser(description="Dynamic System Prompt Compiler")
    parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
    parser.add_argument("--platform", default="antigravity", choices=["antigravity", "claude", "hermes", "agy"], help="Target platform")
    parser.add_argument("--prompt", default="", help="User prompt string for keyword matching")

    args = parser.parse_args()
    compiled = compile_prompt(args.role, args.platform, args.prompt)
    print(compiled)

if __name__ == "__main__":
    main()
