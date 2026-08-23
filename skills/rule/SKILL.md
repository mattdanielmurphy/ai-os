---
name: rule
description: "Inspect, toggle, or configure ai-os system rules and high-reasoning settings."
---

# AI-OS Rule Management

Execute rule inspection and configuration management using `scripts/rule_toggle.py`.

1. **List / Status**:
   If the user typed `/rule`, `/rules`, `/rule list`, or `/rule status`, execute:
   `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py list`
   and present the table of active/disabled rules and current settings.

2. **Toggle Rule On / Off**:
   - To enable a rule: `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py on <rule_id>`
   - To disable a rule: `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py off <rule_id>`
   - To toggle a rule: `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py toggle <rule_id>`

3. **Change Settings**:
   - To change a setting value: `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py set <setting_id> <value>`
   - To inspect a setting: `python3 /Users/matt/projects/ai-os/scripts/rule_toggle.py get <setting_id>`

4. Confirm that `build_rules.py` has recompiled the system directives across `GEMINI.md`, `CLAUDE.md`, and `HERMES.md`.
