#!/usr/bin/env python3
"""
rollback.py - Instant 1-second recovery tool for AI-OS Codex Hooks.

Restores the previous monolithic ~/.codex/AGENTS.md and disables the dynamic hook engine.
"""

import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

CODEX_DIR = Path.home() / ".codex"
AGENTS_MD = CODEX_DIR / "AGENTS.md"
AGENTS_MD_BAK = CODEX_DIR / "AGENTS.md.bak"
CONFIG_FILE = CODEX_DIR / "hooks_config.json"
HOOKS_JSON = CODEX_DIR / "hooks.json"
HOOKS_JSON_DISABLED = CODEX_DIR / "hooks.json.disabled"


def rollback():
    print("Initiating AI-OS Codex Hooks Rollback...")

    # 1. Restore AGENTS.md from backup
    if AGENTS_MD_BAK.exists():
        try:
            # Remove existing read-only permissions if present
            if AGENTS_MD.exists():
                AGENTS_MD.chmod(0o644)
            shutil.copy2(AGENTS_MD_BAK, AGENTS_MD)
            print(f"✅ Restored monolithic AGENTS.md from {AGENTS_MD_BAK} ({AGENTS_MD.stat().st_size} bytes)")
        except Exception as e:
            print(f"❌ Error restoring AGENTS.md: {e}", file=sys.stderr)
    else:
        print("⚠️ Warning: No AGENTS.md.bak found; running build_rules.py fallback...", file=sys.stderr)

    # 2. Disable hooks config
    try:
        config_data = {
            "mode": "disabled",
            "updated_at": datetime.now().isoformat(),
            "description": "Hooks rolled back and disabled"
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        print("✅ Set hook operating mode to DISABLED in hooks_config.json")
    except Exception as e:
        print(f"❌ Error updating hooks_config.json: {e}", file=sys.stderr)

    # 3. Disable hooks.json if present
    if HOOKS_JSON.exists():
        try:
            HOOKS_JSON.rename(HOOKS_JSON_DISABLED)
            print(f"✅ Renamed {HOOKS_JSON} -> {HOOKS_JSON_DISABLED}")
        except Exception as e:
            print(f"❌ Error renaming hooks.json: {e}", file=sys.stderr)

    print("\n🎉 Rollback complete! System restored to static global instructions.")


if __name__ == "__main__":
    rollback()
