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
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from postflight_lib import compute_thread_metrics, format_metrics_table, has_uncommitted_changes, extract_workspace_root

try:
    from transcript_evaluator import evaluate_turn, run_batch_synthesis_check
except ImportError:
    evaluate_turn = None
    run_batch_synthesis_check = None

BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
GEN_SCRIPT = Path("/Users/matt/projects/ai-os/scripts/gen_conversation_md.py")

# Per-conversation cooldown to debounce rapid writes (seconds)
COOLDOWN = 0.05
DEFAULT_POLLING = 0.1


def log_msg(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


_subagent_cache = {}
_last_dir_scan = 0
_cached_active_convs = {}
_cached_sub_map = {}
_conv_brain_map = {}
_last_scanned_brain_dir = None


def get_brain_dir_for_conv(conv_id: str, default: Path = BRAIN_DIR) -> Path:
    return _conv_brain_map.get(conv_id, default)


def get_active_convs(brain_dir: Path, max_age_secs: int = 1800, force_rescan: bool = False) -> tuple[dict, dict]:
    """Find active conversations and map subagent conv_ids to parent conv_ids.
    
    Returns ({conv_id: (mtime, size)}, subagent_to_parent_map).
    """
    global _last_dir_scan, _cached_active_convs, _cached_sub_map, _conv_brain_map, _last_scanned_brain_dir
    now = time.time()

    # Full directory discovery only every 2 seconds or if brain_dir changed
    if force_rescan or (now - _last_dir_scan) > 2.0 or brain_dir != _last_scanned_brain_dir:
        _last_dir_scan = now
        _last_scanned_brain_dir = brain_dir
        active = {}
        subagent_to_parent = {}
        default_brains = [
            Path.home() / ".gemini" / "antigravity" / "brain",
            Path.home() / ".gemini" / "antigravity-ide" / "brain",
            Path.home() / ".gemini" / "antigravity-cli" / "brain",
        ]
        if brain_dir in default_brains:
            scan_dirs = default_brains
        else:
            scan_dirs = [brain_dir]

        if not any(p.exists() for p in scan_dirs):
            return active, subagent_to_parent

        for brain_dir_path in scan_dirs:
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
                            _conv_brain_map[conv_dir.name] = brain_dir_path
                            
                            cached = _subagent_cache.get(conv_dir.name)
                            if cached and cached[0] == stat.st_mtime and cached[1] == stat.st_size:
                                subagent_to_parent.update(cached[2])
                                for sub_cid in cached[2]:
                                    _conv_brain_map[sub_cid] = brain_dir_path
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
                                                        _conv_brain_map[m] = brain_dir_path
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
        b_dir = _conv_brain_map.get(cid, brain_dir)
        transcript = b_dir / cid / ".system_generated" / "logs" / "transcript.jsonl"
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
        log_msg(f"gen_conversation_md failed for {conv_id}: {e}")
        return False
        
    # 2. Render Discussions.html (main threads only)
    if conv_id not in _cached_sub_map:
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
        except Exception as e:
            log_msg(f"discussions_html failed for {conv_id}: {e}")
    return True


def is_turn_completed(transcript_path: Path) -> bool:
    """Check if the latest turn in transcript.jsonl has completed (agent stopped calling tools)."""
    if not transcript_path.exists():
        return False
    try:
        with open(transcript_path, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            buffer_size = min(size, 8192)
            f.seek(size - buffer_size)
            lines = f.read().decode('utf-8', errors='ignore').strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                t = obj.get('type')
                if t == 'PLANNER_RESPONSE':
                    # Completed turn if no tool calls were made in this planner response
                    return not bool(obj.get('tool_calls'))
                elif t == 'USER_INPUT':
                    # User just asked something, agent hasn't responded yet
                    return False
                elif t in ('MODEL', 'SYSTEM', 'USER_EXPLICIT'):
                    return False
    except Exception as e:
        log_msg(f"is_turn_completed check error: {e}")
        return False
    return False

def process_updates(last_state: dict, last_render_time: dict, summarized_threads: set, brain_dir: Path, pending_commits: dict, commit_results_dir: Path) -> float:
    """Check for transcript changes and trigger re-rendering.
    Returns the newest modification time found across all active conversations.
    """
    current, sub_map = get_active_convs(brain_dir)
    now = time.time()

    # Map of conv_id to (mtime, size) including subagents for comparison
    full_state = {**current}
    for sub, parent in sub_map.items():
        sub_brain = _conv_brain_map.get(sub, brain_dir)
        sub_dir = sub_brain / sub
        if sub_dir.exists():
            t = sub_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if t.exists():
                s = t.stat()
                full_state[sub] = (s.st_mtime, s.st_size)

    newest_mtime = max((mtime for mtime, _ in full_state.values()), default=0)


    for conv_id, (mtime, size) in full_state.items():
        # Identify which conv to render (if subagent, render parent)
        render_id = sub_map.get(conv_id, conv_id)
        target_brain = _conv_brain_map.get(render_id, brain_dir)
        
        prev = last_state.get(conv_id)

        if prev is None or mtime != prev[0] or size != prev[1]:
            # Change detected — check cooldown
            last_t = last_render_time.get(render_id, 0)
            if (now - last_t) < COOLDOWN:
                continue

            log_msg(f"Update detected ({conv_id[:8]}... -> {render_id[:8]}...): Re-rendering.")
            if render(render_id, target_brain):
                log_msg(f"  OK.")
            last_state[conv_id] = (mtime, size)
            last_render_time[render_id] = now

            # Auto-commit check (Trigger only once when the entire turn is completed)
            transcript_file = target_brain / render_id / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript_file.exists() and is_turn_completed(transcript_file):
                # Run background micro-evaluator
                if evaluate_turn:
                    try:
                        with open(transcript_file, 'r', encoding='utf-8', errors='ignore') as tf:
                            all_lines = tf.readlines()
                            turn_idx = sum(1 for l in all_lines if '"type":"USER_INPUT"' in l)
                            for l in reversed(all_lines):
                                if '"type":"PLANNER_RESPONSE"' in l:
                                    evaluate_turn(json.loads(l), render_id, turn_idx)
                                    if run_batch_synthesis_check:
                                        run_batch_synthesis_check(render_id, turn_idx)
                                    break
                    except Exception as e:
                        log_msg(f"Evaluation error: {e}")

                workspace_root = extract_workspace_root(transcript_path=transcript_file)
                if workspace_root and workspace_root.exists():
                    # Check for cooldown per repository
                    last_commit_time = last_render_time.get(f"commit_{workspace_root}", 0)
                    if (now - last_commit_time) > 10:
                        if has_uncommitted_changes(str(workspace_root)) and str(workspace_root) not in pending_commits:
                            res_path = commit_results_dir / f"{render_id}_{int(now)}.json"
                            try:
                                proc = subprocess.Popen(
                                    [sys.executable, str(SCRIPTS_DIR / "auto_commit.py"), "--result-path", str(res_path)],
                                    cwd=str(workspace_root)
                                )
                                pending_commits[str(workspace_root)] = (proc, res_path, render_id, target_brain)
                                last_render_time[f"commit_{workspace_root}"] = now
                            except Exception as e:
                                log_msg(f"Failed to spawn auto_commit for {workspace_root}: {e}")

    # Check pending commits
    for repo_path, item in list(pending_commits.items()):
        proc = item[0]
        res_path = item[1]
        conv_id = item[2]
        c_brain = item[3] if len(item) > 3 else brain_dir
        if proc.poll() is not None:
            if res_path.exists():
                try:
                    res = json.loads(res_path.read_text())
                    if res.get("status") == "committed":
                        render(conv_id, c_brain)
                except Exception as e:
                    log_msg(f"Result processing failed: {e}")
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
                log_msg(f"summarize_thread failed: {e}")

    return newest_mtime


def main():
    parser = argparse.ArgumentParser(
        description="Watch conversation transcripts and auto-render markdown."
    )
    parser.add_argument("--brain-dir", type=Path, default=BRAIN_DIR, help="Brain directory path")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous loop")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=float, default=DEFAULT_POLLING,
        help="Poll interval in seconds (default: 0.1)"
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
        log_msg(f"Watching {args.brain_dir} for changes... ({len(last_state)} active conversations)")
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
            log_msg("Stopping.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
