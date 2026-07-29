#!/usr/bin/env python3
"""
compile_dynamic_prompt.py - Dynamic System Prompt Compiler for ai-os

Assembles a minimal, tailored system prompt based on role (orchestrator vs leaf)
and task context/keywords.
"""

import os
import sys
import argparse
from pathlib import Path

RULES_DIR = Path("/Users/matt/projects/ai-os/.rules")

def read_rule(name: str) -> str:
    path = RULES_DIR / f"{name}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def compile_prompt(role: str = "orchestrator", platform: str = "antigravity", prompt_text: str = "") -> str:
    sections = []
    
    # Always include core safety
    sections.append(read_rule("core_safety"))

    if role.lower() == "leaf":
        sections.append(read_rule("subagent_leaf"))
        return "\n\n".join(sections)

    # Orchestrator mode: add protocols
    sections.append(read_rule("git_protocol"))
    sections.append(read_rule("agent_logs"))

    # Platform specific rules
    if platform.lower() == "antigravity":
        sections.append(read_rule("gemini_only"))
    elif platform.lower() == "claude":
        sections.append(read_rule("claude_only"))
    elif platform.lower() == "hermes":
        sections.append(read_rule("hermes_only"))

    # Dynamic context based on prompt keywords
    p_lower = prompt_text.lower()
    if any(kw in p_lower for kw in ["mac", "hammerspoon", "tcc", "shortcut", "launchagent"]):
        sections.append(read_rule("mac_env"))

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
