#!/usr/bin/env python3
import argparse
import json
import os
import uuid
import re
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Constants
BRAIN_DIR = Path.home() / ".gemini/antigravity/brain"
CONFIG_DIR = Path.home() / ".config/gemini-antigravity-bridge"
SYNC_STATE_FILE = CONFIG_DIR / "sync_state.json"
SUMMARY_FILE = BRAIN_DIR / "thread_summaries.json"
DOCS_THREADS_DIR = Path("/Users/matt/projects/ai-os/docs/gemini-threads")


def load_sync_state():
    if SYNC_STATE_FILE.exists():
        with open(SYNC_STATE_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_sync_state(state):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_stable_uuid(raw_id):
    try:
        return str(uuid.UUID(raw_id))
    except (ValueError, TypeError):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"gemini-thread:{raw_id}"))

def parse_frontmatter(content):
    meta = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            fm_content = parts[1]
            for line in fm_content.splitlines():
                if ':' in line:
                    key, val = line.split(':', 1)
                    meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta

def extract_messages(content):
    messages = []
    # Try regex comments format
    comment_pattern = re.compile(r'<!-- gemini-message index=(\d+) role="([^"]+)" timestamp="([^"]*)" -->([\s\S]*?)<!-- /gemini-message -->')
    matches = comment_pattern.findall(content)
    
    if matches:
        # Check if min index is 1 to normalize
        indices = [int(idx) for idx, _, _, _ in matches]
        min_idx = min(indices) if indices else 0
        normalize = (min_idx == 1)

        for idx, role, ts, text in matches:
            step_idx = int(idx)
            if normalize: step_idx -= 1
            
            role_map = {"user": ("USER_EXPLICIT", "USER_INPUT"), "assistant": ("MODEL", "PLANNER_RESPONSE"), "model": ("MODEL", "PLANNER_RESPONSE")}
            src, typ = role_map.get(role, ("MODEL", "PLANNER_RESPONSE"))
            msg = text.strip()
            # Clean headers
            msg = re.sub(r'^## (User|Gemini|Assistant).*?\n', '', msg, flags=re.IGNORECASE)
            messages.append({"step_index": step_idx, "source": src, "type": typ, "created_at": ts, "content": msg})
    else:
        # Fallback to headers
        header_pattern = re.compile(r'## (User|Gemini|Assistant).*?\n([\s\S]*?)(?=(?:^## )|\Z)', re.MULTILINE)
        matches = header_pattern.findall(content)
        for i, (role, text) in enumerate(matches):
            src, typ = ("USER_EXPLICIT", "USER_INPUT") if role.lower() == "user" else ("MODEL", "PLANNER_RESPONSE")
            messages.append({"step_index": i, "source": src, "type": typ, "created_at": datetime.now().isoformat(), "content": text.strip()})
    
    return messages

def update_summaries(uuid_key, title):
    summaries = {}
    if SUMMARY_FILE.exists():
        with open(SUMMARY_FILE, 'r') as f:
            try: summaries = json.load(f)
            except: pass
    summaries[uuid_key] = f"[Gemini] {title}"
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, 'w') as f:
        json.dump(summaries, f, indent=2)

SUMMARIES_DB = Path.home() / ".gemini/antigravity-cli/conversation_summaries.db"

