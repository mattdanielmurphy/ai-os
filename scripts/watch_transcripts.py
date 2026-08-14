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
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
GEN_SCRIPT = Path("/Users/matt/projects/ai-os/scripts/gen_conversation_md.py")

# Per-conversation cooldown to debounce rapid writes (seconds)
COOLDOWN = 1.0


def get_active_convs(brain_dir: Path, max_age_secs: int = 7200) -> tuple[dict, dict]:
    """Find active conversations and map subagent conv_ids to parent conv_ids.
    
    Returns ({conv_id: (mtime, size)}, subagent_to_parent_map).
    """
    active = {}
    subagent_to_parent = {}
    if not brain_dir.exists():
        return active, subagent_to_parent

    now = time.time()
    for conv_dir in brain_dir.iterdir():
        if not conv_dir.is_dir():
            continue
        transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            stat = transcript.stat()
            if (now - stat.st_mtime) < max_age_secs:
                active[conv_dir.name] = (stat.st_mtime, stat.st_size)
                
                # Scan for subagents
                try:
                    with open(transcript) as f:
                        for line in f:
                            try:
                                obj = json.loads(line)
                                content = obj.get('content', '')
                                if re.search(r'(?:invoke_subagent|agy_start|agy)\b', content):
                                    matches = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', content)
                                    for m in matches:
                                        if m != conv_dir.name:
                                            subagent_to_parent[m] = conv_dir.name
                            except: continue
                except: pass
    return active, subagent_to_parent


def render(conv_id: str, brain_dir: Path) -> bool:
    """Run gen_conversation_md.py AND discussions_html.py for a conversation."""
    app_data_dir = brain_dir.parent
    
    # 1. Render Markdown thread
    try:
        sys.path.append(str(SCRIPTS_DIR))
        from gen_conversation_md import generate
        generate(conv_id, "Conversation", app_data_dir=app_data_dir)
        try:
            from link_formatter import enrich_file_links
            thread_md = brain_dir / conv_id / "thread.md"
            if thread_md.exists():
                enriched = enrich_file_links(thread_md.read_text())
                tmp_md = thread_md.with_name(f"{thread_md.name}.tmp")
                tmp_md.write_text(enriched)
                tmp_md.replace(thread_md)
        except Exception as e:
            print(f"link_formatter enrichment on thread.md failed: {e}")
    except Exception as e:
        print(f"gen_conversation_md failed: {e}")
        return False
        
    # 2. Render Discussions.html
    try:
        from discussions_html import build_document, parse_exchanges
        transcript = brain_dir / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.exists():
            exchanges = parse_exchanges(transcript)
            project_root = SCRIPTS_DIR.parent
            threads = {conv_id: {"title": f"Conversation {conv_id[:8]}", "exchanges": exchanges}}
            html = build_document(threads, project_root.name, project_root)
            out_file = project_root / 'Discussions.html'
            out_file.write_text(html)
        return True
    except Exception as e:
        print(f"discussions_html failed: {e}")
        return False


def process_updates(last_state: dict, last_render_time: dict, summarized_threads: set, brain_dir: Path):
    """Check for transcript changes and trigger re-rendering."""
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

    for conv_id, (mtime, size) in full_state.items():
        # Identify which conv to render (if subagent, render parent)
        render_id = sub_map.get(conv_id, conv_id)
        
        prev = last_state.get(conv_id)
        
        # Check for self-healing need (stale in-progress marker when transcript is complete)
        thread_file = brain_dir / render_id / "thread.md"
        needs_repair = False
        if thread_file.exists():
            try:
                t_content = thread_file.read_text()
                if "*(response in progress)*" in t_content:
                    # check if parent transcript has finished planner response
                    p_trans = brain_dir / render_id / ".system_generated" / "logs" / "transcript.jsonl"
                    if p_trans.exists() and p_trans.stat().st_size > 0:
                        needs_repair = True
            except Exception:
                pass

        if needs_repair or prev is None or mtime != prev[0] or size != prev[1]:
            # Change detected — check cooldown
            last_t = last_render_time.get(render_id, 0)
            if (now - last_t) < COOLDOWN:
                continue

            print(f"Update detected ({conv_id[:8]}... -> {render_id[:8]}...): Re-rendering.")
            if render(render_id, brain_dir):
                print(f"  OK.")
            last_state[conv_id] = (mtime, size)
            last_render_time[render_id] = now

    # Clean up stale entries
    for conv_id in list(last_state.keys()):
        if conv_id not in current:
            del last_state[conv_id]
            last_render_time.pop(conv_id, None)
            if conv_id in summarized_threads:
                summarized_threads.remove(conv_id)

    # Summarize idle threads
    for conv_id, (mtime, size) in full_state.items():
        if conv_id not in summarized_threads and (now - mtime) > 300:
            print(f"Thread {conv_id[:8]} idle > 5m. Triggering summarize_thread.py...")
            subprocess.Popen([sys.executable, str(SCRIPTS_DIR / "summarize_thread.py"), conv_id])
            summarized_threads.add(conv_id)


def main():
    parser = argparse.ArgumentParser(
        description="Watch conversation transcripts and auto-render markdown."
    )
    parser.add_argument("--brain-dir", type=Path, default=BRAIN_DIR, help="Brain directory path")
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
        process_updates(last_state, last_render_time, set(), args.brain_dir)
    elif args.daemon:
        # Pre-seed: record current state
        active, _ = get_active_convs(args.brain_dir)
        last_state = {**active}
        last_render_time = {}
        summarized_threads = set()
        print(f"Watching {args.brain_dir} for changes... ({len(last_state)} active conversations)")
        try:
            while True:
                process_updates(last_state, last_render_time, summarized_threads, args.brain_dir)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopping.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
