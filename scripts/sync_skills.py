#!/usr/bin/env python3
import os
import shutil
import json
import subprocess
import filecmp
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
        if loc.exists() and loc.is_dir():
            for root, _, files in os.walk(loc):
                for f in files:
                    full_path = Path(root) / f
                    if full_path.is_file() and not full_path.is_symlink():
                        try:
                            rel_path = full_path.relative_to(loc)
                            all_rel_paths.add(str(rel_path))
                        except ValueError:
                            continue

    # Handle Deletions
    for rel_path in list(state.keys()):
        if rel_path not in all_rel_paths:
            git_checkpoint(rel_path)
            for loc in all_locations:
                file_path = loc / rel_path
                if file_path.exists() and file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
            del state[rel_path]

    # Handle additions and updates with the repository as the authority.
    # The old newest-mtime strategy allowed a stale installed copy to win over
    # a deliberate repository edit. Target-only skills are intentionally left
    # untouched; only paths owned by the primary source are propagated.
    for rel_path in sorted(all_rel_paths):
        source_path = PRIMARY_SOURCE / rel_path
        if not source_path.is_file():
            continue

        source_mtime = source_path.stat().st_mtime
        for loc in TARGET_DIRS:
            target_path = loc / rel_path
            if target_path.exists() and target_path.is_dir():
                continue
            if target_path.resolve() == source_path.resolve():
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not target_path.exists() or not filecmp.cmp(source_path, target_path, shallow=False):
                    shutil.copy2(source_path, target_path)
            except OSError:
                pass
        state[rel_path] = source_mtime

    save_state(state)

if __name__ == "__main__":
    main()
