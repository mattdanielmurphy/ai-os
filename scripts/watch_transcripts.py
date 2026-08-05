#!/usr/bin/env python3
"""watch_transcripts.py — Watch conversation transcripts and auto-render markdown.

Runs as a daemon that polls transcript.jsonl files for changes and
re-runs gen_conversation_md.py to keep thread.md up to date.

Fixes vs. original:
- Pre-seeds last_mtimes on startup to avoid re-rendering all conversations.
- Uses file size + mtime to detect changes (catches appends that don't change mtime).
- Debounces rapid writes with a 1s cooldown per conversation.
"""

import argparse
import subprocess
import time
from pathlib import Path

BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
GEN_SCRIPT = Path("/Users/matt/projects/ai-os/scripts/gen_conversation_md.py")

# Per-conversation cooldown to debounce rapid writes (seconds)
COOLDOWN = 1.0


def get_active_convs(max_age_secs: int = 7200) -> dict:
    """Find conversation IDs with transcript.jsonl updated within max_age_secs.
    
    Returns {conv_id: (mtime, size)} for active conversations.
    """
    active = {}
    if not BRAIN_DIR.exists():
        return active

    now = time.time()
    for conv_dir in BRAIN_DIR.iterdir():
        if not conv_dir.is_dir():
            continue
        transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            stat = transcript.stat()
            if (now - stat.st_mtime) < max_age_secs:
                active[conv_dir.name] = (stat.st_mtime, stat.st_size)
    return active


def render(conv_id: str) -> bool:
    """Run gen_conversation_md.py for a conversation. Returns True on success."""
    try:
        subprocess.run(
            ["python3", str(GEN_SCRIPT), conv_id],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error re-rendering {conv_id}: {e}")
        if e.stderr:
            print(f"  stderr: {e.stderr.strip()[:200]}")
        return False


def process_updates(last_state: dict, last_render_time: dict):
    """Check for transcript changes and trigger re-rendering."""
    current = get_active_convs()
    now = time.time()

    for conv_id, (mtime, size) in current.items():
        prev = last_state.get(conv_id)
        if prev is None or mtime != prev[0] or size != prev[1]:
            # Change detected — check cooldown
            last_t = last_render_time.get(conv_id, 0)
            if (now - last_t) < COOLDOWN:
                continue  # Skip, will catch on next poll

            print(f"Update detected: {conv_id[:12]}... Re-rendering.")
            if render(conv_id):
                print(f"  OK.")
            last_state[conv_id] = (mtime, size)
            last_render_time[conv_id] = now

    # Clean up stale entries
    for conv_id in list(last_state.keys()):
        if conv_id not in current:
            del last_state[conv_id]
            last_render_time.pop(conv_id, None)


def main():
    parser = argparse.ArgumentParser(
        description="Watch conversation transcripts and auto-render markdown."
    )
    parser.add_argument("--daemon", action="store_true", help="Run in continuous loop")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--interval", type=float, default=2.0,
        help="Poll interval in seconds (default: 2.0)"
    )
    args = parser.parse_args()

    if args.once:
        last_state = {}
        last_render_time = {}
        process_updates(last_state, last_render_time)
    elif args.daemon:
        # Pre-seed: record current state so we don't re-render everything on startup
        last_state = get_active_convs()
        last_render_time = {}
        print(f"Watching {BRAIN_DIR} for changes... ({len(last_state)} active conversations)")
        try:
            while True:
                process_updates(last_state, last_render_time)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopping.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
