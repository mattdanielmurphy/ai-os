import subprocess
import sys
import os
import datetime
import concurrent.futures
import json
import time
import glob
import re
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_cmd(args, timeout=5, check=False):
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=check)
        return res.stdout.strip(), res.returncode
    except Exception:
        return "", 1

def log_preflight(status):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{ts} | WD: {os.getcwd()} | Status: {status}\n"
    
    paths = [os.path.expanduser("~/.preflight.log"), "./tmp/last_preflight.log"]
    for p in paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(log_msg)
        except Exception:
            pass
    return ts

def run_step(name, func, *args):
    try:
        return name, func(*args)
    except Exception as e:
        return name, f"ERROR: {e}"

def step_quota():
    snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
    if os.path.exists(snapshot_path):
        mtime = os.path.getmtime(snapshot_path)
        if time.time() - mtime < 60:
            try:
                with open(snapshot_path, "r", encoding="utf-8") as f:
                    snapshot = json.load(f)
                warnings = [f"{k}: {v*100:.1f}% remaining" for k, v in snapshot.items() if isinstance(v, (int, float)) and v < 0.25]
                if warnings:
                    return f"ag-quota (cached): WARNING ({'; '.join(warnings[:2])})"
                return "ag-quota (cached): OK"
            except Exception:
                pass
    out, code = run_cmd(["ag-quota", "--all", "-j"], timeout=2)
    if code == 0 and out:
        try:
            data = json.loads(out)
            snapshot = {}
            warnings = []
            if isinstance(data, list):
                for acct in data:
                    email = acct.get("email") or acct.get("quota_summary", {}).get("Email", "unknown")
                    models = acct.get("quota_summary", {}).get("Models", [])
                    for m in models:
                        frac = m.get("RemainingFraction", 1.0)
                        is_ex = m.get("IsExhausted", False)
                        disp = m.get("DisplayName") or m.get("ModelID", "")
                        key = f"{email} | {disp}"
                        if isinstance(frac, (int, float)):
                            snapshot[key] = round(frac, 4)
                        if is_ex or (isinstance(frac, (int, float)) and frac < 0.25):
                            warnings.append(f"{key}: {frac*100:.1f}% remaining")
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            if warnings:
                return f"ag-quota: WARNING ({'; '.join(warnings[:2])})"
            return "ag-quota: OK"
        except Exception:
            return "ag-quota: OK"
    return "ag-quota: Skipped/Cached"

def step_aios_planner():
    """Verify AI-OS companion app and Perplexity bridge are alive on port 3031."""
    try:
        req = urllib.request.Request("http://127.0.0.1:3031/api/debug/ping")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            data = resp.read().decode("utf-8")
            if "PPLX=true" in data:
                return "AI-OS Planner (:3031): OK (Perplexity Connected)"
            return "AI-OS Planner (:3031): OK"
    except Exception:
        pass
    return "AI-OS Planner (:3031): OFFLINE (launch agent: aios-server)"

