#!/usr/bin/env python3
"""
rollout.py - Manage rollout phases for AI-OS Codex Hooks.

Modes:
  - shadow:   Hooks intercept tool calls, log violations to ~/.codex/hooks_audit.log, but do NOT block.
  - enforce:  Hooks strictly block violations (rm, .env reads, npm, git init ~) at execution layer.
  - disabled: Hooks are bypassed completely.

Usage:
  python3 rollout.py --mode shadow
  python3 rollout.py --mode enforce
  python3 rollout.py --status
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

CODEX_DIR = Path.home() / ".codex"
CONFIG_FILE = CODEX_DIR / "hooks_config.json"
AUDIT_LOG_FILE = CODEX_DIR / "hooks_audit.log"
POLICIES_DIR = CODEX_DIR / "policies"
AGENTS_MD = CODEX_DIR / "AGENTS.md"


def get_current_status():
    mode = "enforce"
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                mode = data.get("mode", "enforce")
        except Exception:
            pass

    policies_count = len(list(POLICIES_DIR.glob("*.md"))) if POLICIES_DIR.exists() else 0
    agents_size = AGENTS_MD.stat().st_size if AGENTS_MD.exists() else 0
    agents_lines = len(AGENTS_MD.read_text(encoding="utf-8").splitlines()) if AGENTS_MD.exists() else 0

    audit_events = 0
    blocked_events = 0
    shadow_events = 0
    if AUDIT_LOG_FILE.exists():
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        audit_events += 1
                        try:
                            entry = json.loads(line)
                            if entry.get("blocked"):
                                blocked_events += 1
                            else:
                                shadow_events += 1
                        except Exception:
                            pass
        except Exception:
            pass

    print("=== AI-OS Codex Hooks Status ===")
    print(f"Active Mode:          {mode.upper()}")
    print(f"Global AGENTS.md:     {agents_size} bytes ({agents_lines} lines)")
    print(f"Compiled Policies:    {policies_count} files in {POLICIES_DIR}")
    print(f"Audit Log Events:     {audit_events} total ({blocked_events} blocked, {shadow_events} shadow)")
    print("================================")


def set_mode(mode: str):
    if mode not in ["shadow", "enforce", "disabled"]:
        print(f"Error: Invalid mode '{mode}'. Choose 'shadow', 'enforce', or 'disabled'.", file=sys.stderr)
        sys.exit(1)

    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    config_data = {
        "mode": mode,
        "updated_at": datetime.now().isoformat(),
        "description": "AI-OS Codex Dynamic Hook Engine Configuration"
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    print(f"✅ Successfully updated AI-OS hook mode to: {mode.upper()}")
    get_current_status()


def main():
    parser = argparse.ArgumentParser(description="Manage AI-OS Codex Hooks Rollout")
    parser.add_argument("--mode", choices=["shadow", "enforce", "disabled"], help="Set hook operating mode")
    parser.add_argument("--status", action="store_true", help="Display current hook status and metrics")

    args = parser.parse_args()

    if args.mode:
        set_mode(args.mode)
    elif args.status or len(sys.argv) == 1:
        get_current_status()


if __name__ == "__main__":
    main()