def register_sqlite_summary(conv_id: str, title: str, step_count: int, ts_iso: str, workspace_uri: str = "file:///Users/matt/projects/ai-os", project_id: str = "a01b1e37-2f5f-4f03-a7cc-e48d0e5c1b02"):
    if not SUMMARIES_DB.exists():
        return
    try:
        conn = sqlite3.connect(str(SUMMARIES_DB))
        cur = conn.cursor()
        
        preview = f"[Gemini] {title}"
        workspace_json = json.dumps([workspace_uri])
        
        cur.execute("""
            INSERT INTO conversation_summaries (
                conversation_id, title, preview, step_count, last_modified_time,
                workspace_uris, status, source, project_id, agent_name,
                parent_conversation_id, nesting_depth, battle_id, winning_conversation_id,
                not_fully_idle, killed, last_user_input_time, last_user_input_step_index, app_data_dir
            ) VALUES (
                ?, '', ?, ?, ?,
                ?, '', '', ?, '',
                '', 0, '', '',
                0, 0, ?, ?, 'antigravity'
            ) ON CONFLICT(conversation_id) DO UPDATE SET
                preview = excluded.preview,
                step_count = excluded.step_count,
                last_modified_time = excluded.last_modified_time,
                workspace_uris = excluded.workspace_uris,
                project_id = excluded.project_id,
                last_user_input_time = excluded.last_user_input_time,
                last_user_input_step_index = excluded.last_user_input_step_index;
        """, (
            conv_id,
            preview,
            step_count,
            ts_iso,
            workspace_json,
            project_id,
            ts_iso,
            0
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[gemini-bridge] SQLite register error for {conv_id}: {e}")

def get_file_date(file_path):
    # 1. Filename YYYY-MM-DD
    match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except:
            pass

    # 2. Frontmatter
    try:
        content = file_path.read_text(errors='ignore')
        meta = parse_frontmatter(content)
        for key in ['archived_at', 'timestamp', 'date']:
            if key in meta:
                try:
                    dt_str = meta[key].replace('Z', '+00:00')
                    dt = datetime.fromisoformat(dt_str)
                    return dt.replace(tzinfo=None)
                except:
                    pass
    except:
        pass
        
    # 3. st_mtime
    return datetime.fromtimestamp(file_path.stat().st_mtime)

def process_file(file_path, sync_state, dry_run=False, quiet=False, force=False):
    with open(file_path, 'r') as f:
        content = f.read()
    
    file_hash = hashlib.md5(content.encode()).hexdigest()
    if not force and not dry_run and sync_state.get(str(file_path)) == file_hash:
        if not quiet: print(f"Skipping: {file_path.name} (no changes)")
        return file_hash

    meta = parse_frontmatter(content)
    conv_id = get_stable_uuid(meta.get('conversation_id', file_path.name))
    title = meta.get('title', file_path.stem)
    
    messages = extract_messages(content)
    
    if dry_run:
        if not quiet: print(f"[DRY-RUN] Would process {title} ({conv_id}) with {len(messages)} messages")
        return file_hash

    thread_dir = BRAIN_DIR / conv_id
    logs_dir = thread_dir / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Save transcripts
    with open(logs_dir / "transcript.jsonl", 'w') as f:
        for msg in messages:
            f.write(json.dumps({**msg, "status": "DONE"}) + "\n")
    
    with open(logs_dir / "transcript_full.jsonl", 'w') as f:
        for msg in messages:
            f.write(json.dumps({**msg, "status": "DONE"}) + "\n")
            
    # Clean up and write markdown to docs/
    DOCS_THREADS_DIR.mkdir(parents=True, exist_ok=True)
    clean_md_path = DOCS_THREADS_DIR / f"{file_path.stem}.md"
    
    with open(clean_md_path, 'w') as f:
        f.write(f"---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"date: \"{datetime.now().date()}\"\n")
        f.write(f"source: \"gemini.google.com\"\n")
        f.write(f"conversation_id: \"{conv_id}\"\n")
        f.write(f"url: \"{meta.get('url', '')}\"\n")
        f.write(f"---\n\n")
        f.write(f"# {title}\n\n")
        f.write(f"> [!NOTE]\n> Archived Gemini Thread: [{title}]({meta.get('url', '')}) | Date: {datetime.now().date()}\n\n")
        
        for msg in messages:
            role_header = "## User" if msg['source'] == "USER_EXPLICIT" else "## Gemini"
            f.write(f"{role_header}\n{msg['content']}\n\n---\n\n")

    update_summaries(conv_id, title)

    
    ts_iso = datetime.now().isoformat()
    if messages:
        ts_iso = messages[-1]['created_at']
    register_sqlite_summary(conv_id, title, len(messages), ts_iso)
    if not quiet: print(f"[gemini-bridge] Synced: {title} ({conv_id})")
    return file_hash

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    sync_state = load_sync_state()
    archive_dir = Path.home() / "Documents/gemini-archive/threads"

    def perform_sync():
        files = []
        if args.file: 
            files.append(args.file)
        elif args.all or args.days or args.watch:
            files = list(archive_dir.glob("*.md"))
        
        if args.days and files:
            latest_file_date = max((get_file_date(f) for f in files), default=datetime.now())
            cutoff = latest_file_date - timedelta(days=args.days)
            files = [f for f in files if get_file_date(f) >= cutoff]

        for f in files:
            file_hash = process_file(f, sync_state, args.dry_run, args.quiet, args.force)
            if not args.dry_run:
                sync_state[str(f)] = file_hash
        
        if not args.dry_run:
            save_sync_state(sync_state)

    if args.watch:
        import time
        try:
            while True:
                perform_sync()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[gemini-bridge] Stopped watching.")
    else:
        perform_sync()

if __name__ == "__main__":
    main()
