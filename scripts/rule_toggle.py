#!/usr/bin/env python3
"""
rule_toggle.py - CLI tool to inspect, toggle, and configure ai-os system rules & settings.

Usage:
  python3 scripts/rule_toggle.py list
  python3 scripts/rule_toggle.py on <rule_id>
  python3 scripts/rule_toggle.py off <rule_id>
  python3 scripts/rule_toggle.py toggle <rule_id>
  python3 scripts/rule_toggle.py set <setting_id> <value>
  python3 scripts/rule_toggle.py get <setting_id>
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/Users/matt/projects/ai-os")
CONFIG_PATH = PROJECT_ROOT / "config" / "rules_config.json"
BUILD_RULES_SCRIPT = PROJECT_ROOT / "scripts" / "build_rules.py"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"💾 Updated configuration: {CONFIG_PATH}")

def rebuild_rules():
    if BUILD_RULES_SCRIPT.exists():
        print("🔨 Rebuilding system rules (GEMINI.md, CLAUDE.md, HERMES.md)...")
        res = subprocess.run([sys.executable, str(BUILD_RULES_SCRIPT)], capture_output=True, text=True)
        if res.returncode == 0:
            print("✅ System rules successfully compiled & synced.")
        else:
            print(f"❌ Error rebuilding rules:\n{res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)

def list_rules(config: dict):
    rules = config.get("rules", {})
    settings = config.get("settings", {})

    print("\n" + "=" * 60)
    print("📋 AI-OS SYSTEM RULE TOGGLES")
    print("=" * 60)
    for rule_id, rule in rules.items():
        status = "🟢 ON " if rule.get("enabled", True) else "🔴 OFF"
        name = rule.get("name", rule_id)
        desc = rule.get("description", "")
        file_name = rule.get("file", "")
        print(f"[{status}]  {rule_id:<26} ({name})")
        if desc:
            print(f"         └─ {desc} [{file_name}]")

    print("\n" + "-" * 60)
    print("⚙️  GLOBAL CONFIGURATION SETTINGS")
    print("-" * 60)
    for setting_id, setting in settings.items():
        val = setting.get("value")
        options = setting.get("options", [])
        desc = setting.get("description", "")
        opts_str = f" (Options: {', '.join(options)})" if options else ""
        print(f"🔹 {setting_id:<28} = {val}{opts_str}")
        if desc:
            print(f"   └─ {desc}")
    print("=" * 60 + "\n")

def set_rule_status(rule_id: str, enabled: bool):
    config = load_config()
    rules = config.get("rules", {})
    if rule_id not in rules:
        print(f"❌ Unknown rule ID: '{rule_id}'. Run 'rule_toggle.py list' to see available rules.", file=sys.stderr)
        sys.exit(1)

    old_state = rules[rule_id].get("enabled", True)
    rules[rule_id]["enabled"] = enabled
    save_config(config)
    
    state_str = "ENABLED" if enabled else "DISABLED"
    print(f"✨ Rule '{rule_id}' is now {state_str} (was {'ENABLED' if old_state else 'DISABLED'}).")
    rebuild_rules()

def toggle_rule(rule_id: str):
    config = load_config()
    rules = config.get("rules", {})
    if rule_id not in rules:
        print(f"❌ Unknown rule ID: '{rule_id}'. Run 'rule_toggle.py list' to see available rules.", file=sys.stderr)
        sys.exit(1)

    cur_state = rules[rule_id].get("enabled", True)
    new_state = not cur_state
    rules[rule_id]["enabled"] = new_state
    save_config(config)

    state_str = "ENABLED" if new_state else "DISABLED"
    print(f"✨ Toggled rule '{rule_id}' -> {state_str}.")
    rebuild_rules()

def set_setting(setting_id: str, value: str):
    config = load_config()
    settings = config.get("settings", {})
    if setting_id not in settings:
        print(f"❌ Unknown setting ID: '{setting_id}'. Run 'rule_toggle.py list' to see available settings.", file=sys.stderr)
        sys.exit(1)

    allowed = settings[setting_id].get("options")
    if allowed and value not in allowed:
        print(f"❌ Invalid value '{value}' for setting '{setting_id}'. Allowed options: {allowed}", file=sys.stderr)
        sys.exit(1)

    old_val = settings[setting_id].get("value")
    settings[setting_id]["value"] = value
    save_config(config)
    print(f"✨ Setting '{setting_id}' updated to '{value}' (was '{old_val}').")
    rebuild_rules()

def get_setting(setting_id: str):
    config = load_config()
    settings = config.get("settings", {})
    if setting_id not in settings:
        print(f"❌ Unknown setting ID: '{setting_id}'.", file=sys.stderr)
        sys.exit(1)
    print(f"{setting_id} = {settings[setting_id].get('value')}")

def print_help():
    print("""
Usage:
  python3 scripts/rule_toggle.py list                 # List all rules and settings
  python3 scripts/rule_toggle.py on <rule_id>         # Enable a specific rule
  python3 scripts/rule_toggle.py off <rule_id>        # Disable a specific rule
  python3 scripts/rule_toggle.py toggle <rule_id>     # Toggle a rule on/off
  python3 scripts/rule_toggle.py set <setting> <val>  # Change a configuration setting
  python3 scripts/rule_toggle.py get <setting>        # Inspect a setting value
""")

def main():
    if len(sys.argv) < 2:
        list_rules(load_config())
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd in ("list", "ls", "status"):
        list_rules(load_config())
    elif cmd in ("on", "enable"):
        if len(sys.argv) < 3:
            print("❌ Missing rule ID. Usage: rule_toggle.py on <rule_id>")
            sys.exit(1)
        set_rule_status(sys.argv[2], True)
    elif cmd in ("off", "disable"):
        if len(sys.argv) < 3:
            print("❌ Missing rule ID. Usage: rule_toggle.py off <rule_id>")
            sys.exit(1)
        set_rule_status(sys.argv[2], False)
    elif cmd in ("toggle", "flip"):
        if len(sys.argv) < 3:
            print("❌ Missing rule ID. Usage: rule_toggle.py toggle <rule_id>")
            sys.exit(1)
        toggle_rule(sys.argv[2])
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("❌ Missing parameters. Usage: rule_toggle.py set <setting_id> <value>")
            sys.exit(1)
        set_setting(sys.argv[2], sys.argv[3])
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("❌ Missing setting ID. Usage: rule_toggle.py get <setting_id>")
            sys.exit(1)
        get_setting(sys.argv[2])
    elif cmd in ("-h", "--help", "help"):
        print_help()
    else:
        print(f"❌ Unknown command: {cmd}")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