def get_project_board_summary():
    board_path = os.path.expanduser("~/projects/ai-os/PROJECT_BOARD.md")
    if not os.path.exists(board_path):
        return []
    
    in_progress = []
    backlog = []
    current_section = None
    
    try:
        with open(board_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if "In Progress" in line_str:
                    current_section = "in_progress"
                    continue
                elif "Backlog" in line_str or "To Do" in line_str:
                    current_section = "backlog"
                    continue
                elif line_str.startswith("## "):
                    current_section = None
                    continue
                
                if line_str.startswith("- [ ]") and current_section:
                    task_text = line_str[5:].strip()
                    if current_section == "in_progress":
                        in_progress.append(task_text)
                    elif current_section == "backlog":
                        backlog.append(task_text)
    except Exception:
        pass
    
    return in_progress, backlog



def step_rules():
    rules_dir = os.path.expanduser("~/projects/ai-os/.rules")
    target = os.path.expanduser("~/.gemini/GEMINI.md")
    if os.path.exists(rules_dir) and os.path.exists(target):
        try:
            target_mtime = os.path.getmtime(target)
            needs_build = any(
                os.path.getmtime(os.path.join(rules_dir, f)) > target_mtime
                for f in os.listdir(rules_dir) if f.endswith(".md")
            )
            if not needs_build:
                return "Rules: OK"
        except Exception:
            pass
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/build_rules.py")], timeout=2)
    return "Rules: OK" if code == 0 else "Rules: WARNING"

def step_secret_audit():
    try:
        from sanitize_thread import SecretAuditHook
        is_clean, errors = SecretAuditHook.audit_git_diff()
        if not is_clean:
            return f"Secret Audit: BLOCKED ({'; '.join(errors[:2])})"
        return "Secret Audit: OK"
    except Exception as e:
        return f"Secret Audit: OK ({e})"

def step_bloat():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/check_thread_bloat.py"), "-j"], timeout=2)
    return f"Thread Bloat: {'WARNING' if 'true' in out.lower() else 'OK'}" if code == 0 else "Thread Bloat: OK"

def step_git():
    is_git_out, is_git_code = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], timeout=1)
    if is_git_code == 0 and is_git_out == "true":
        _, diff_code = run_cmd(["git", "diff", "--quiet"], timeout=1)
        _, cached_code = run_cmd(["git", "diff", "--cached", "--quiet"], timeout=1)
        untracked_out, _ = run_cmd(["git", "ls-files", "--others", "--exclude-standard"], timeout=1)
        has_local_changes = (diff_code != 0 or cached_code != 0 or bool(untracked_out.strip()))
        
        if has_local_changes:
            status_out, _ = run_cmd(["git", "status", "--porcelain"], timeout=1)
            num_changes = len(status_out.strip().splitlines()) if status_out else 0
            if num_changes > 10:
                print(f"\n⚠️ WARNING: {num_changes} uncommitted file changes detected! Please review and commit changes via auto_commit.py or ask the user before proceeding.\n")
                return f"Git: WARNING ({num_changes} uncommitted changes — commit required before Perplexity plan)"
            return f"Git: OK ({num_changes} uncommitted changes present — commit before planning)"
        
        out, code = run_cmd(["git", "pull"], timeout=5)
        if code == 0:
            res_str = "Up-to-date" if "Already up to date" in out else "Pulled changes"
            return f"Git: OK ({res_str})"
        return "Git: WARNING (pull failed or timed out)"
    return "Git: Skipped (no git repository)"

