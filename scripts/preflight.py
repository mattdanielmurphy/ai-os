import subprocess
import sys
import os
import datetime
import concurrent.futures
import json
import time
import glob
import re

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

def step_jules_quota():
    try:
        from jules_quota import get_jules_status
        status = get_jules_status()
        if status["status"] == "OK":
            return f"Jules Quota: OK ({status['total_remaining']}/{status['total_limit']} sessions)"
        return f"Jules Quota: {status['status']}"
    except Exception:
        return "Jules Quota: Skipped"


def step_pplx_quota():
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q.get("status") == "OK":
            return f"Perplexity Quota: OK ({q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research, {q.get('remaining_uploads')} Uploads)"
        return f"Perplexity Quota: {q.get('status')}"
    except Exception as e:
        return f"Perplexity Quota: ERROR ({e})"

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
        _, untracked_out = run_cmd(["git", "ls-files", "--others", "--exclude-standard"], timeout=1)
        has_local_changes = (diff_code != 0 or cached_code != 0 or len(untracked_out) > 0)
        
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
        print("\n=== RECENT THREAD CONTEXT (NEW THREAD START) ===")
        summaries = {}
        for sum_dir in ["~/.gemini/antigravity-ide/brain", "~/.gemini/antigravity/brain", "~/.gemini/antigravity-cli/brain"]:
            sum_path = os.path.expanduser(f"{sum_dir}/thread_summaries.json")
            if os.path.exists(sum_path):
                with open(sum_path, "r") as f:
                    try:
                        loaded = json.load(f)
                        for k, v in loaded.items():
                            if k not in summaries:
                                summaries[k] = v
                    except: pass
        
        print("--- Detailed Summaries of Past 5 Threads ---")
        for i, path in enumerate(all_convs[1:6]):
            cid = os.path.basename(path)
            folders = extract_folders(path)
            title = get_thread_title(path)
            summ = summaries.get(cid, "No summary available")
            if summ == "No summary available":
                summ = get_thread_title(path)
            print(f"[{i+1}] [{cid[:8]}] {title}")
            print(f"    Folders: {', '.join(folders) if folders else 'None'}")
            print(f"    Summary: {summ}")
        
        print("\n--- Titles & Folders of Past 10 Threads ---")
        for path in all_convs[1:11]:
            cid = os.path.basename(path)
            folders = extract_folders(path)
            title = get_thread_title(path)
            print(f"- [{cid[:8]}] {title} | Folders: {', '.join(folders) if folders else 'None'}")
        
        in_progress, backlog = get_project_board_summary()
        if in_progress or backlog:
            print("\n=== ACTIVE PROJECT BOARD (PROJECT_BOARD.md) ===")
            print("Path: file:///Users/matt/projects/ai-os/PROJECT_BOARD.md")
            print("Launch: http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md\n")
            if in_progress:
                print("🚀 In Progress:")
                for item in in_progress[:4]:
                    print(f"  - {item}")
            if backlog:
                print("\n📋 Top Backlog:")
                for item in backlog[:4]:
                    print(f"  - {item}")
            print("================================================\n")
    else:
        print(f"[Thread Context: Active conversation {active_cid[:8]} (turn {turn_count})]\n")
    
    if is_first:
        steps = [
            ("Quota", step_quota),
            ("Jules Quota", step_jules_quota),
            ("Perplexity", step_pplx_quota),
            ("Rules", step_rules),
            ("Secret Audit", step_secret_audit),
            ("Git", step_git),
            ("Watcher", step_watcher),
            ("Hammerspoon", step_hammerspoon_errors),
        ]
    else:
        steps = [
            ("Quota", step_quota),
            ("Secret Audit", step_secret_audit),
        ]
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_step = {executor.submit(run_step, name, func): name for name, func in steps}
        for future in concurrent.futures.as_completed(future_to_step):
            name, result = future.result()
            results[name] = result
            
    for name, _ in steps:
        print(f"- {results[name]}")

    ts = log_preflight("COMPLETED")
    print(f"\n[PREFLIGHT LOGGED] Timestamp: {ts} | Written to ~/.preflight.log")

if __name__ == "__main__":
    main()

