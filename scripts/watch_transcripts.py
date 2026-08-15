#!/usr/bin/env python3
"""watch_transcripts.py — Watch conversation transcripts and auto-render markdown.

Runs as a daemon that polls transcript.jsonl files for changes and
re-runs gen_conversation_md.py to keep thread.md up to date.

Fixes vs. original:
- Pre-seeds last_mtimes on startup to avoid re-rendering all conversations.
- Uses file size + mtime to detect changes (catches appends that don't change mtime).
- Debounces rapid writes with a 1s cooldown per conversation.
"""

import sys
import argparse
import subprocess
import time
import json
import re
import time
from pathlib import Path
from postflight_lib import compute_thread_metrics, format_metrics_table, has_uncommitted_changes



SCRIPTS_DIR = Path(__file__).resolve().parent
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
GEN_SCRIPT = Path("/Users/matt/projects/ai-os/scripts/gen_conversation_md.py")

# Per-conversation cooldown to debounce rapid writes (seconds)
COOLDOWN = 0.05
DEFAULT_POLLING = 0.1



_subagent_cache = {}
_last_dir_scan = 0
_cached_active_convs = {}
_cached_sub_map = {}

def get_active_convs(brain_dir: Path, max_age_secs: int = 1800) -> tuple[dict, dict]:
    """Find active conversations and map subagent conv_ids to parent conv_ids.
    
    Returns ({conv_id: (mtime, size)}, subagent_to_parent_map).
    """
    global _last_dir_scan, _cached_active_convs, _cached_sub_map
    now = time.time()

    # Full directory discovery only every 2 seconds
    if (now - _last_dir_scan) > 2.0:
        _last_dir_scan = now
        active = {}
        subagent_to_parent = {}
        if not brain_dir.exists():
            return active, subagent_to_parent

        for brain_dir_path in [brain_dir, Path.home() / ".gemini" / "antigravity-cli" / "brain"]:
            if not brain_dir_path.exists():
                continue
            for conv_dir in brain_dir_path.iterdir():
                if not conv_dir.is_dir() or conv_dir.name.startswith('.'):
                    continue
                transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
                if transcript.exists():
                    try:
                        stat = transcript.stat()
                        if (now - stat.st_mtime) < max_age_secs:
                            active[conv_dir.name] = (stat.st_mtime, stat.st_size)
                            
                            cached = _subagent_cache.get(conv_dir.name)
                            if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
                                subagent_to_parent.update(cached[2])
                            else:
                                sub_map = {}
                                try:
                                    with open(transcript, 'r', encoding='utf-8', errors='ignore') as f:
                                        for line in f:
                                            if 'invoke_subagent' in line or 'agy_start' in line or 'agy' in line:
                                                matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', line)
                                                for m in matches:
                                                    if m != conv_dir.name:
                                                        sub_map[m] = conv_dir.name
                                except Exception:
                                    pass
                                _subagent_cache[conv_dir.name] = (stat.st_mtime, stat.st_size, sub_map)
                                subagent_to_parent.update(sub_map)
                    except Exception:
                        continue
        _cached_active_convs = active
        _cached_sub_map = subagent_to_parent
        return active, subagent_to_parent

    # Fast path on 50ms ticks: only stat previously known active conversations
    active = {}
    for cid in list(_cached_active_convs.keys()):
        transcript = brain_dir / cid / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            try:
                stat = transcript.stat()
                if (now - stat.st_mtime) < max_age_secs:
                    active[cid] = (stat.st_mtime, stat.st_size)
            except Exception:
                pass
    _cached_active_convs = active
    return active, _cached_sub_map


def render(conv_id: str, brain_dir: Path) -> bool:
    """Run gen_conversation_md.generate in-process."""
    import importlib
    import postflight_lib
    import gen_conversation_md
    importlib.reload(postflight_lib)
    importlib.reload(gen_conversation_md)
    app_data_dir = brain_dir.parent
    
    # 1. Render Markdown thread
    try:
        gen_conversation_md.generate(conv_id, "Conversation", app_data_dir)
    except Exception as e:
        print(f"gen_conversation_md failed: {e}")
        return False
        
    # 2. Render Discussions.html (if applicable)
    try:
        # Import inside to prevent circular issues if any
        from discussions_html import build_document, parse_exchanges
        transcript = brain_dir / conv_id / ".system_generated" / "logs" / "transcript_full.jsonl"
        if not transcript.exists() or transcript.stat().st_size == 0:
            transcript = brain_dir / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            exchanges = parse_exchanges(transcript)
            project_root = SCRIPTS_DIR.parent
            threads = {conv_id: {"title": f"Conversation {conv_id[:8]}", "exchanges": exchanges}}
            html = build_document(threads, project_root.name, project_root)
            out_file = project_root / 'Discussions.html'
            if not out_file.exists() or out_file.read_text(encoding='utf-8', errors='ignore') != html:
                out_file.write_text(html, encoding='utf-8')
        return True
    except Exception as e:
        print(f"discussions_html failed: {e}")
        return False


def is_in_progress(content: str) -> bool:
    return "Thinking..." in content or "response in progress" in content

