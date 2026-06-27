# CLAUDE CODE - SYSTEM INSTRUCTIONS

## GLOBAL RULES
- The Deletion Ban: You must never run `rm -rf`. If you need to delete, use `mv [path] ~/.Trash/`.
- Memory Constraint: You must not run raw `git log` commands. You MUST use the 2-layer Git pipeline: First call `/Users/matthewmurphy/projects/ai-os/scripts/memory_search.sh <keyword>`, then call `/Users/matthewmurphy/projects/ai-os/scripts/memory_diff.sh <ID>`.

## CLAUDE-SPECIFIC RULES
- Cost Telemetry: At the end of every single turn, you MUST call `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py` to report token usage and cost.
- Cost Telemetry: At the end of every single turn, you MUST run /Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py --agent claude to report the true delegated cost.
