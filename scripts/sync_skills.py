#!/usr/bin/env python3
import os
import shutil
import json
import subprocess
import filecmp
import hashlib
from pathlib import Path
from datetime import datetime

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

def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def move_to_trash(path, rel_path):
    trash = HOME / ".Trash"
    trash.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = trash / f"sync-skills-{stamp}-{rel_path.replace('/', '_')}"
    shutil.move(str(path), str(destination))

def main():
    state = load_state()
    # Only repository files define managed skills. Runtime-only/vendor skills
    # must never become sync inputs merely because they exist in a target.
    source_rel_paths = set()
    if PRIMARY_SOURCE.exists():
        for root, _, files in os.walk(PRIMARY_SOURCE):
            for name in files:
                full_path = Path(root) / name
                if full_path.is_file() and not full_path.is_symlink():
                    source_rel_paths.add(str(full_path.relative_to(PRIMARY_SOURCE)))

    # Retire only target files whose content still matches the last source
    # snapshot recorded by this sync. Older state entries (mtime-only) and
    # modified/vendor content are preserved for manual review.
    for rel_path, prior in list(state.items()):
        if rel_path in source_rel_paths:
            continue
        if not isinstance(prior, dict):
            # Legacy mtime entries cannot prove ownership; leave any target
            # files untouched, but stop tracking them as managed state.
            del state[rel_path]
            continue
        expected_hash = prior.get("sha256")
        if not expected_hash:
            del state[rel_path]
            continue
        for loc in TARGET_DIRS:
            file_path = loc / rel_path
            if file_path.is_file() and not file_path.is_symlink():
                try:
                    if file_hash(file_path) == expected_hash:
                        move_to_trash(file_path, rel_path)
                except OSError:
                    pass
        del state[rel_path]

    # Handle additions and updates with the repository as the authority.
    # The old newest-mtime strategy allowed a stale installed copy to win over
    # a deliberate repository edit. Target-only skills are intentionally left
    # untouched; only paths owned by the primary source are propagated.
    for rel_path in sorted(source_rel_paths):
        source_path = PRIMARY_SOURCE / rel_path
        if not source_path.is_file():
            continue

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
        state[rel_path] = {"sha256": file_hash(source_path)}

    save_state(state)

if __name__ == "__main__":
    main()