def step_watcher():
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.matt.agent.watch-transcripts.plist")
    _, pgrep_code = run_cmd(["pgrep", "-f", "watch_transcripts.py"], timeout=1)
    if pgrep_code != 0:
        if os.path.exists(plist_path):
            run_cmd(["launchctl", "load", "-w", plist_path], timeout=3)
            return "Watcher: Loaded watch-transcripts LaunchAgent"
        else:
            watch_script = "/Users/matt/projects/ai-os/scripts/watch_transcripts.py"
            subprocess.Popen(
                f"nohup python3 {watch_script} --daemon > /dev/null 2>&1 &",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            return "Watcher: Started watch_transcripts daemon"
    return "Watcher: Running"

def step_hammerspoon_errors():
    out, code = run_cmd(["osascript", "-e", 'tell application "Hammerspoon" to execute lua code "return hs.console.getConsole()"'], timeout=1)
    if code != 0:
        return "Hammerspoon: ERROR (could not query)"
    
    lines = [l for l in out.splitlines() if l.strip()]
    last_15 = lines[-15:]
    errors = [l for l in last_15 if "ERROR:" in l]
    if errors:
        excerpt = errors[-1].split("ERROR:")[1].strip()[:30]
        return f"Hammerspoon: ERROR ({excerpt})"
    return "Hammerspoon: OK"

def get_memory_data(project_name="ai-os", in_progress=None):
    """Fetch total count and top hydrated memories in a single fast call with mtime caching."""
    cache_dir = os.path.expanduser("~/.hermes/cache")
    clean_proj = re.sub(r'[^a-zA-Z0-9_\-]', '_', project_name or "default")
    cache_file = os.path.join(cache_dir, f"preflight_mem_{clean_proj}.json")
    memory_md = os.path.expanduser("~/.hermes/memories/MEMORY.md")
    
    # Check cache validity (valid for 15 mins, or invalidated if MEMORY.md was touched)
    if os.path.exists(cache_file):
        try:
            cache_mtime = os.path.getmtime(cache_file)
            mem_mtime = os.path.getmtime(memory_md) if os.path.exists(memory_md) else 0
            if (time.time() - cache_mtime < 900) and (cache_mtime > mem_mtime):
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("count", 0), data.get("memories", [])
        except Exception:
            pass

    try:
        query_parts = []
        if project_name and project_name not in ["projects", "matt"]:
            query_parts.append(project_name)
        if in_progress:
            task_clean = re.sub(r'\[.*?\]', '', in_progress[0]).strip()
            query_parts.append(task_clean)
        
        query = " ".join(query_parts).strip() or "user preferences and work style"
        out, code = run_cmd(["aios-memory", "preflight", "--query", query, "--limit", "4"], timeout=6)
        if code == 0 and out:
            data = json.loads(out)
            count = data.get("count", 0)
            memories = data.get("memories", [])
            try:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump({"count": count, "memories": memories}, f)
            except Exception:
                pass
            return count, memories
    except Exception:
        pass
    return 0, []

def get_transcript_path(conv_dir):
    p1 = os.path.join(conv_dir, ".system_generated", "logs", "transcript.jsonl")
    p2 = os.path.join(conv_dir, "transcript.jsonl")
    return p1 if os.path.exists(p1) else p2

def get_thread_context(target_cid=None):
    brain_dirs = [
        os.path.expanduser("~/.gemini/antigravity-ide/brain/"),
        os.path.expanduser("~/.gemini/antigravity/brain/"),
        os.path.expanduser("~/.gemini/antigravity-cli/brain/"),
    ]
    convs = []
    for brain_dir in brain_dirs:
        if not os.path.exists(brain_dir):
            continue
        for d in glob.glob(os.path.join(brain_dir, "*")):
            if os.path.isdir(d) and os.path.basename(d) != "scratch":
                bname = os.path.basename(d)
                if len(bname) >= 32:
                    convs.append(d)
    if not convs: return None, True, 0, []
    
    # Sort by mtime of transcript file, then directory mtime
    def get_sort_key(d):
        t_path = get_transcript_path(d)
        if os.path.exists(t_path): return os.path.getmtime(t_path)
        return os.path.getmtime(d)

    convs.sort(key=get_sort_key, reverse=True)
    
    if target_cid:
        active_path = next((p for p in convs if os.path.basename(p) == target_cid), convs[0])
    else:
        active_path = convs[0]
        
    active_cid = os.path.basename(active_path)
    
    transcript_path = get_transcript_path(active_path)
    user_turn_count = 0
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "USER_INPUT":
                        user_turn_count += 1
                except: continue
    
    is_first = user_turn_count <= 1
    return active_cid, is_first, user_turn_count, convs

def extract_folders(conv_path):
    folders = set()
    patterns = [
        re.compile(r"/Users/matt/projects/([^/\"\'\s\\]+)"),
        re.compile(r"/Users/matt/Library/Mobile Documents/[^/\"\'\s\\]+/([^/\"\'\s\\]+)"),
        re.compile(r"/Users/matt/\.gemini/([^/\"\'\s\\]+)")
    ]
    
    transcript_path = get_transcript_path(conv_path)
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as f:
            for line in f:
                for p in patterns:
                    m = p.search(line)
                    if m:
                        folder = m.group(1).strip("\"\'\n\\")
                        if re.match(r"^[a-zA-Z0-9_\-\.]+$", folder):
                            folders.add(folder)
    return sorted(list(folders))[:3]

def get_thread_title(conv_path):
    transcript_path = get_transcript_path(conv_path)
    if not os.path.exists(transcript_path): return "Untitled"
    
    with open(transcript_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("type") == "USER_INPUT":
                    content = entry.get("content", "")
                    # Strip tags and take first line up to 60 chars
                    clean = re.sub(r'<[^>]+>', '', content).strip()
                    return (clean.splitlines()[0])[:60]
            except: continue
    return "Untitled"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--first-turn", action="store_true")
    parser.add_argument("--subsequent", action="store_true")
    parser.add_argument("--conv-id", help="Target conversation ID")
    args = parser.parse_args()

    active_cid, is_first, turn_count, all_convs = get_thread_context(args.conv_id)
    if args.first_turn: is_first = True
    elif args.subsequent: is_first = False

    log_preflight("STARTED")
    print("=== PRE-FLIGHT CHECK ===")
    
    if is_first:
        steps = [
            ("Quota", step_quota),
            ("Planner", step_aios_planner),
            ("Rules", step_rules),
            ("Secret Audit", step_secret_audit),
            ("Git", step_git),
            ("Watcher", step_watcher),
            ("Hammerspoon", step_hammerspoon_errors),
        ]
        proj_name = os.path.basename(os.getcwd())
        in_progress, backlog = get_project_board_summary()
    else:
        steps = [
            ("Quota", step_quota),
            ("Secret Audit", step_secret_audit),
        ]
        in_progress, backlog = [], []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Launch memory fetch in parallel with step execution
        if is_first:
            mem_future = executor.submit(get_memory_data, proj_name, in_progress)
        
        future_to_step = {executor.submit(run_step, name, func): name for name, func in steps}

        # Main thread concurrently displays Recent Thread Context and Project Board
        if is_first:
            print("\n=== RECENT THREAD CONTEXT (NEW THREAD START) ===")
            seen_titles = set()
            count_shown = 0
            for path in all_convs[1:30]:
                cid = os.path.basename(path)
                title = get_thread_title(path)
                norm_title = title.strip().lower()
                if norm_title in seen_titles:
                    continue
                seen_titles.add(norm_title)
                folders = extract_folders(path)
                folder_str = f" | Folders: {', '.join(folders)}" if folders else ""
                print(f"- [{cid[:8]}] {title}{folder_str}")
                count_shown += 1
                if count_shown >= 8:
                    break
            
            if in_progress or backlog:
                print("\n=== ACTIVE PROJECT BOARD (PROJECT_BOARD.md) ===")
                print("Path: [PROJECT_BOARD.md](/Users/matt/projects/ai-os/PROJECT_BOARD.md)\n")
                if in_progress:
                    print("🚀 In Progress:")
                    for item in in_progress[:4]:
                        print(f"  - {item}")
                if backlog:
                    print("\n📋 Top Backlog:")
                    for item in backlog[:4]:
                        print(f"  - {item}")
                print("================================================\n")

            # Hydrate top relevant memories for Turn 1
            try:
                mem_count, hydrated_memories = mem_future.result(timeout=6)
            except Exception:
                mem_count, hydrated_memories = 0, []

            if hydrated_memories:
                print("=== RELEVANT CONTEXT & MEMORIES (MEM0 HYDRATION) ===")
                for mem in hydrated_memories:
                    print(f"• {mem.lstrip('- •').strip()}")
                print("====================================================\n")
        else:
            print(f"[Thread Context: Active conversation {active_cid[:8]} (turn {turn_count})]\n")
            mem_count = 0

        # Collect step results
        results = {}
        for future in concurrent.futures.as_completed(future_to_step):
            name, result = future.result()
            results[name] = result

    if is_first:
        print(f"- Memory (Mem0): OK ({mem_count} memories indexed)")
    for name, _ in steps:
        print(f"- {results[name]}")

    ts = log_preflight("COMPLETED")
    print(f"\n[PREFLIGHT LOGGED] Timestamp: {ts} | Written to ~/.preflight.log")

if __name__ == "__main__":
    main()
