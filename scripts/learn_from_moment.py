#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def resolve_repo_root(cwd: str) -> Path:
    current = Path(cwd).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "AG_CONTEXT.md").exists():
            return parent
    return current

def guard_skill_path(path: Path):
    path = path.resolve()
    if "builtin" in str(path) or "plugins" in str(path):
        raise PermissionError(f"Cannot edit built-in or plugin skill: {path}")
    if not ("custom-skills" in str(path) or ".gemini/config/skills" in str(path)):
         # It's okay if it's not a skill, but if it is being treated as one, ensure it's not a system one.
         pass

def classify_destination(context: str) -> str:
    context_lower = context.lower()
    if any(word in context_lower for word in ["rule", "domain", "policy"]):
        return "DOMAIN_RULE"
    elif any(word in context_lower for word in ["decision", "timeline", "event"]):
        return "NARRATIVE_DECISION"
    elif any(word in context_lower for word in ["concept", "entity", "wiki"]):
        return "CONCEPTUAL_ENTITY"
    else:
        return "REUSABLE_PROCEDURE"

def append_learning_event(event_data: dict):
    log_dir = Path("agent-logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "learning-events.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(event_data) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Learn from current moment.")
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--cwd", default=os.getcwd())
    args = parser.parse_args()

    root = resolve_repo_root(args.cwd)
    os.chdir(root)

    dest = classify_destination(args.context)
    event = {
        "timestamp": datetime.now().isoformat(),
        "trigger": args.trigger,
        "context": args.context,
        "destination_type": dest
    }
    
    append_learning_event(event)
    print(f"Captured: {dest}. Event appended to agent-logs/learning-events.jsonl")
    
    if dest == "DOMAIN_RULE":
        print(f"Instruction: Append to {root}/AG_CONTEXT.md: {args.context}")
    elif dest == "NARRATIVE_DECISION":
        print(f"Instruction: Append to {root}/DEVELOPMENT_JOURNAL.md: {args.context}")
    elif dest == "REUSABLE_PROCEDURE":
        print(f"Instruction: Create/Update custom skill at {root}/skills/custom-skills/<slug>/SKILL.md")

if __name__ == "__main__":
    main()
