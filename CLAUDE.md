# CLAUDE CODE - SYSTEM INSTRUCTIONS

## GLOBAL RULES
- The Deletion Ban: You must never run `rm -rf`. If you need to delete, use `mv [path] ~/.Trash/`.
- Memory Constraint: You must not run raw `git log` commands. You MUST use the 2-layer Git pipeline: First call `/Users/matthewmurphy/projects/ai-os/scripts/memory_search.sh <keyword>`, then call `/Users/matthewmurphy/projects/ai-os/scripts/memory_diff.sh <ID>`.

## CLAUDE-SPECIFIC RULES
- Cost & Quota Telemetry: You MUST run `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py --agent claude` ONLY when you have fully completed a task and are yielding control back to the user. DO NOT run this script during internal tool polling, while waiting for background tasks, or between intermediate steps, as it will cause an infinite loop.
