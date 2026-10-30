#!/usr/bin/env python3
"""Print a Claude Code session's current context size (k tokens) from its transcript.

Usage: thread_size.py <session-uuid-or-local_id> [--limit 250]
Exit 0 = under the limit (resume it), 2 = at/over (start a fresh thread with a brief).
Works for idle sessions, unlike get_usage, because it reads the .jsonl on disk.
"""
import glob, json, os, sys

def size(uuid):
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{uuid}.jsonl"))
    if not paths:
        return None
    last = None
    for line in open(paths[0]):
        try:
            m = json.loads(line).get("message")
        except Exception:
            continue
        if isinstance(m, dict) and m.get("usage"):
            last = m["usage"]
    if not last:
        return 0
    return (last.get("input_tokens", 0) + last.get("cache_read_input_tokens", 0)
            + last.get("cache_creation_input_tokens", 0))

if __name__ == "__main__":
    sid = sys.argv[1]
    if sid.startswith("local_"):  # desktop-app id -> CLI transcript id
        meta = glob.glob(os.path.expanduser(
            f"~/Library/Application Support/Claude/claude-code-sessions/*/*/{sid}.json"))
        sid = json.load(open(meta[0]))["cliSessionId"] if meta else sid.removeprefix("local_")
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 250
    t = size(sid)
    if t is None:
        print(f"unknown: no transcript for {sid}")
        sys.exit(1)
    k = t // 1000
    print(f"{k}k tokens: {'OVER ' + str(limit) + 'k, start a fresh thread' if k >= limit else 'ok to resume'}")
    sys.exit(2 if k >= limit else 0)
