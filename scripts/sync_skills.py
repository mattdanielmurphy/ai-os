#!/usr/bin/env python3
"""
sync_skills.py - Universal Cross-Platform Skill Synchronizer for ai-os

This script synchronizes skills FROM a single source of truth:
~/projects/ai-os/skills/

TO all target agent ecosystems:
  - Hermes: ~/.hermes/skills/
  - Claude: ~/.claude/skills/
  - Codex / Agents: ~/.agents/skills/
  - Gemini / Antigravity: ~/.gemini/config/skills/ & ~/.gemini/antigravity-cli/skills/
  - agy: ~/.agy/skills/
  - Antigravity: ~/.antigravity/skills/
"""

import os
import shutil
from pathlib import Path

HOME = Path.home()

PRIMARY_SOURCE = HOME / "projects" / "ai-os" / "skills"

TARGET_DIRS = [
    HOME / ".hermes" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".agents" / "skills",
    HOME / ".gemini" / "config" / "skills",
    HOME / ".gemini" / "antigravity-cli" / "skills",
    HOME / ".agy" / "skills",
    HOME / ".gemini" / "antigravity" / "skills",
]

def sync_skill_directory(src_dir: Path, dest_dir: Path):
    """
    Copies skill files from src_dir to dest_dir, preserving subdirectories and files.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        rel_path = Path(root).relative_to(src_dir)
        target_root = dest_dir / rel_path
        target_root.mkdir(parents=True, exist_ok=True)
        for f in files:
            src_file = Path(root) / f
            dest_file = target_root / f
            # Copy if missing or modified
            if not dest_file.exists() or src_file.stat().st_mtime > dest_file.stat().st_mtime:
                shutil.copy2(src_file, dest_file)

def main():
    print("=== UNIVERSAL SKILL SYNCHRONIZER ===")

    if not PRIMARY_SOURCE.exists():
        print(f"❌ Primary source directory not found: {PRIMARY_SOURCE}")
        return

    # Find all skills in the primary source directory
    skills = {}
    for item in PRIMARY_SOURCE.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            skills[item.name] = item

    print(f"📦 Total unique custom skills in source: {len(skills)}")

    synced_count = 0
    # Sync every skill to all target platforms
    for skill_name, src_path in skills.items():
        for tdir in TARGET_DIRS:
            target_skill_dir = tdir / skill_name
            try:
                sync_skill_directory(src_path, target_skill_dir)
                synced_count += 1
            except Exception as e:
                print(f"⚠️ Error syncing {skill_name} to {tdir}: {e}")

    print(f"✅ Skill sync complete across {len(TARGET_DIRS)} target directories!")

if __name__ == "__main__":
    main()
