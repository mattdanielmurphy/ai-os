#!/usr/bin/env python3
"""WorktreeCreate / WorktreeRemove hook: git worktrees made of APFS clones.

The Claude app normally runs `git worktree add`, which writes every tracked file
for real (~110 MB per ai-os thread). This hook registers the worktree with
`--no-checkout`, then fills it with copy-on-write clones (clonefile) of the base
checkout's unmodified tracked files, so a new worktree costs ~0 disk until files
are edited. Files that differ from the start commit are written by git normally.

Contract (Claude desktop app): JSON on stdin {hook_event_name, cwd (base repo),
name}; for WorktreeCreate print the new worktree's absolute path as the last
stdout line, exit 0. Any failure in the clone step falls back to a plain
checkout so a thread never fails to start because of this hook.

Test without the app:  scripts/clone_worktree.py --test <repo>
Undo: remove the WorktreeCreate/WorktreeRemove entries from ~/.claude/settings.json.
"""
import ctypes
import json
import os
import subprocess
import sys
import time

LOG = os.path.expanduser("~/Library/Logs/clone_worktree.log")
_libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
_clonefile = _libc.clonefile
_clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
CLONE_NOFOLLOW = 0x0001


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def start_ref(base):
    """Same start point as the app: the remote default branch, else HEAD."""
    ref = git(base, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD", check=False).strip()
    if ref:
        branch = ref.split("/", 1)[1]
        subprocess.run(["git", "-C", base, "fetch", "-q", "origin", branch],
                       capture_output=True, timeout=20)
        return ref
    return "HEAD"


def clone_files(base, wt, start):
    """Clone every tracked file whose base-checkout content equals `start`'s."""
    # Files whose working copy differs from `start` (edits, staged, or start != HEAD).
    differ = set(git(base, "diff", "--name-only", "-z", start).split("\0"))
    cloned = 0
    for entry in git(base, "ls-files", "-s", "-z").split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        if meta.startswith("160000") or path in differ:  # submodule or changed
            continue
        src, dst = os.path.join(base, path), os.path.join(wt, path)
        if not os.path.lexists(src) or os.path.lexists(dst):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if _clonefile(src.encode(), dst.encode(), CLONE_NOFOLLOW) == 0:
            cloned += 1
    return cloned


def create(base, name):
    base = git(base, "rev-parse", "--show-toplevel").strip()
    wt = os.path.join(base, ".claude", "worktrees", name)
    branch = f"claude/{name}"
    start = start_ref(base)
    git(base, "worktree", "add", "--no-checkout", "-q", "-b", branch, wt, start)
    t0 = time.time()
    try:
        cloned = clone_files(base, wt, start)
        git(wt, "reset", "-q")                      # index from HEAD, files untouched
        git(wt, "update-index", "-q", "--refresh", check=False)
        git(wt, "checkout", "-q", "--", ".")        # writes only missing/differing files
        log(f"create {wt} from {start}: {cloned} cloned in {time.time() - t0:.1f}s")
    except Exception as e:                          # never block a thread start
        log(f"clone failed for {wt}, plain checkout instead: {e}")
        git(wt, "checkout", "-q", "-f", branch)
    return wt


def remove(path, base):
    git(base, "worktree", "remove", "--force", path, check=False)
    log(f"remove {path}")


def main():
    if sys.argv[1:2] == ["--test"]:
        print(create(sys.argv[2], f"clonetest-{int(time.time())}"))
        return
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    if event == "WorktreeCreate":
        print(create(data["cwd"], data["name"]))
    elif event == "WorktreeRemove":
        remove(data["worktree_path"], data["cwd"])


if __name__ == "__main__":
    main()
