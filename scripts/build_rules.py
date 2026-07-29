#!/usr/bin/env python3
"""
build_rules.py - Single Source Rule Bundler for ai-os

Combines modular rules from .rules/ into destination targets:
  - CLAUDE.md = common.md + claude_only.md
  - GEMINI.md = common.md + gemini_only.md (written to ~/.gemini/GEMINI.md and synced to ~/projects/ai-os/AGENTS.md)
  - HERMES.md = common.md + hermes_only.md (written to ~/projects/ai-os/HERMES.md and ~/.hermes/HERMES.md)
"""

import os
from pathlib import Path
from compile_dynamic_prompt import compile_prompt

PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
RULES_DIR = PROJECT_ROOT / ".rules"

COMMON_PATH = RULES_DIR / "common.md"
CLAUDE_ONLY_PATH = RULES_DIR / "claude_only.md"
GEMINI_ONLY_PATH = RULES_DIR / "gemini_only.md"
HERMES_ONLY_PATH = RULES_DIR / "hermes_only.md"

CLAUDE_TARGET = PROJECT_ROOT / "CLAUDE.md"
GEMINI_TARGET = Path("/Users/matt/.gemini/GEMINI.md")
HERMES_TARGET_PROJECT = PROJECT_ROOT / "HERMES.md"
HERMES_TARGET_GLOBAL = Path("/Users/matt/.hermes/HERMES.md")

def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            os.chmod(path, 0o644)
        except Exception:
            pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(content + "\n")
    try:
        os.chmod(path, 0o444)
    except Exception:
        pass
    print(f"✅ Generated (Protected 444): {path}")

def main():
    # common = read_file(COMMON_PATH)
    # claude_only = read_file(CLAUDE_ONLY_PATH)
    # gemini_only = read_file(GEMINI_ONLY_PATH)
    # hermes_only = read_file(HERMES_ONLY_PATH)

    # Build CLAUDE.md
    claude_content = compile_prompt(role="orchestrator", platform="claude")
    write_file(CLAUDE_TARGET, claude_content)

    # Build GEMINI.md
    gemini_content = compile_prompt(role="orchestrator", platform="antigravity")
    write_file(GEMINI_TARGET, gemini_content)

    # Build HERMES.md
    hermes_content = compile_prompt(role="orchestrator", platform="hermes")
    write_file(HERMES_TARGET_PROJECT, hermes_content)
    write_file(HERMES_TARGET_GLOBAL, hermes_content)

    # Sync skills across Hermes, Claude, Antigravity, agy, Codex
    sync_skills_script = PROJECT_ROOT / "scripts" / "sync_skills.py"
    if sync_skills_script.exists():
        os.system(f"python3 {sync_skills_script}")

    # Maintain single clean symlink for AGENTS.md -> GEMINI.md if missing or broken
    agents_symlink = PROJECT_ROOT / "AGENTS.md"
    if agents_symlink.is_symlink() or not agents_symlink.exists():
        try:
            if agents_symlink.exists() or agents_symlink.is_symlink():
                agents_symlink.unlink()
            agents_symlink.symlink_to(GEMINI_TARGET)
            print(f"✅ Symlinked: {agents_symlink} -> {GEMINI_TARGET}")
        except Exception as e:
            print(f"Warning creating symlink: {e}")

if __name__ == "__main__":
    main()