def process_updates(last_state: dict, last_render_time: dict, summarized_threads: set, brain_dir: Path, pending_commits: dict, commit_results_dir: Path) -> float:
    """Check for transcript changes and trigger re-rendering.
    Returns the newest modification time found across all active conversations.
    """
    current, sub_map = get_active_convs(brain_dir)
    now = time.time()

    # Map of conv_id to (mtime, size) including subagents for comparison
    full_state = {**current}
    for sub, parent in sub_map.items():
        sub_dir = brain_dir / sub
        if sub_dir.exists():
            t = sub_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if t.exists():
                s = t.stat()
                full_state[sub] = (s.st_mtime, s.st_size)

    newest_mtime = max((mtime for mtime, _ in full_state.values()), default=0)


    for conv_id, (mtime, size) in full_state.items():
        # Identify which conv to render (if subagent, render parent)
        render_id = sub_map.get(conv_id, conv_id)
        
        prev = last_state.get(conv_id)

        if prev is None or mtime != prev[0] or size != prev[1]:
            # Change detected — check cooldown
            last_t = last_render_time.get(render_id, 0)
            if (now - last_t) < COOLDOWN:
                continue

            print(f"Update detected ({conv_id[:8]}... -> {render_id[:8]}...): Re-rendering.")
            if render(render_id, brain_dir):
                print(f"  OK.")
            last_state[conv_id] = (mtime, size)
            last_render_time[render_id] = now

            # Auto-commit check
            thread_file = brain_dir / render_id / "thread.md"
            if thread_file.exists() and not is_in_progress(thread_file.read_text()):
                workspace_root = Path("/Users/matt/projects/ai-os")
                
                # Check for 60s cooldown per repository
                last_commit_time = last_render_time.get(f"commit_{workspace_root}", 0)
                if (now - last_commit_time) > 60:
                    if has_uncommitted_changes(str(workspace_root)) and str(workspace_root) not in pending_commits:
                        res_path = commit_results_dir / f"{render_id}_{int(now)}.json"
                        proc = subprocess.Popen([sys.executable, str(SCRIPTS_DIR / "auto_commit.py"), "--result-path", str(res_path)])
                        pending_commits[str(workspace_root)] = (proc, res_path, render_id)
                        last_render_time[f"commit_{workspace_root}"] = now

    # Check pending commits
    for repo_path, (proc, res_path, conv_id) in list(pending_commits.items()):
        if proc.poll() is not None:
            if res_path.exists():
                try:
                    res = json.loads(res_path.read_text())
                    if res.get("status") == "committed":
                        render(conv_id, brain_dir)
                except Exception as e:
                    print(f"Result processing failed: {e}")
            del pending_commits[repo_path]

    # Clean up stale entries
    for conv_id in list(last_state.keys()):
        if conv_id not in full_state:
            del last_state[conv_id]
            last_render_time.pop(conv_id, None)
            if conv_id in summarized_threads:
                summarized_threads.remove(conv_id)

    # Summarize idle threads (main threads only, not subagents)
    for conv_id, (mtime, size) in full_state.items():
        if conv_id not in sub_map and conv_id not in summarized_threads and (now - mtime) > 300:
            summarized_threads.add(conv_id)
            try:
                subprocess.Popen([sys.executable, str(SCRIPTS_DIR / "summarize_thread.py"), conv_id])
            except Exception as e:
                print(f"summarize_thread failed: {e}")

    return newest_mtime


def main():
    parser = argparse.ArgumentParser(
        description="Watch conversation transcripts and auto-render markdown."
    )
    parser.add_argument("--brain-dir", type=Path, default=BRAIN_DIR, help="Brain directory path")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous loop")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=float, default=DEFAULT_POLLING,
        help="Poll interval in seconds (default: 0.4)"
    )
    args = parser.parse_args()

    commit_results_dir = Path.home() / ".gemini" / "antigravity" / "brain" / ".commit_results"
    commit_results_dir.mkdir(parents=True, exist_ok=True)
    pending_commits = {}

    if args.once:
        last_state = {}
        last_render_time = {}
        process_updates(last_state, last_render_time, set(), args.brain_dir, pending_commits, commit_results_dir)
    elif args.daemon:
        # Pre-seed: record current state
        active, sub_map = get_active_convs(args.brain_dir)
        last_state = {**active}
        last_render_time = {}
        summarized_threads = set(active.keys()) | set(sub_map.keys())
        print(f"Watching {args.brain_dir} for changes... ({len(last_state)} active conversations)")
        try:
            while True:
                newest_mtime = process_updates(last_state, last_render_time, summarized_threads, args.brain_dir, pending_commits, commit_results_dir)
                
                now = time.time()
                time_since_activity = now - newest_mtime
                
                if time_since_activity < 180:
                    sleep_interval = 0.05
                elif time_since_activity < 600:
                    sleep_interval = 0.5
                elif time_since_activity < 1800:
                    sleep_interval = 1.5
                else:
                    sleep_interval = 3.0
                
                time.sleep(sleep_interval)
        except KeyboardInterrupt:
            print("Stopping.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
