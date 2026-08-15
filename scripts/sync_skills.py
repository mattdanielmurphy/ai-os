#!/usr/bin/env python3
import os
import shutil
import json
import subprocess
from pathlib import Path

HOME = Path.home()
PRIMARY_SOURCE = HOME / "projects" / "ai-os" / "skills"
STATE_FILE = Path("/Users/matt/projects/ai-os/scripts/.sync_skills_state.json")

TARGET_DIRS = [
    HOME / ".hermes" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".agents" / "skills",
    HOME / ".gemini" / "config" / "skills",
    HOME / ".gemini" / "antigravity-cli" / "skills",
    HOME / ".agy" / "skills",
    HOME / ".gemini" / "antigravity" / "skills",
]

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def git_checkpoint(rel_path):
    try:
        # Check if exists in primary source
        if (PRIMARY_SOURCE / rel_path).exists():
            subprocess.run(["git", "-C", str(PRIMARY_SOURCE.parent), "add", f"skills/{rel_path}"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(PRIMARY_SOURCE.parent), "commit", "-m", f"Auto-checkpoint before skill deletion: {rel_path}"], check=True, capture_output=True)
    except Exception:
        pass

def main():
    state = load_state()
    all_locations = [PRIMARY_SOURCE] + TARGET_DIRS
    
    # Discover all relative paths
    all_rel_paths = set()
    for loc in all_locations:
        if loc.exists():
            for root, _, files in os.walk(loc):
                for f in files:
                    full_path = Path(root) / f
                    rel_path = full_path.relative_to(loc)
                    all_rel_paths.add(str(rel_path))

    # Handle Deletions
    for rel_path in list(state.keys()):
        if rel_path not in all_rel_paths:
            git_checkpoint(rel_path)
            for loc in all_locations:
                file_path = loc / rel_path
                if file_path.exists():
                    if file_path.is_file():
                        file_path.unlink()
            del state[rel_path]

    # Handle Additions/Updates
    for rel_path in all_rel_paths:
        max_mtime = 0.0
        newest_file = None
        
        # Find newest
        for loc in all_locations:
            file_path = loc / rel_path
            if file_path.exists():
                mtime = file_path.stat().st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
                    newest_file = file_path
        
        if newest_file and (rel_path not in state or state[rel_path] < max_mtime):
            # Sync to all
            for loc in all_locations:
                target_path = loc / rel_path
                if target_path.resolve() != newest_file.resolve():
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(newest_file, target_path)
                    except shutil.SameFileError:
                        pass
            state[rel_path] = max_mtime

    save_state(state)

if __name__ == "__main__":
    main()
