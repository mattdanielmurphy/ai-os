import subprocess
import sys
import os
import datetime
import concurrent.futures
import json
import time

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
    
    # Check cache freshness (valid for 60s)
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

    # If stale or missing, query ag-quota with short timeout
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
    from jules_quota import get_jules_status
    status = get_jules_status()
    if status["status"] == "OK":
        return f"Jules Quota: OK ({status['total_remaining']}/{status['total_limit']} sessions)"
    return f"Jules Quota: {status['status']}"

def step_pplx_quota():
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q.get("status") == "OK":
            return f"Perplexity Quota: OK ({q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research, {q.get('remaining_uploads')} Uploads)"
        return f"Perplexity Quota: {q.get('status')}"
    except Exception as e:
        return f"Perplexity Quota: ERROR ({e})"

def step_triage(role="orchestrator", verbose=False):
    from triage_task import evaluate_triage
    decision = evaluate_triage(prompt="preflight check", role=role)
    line = f"Triager: Engine {decision['engine'].upper()} ({decision['recommended_model']}) | Jules: {decision['use_jules']}"
    if verbose and decision.get('compiled_system_prompt'):
        line += f"\n--- INJECTED DIRECTIVE ---\n{decision['compiled_system_prompt'][:200]}...\n--------------------------"
    return line

def step_rules():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/build_rules.py")], timeout=2)
    return "Rules: OK" if code == 0 else "Rules: WARNING"

def step_bloat():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/check_thread_bloat.py"), "-j"], timeout=2)
    return f"Thread Bloat: {'WARNING' if 'true' in out.lower() else 'OK'}" if code == 0 else "Thread Bloat: OK"

def step_git():
    if os.path.exists(".git"):
        _, diff_code = run_cmd(["git", "diff", "--quiet"], timeout=1)
        _, cached_code = run_cmd(["git", "diff", "--cached", "--quiet"], timeout=1)
        _, untracked_out = run_cmd(["git", "ls-files", "--others", "--exclude-standard"], timeout=1)
        has_local_changes = (diff_code != 0 or cached_code != 0 or len(untracked_out) > 0)
        
        if has_local_changes:
            # Count modified/untracked files
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
    return "Git: Skipped (no .git)"

def step_watcher():
    _, pgrep_code = run_cmd(["pgrep", "-f", "watch_transcripts.py"], timeout=1)
    if pgrep_code != 0:
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

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    log_preflight("STARTED")
    print("=== PRE-FLIGHT CHECK ===")
    try:
        import json, os
        summaries_path = os.path.expanduser("~/.gemini/antigravity/brain/thread_summaries.json")
        if os.path.exists(summaries_path):
            with open(summaries_path, "r") as f:
                summaries = json.load(f)
                if summaries:
                    print("\n=== RECENT THREAD SUMMARIES ===")
                    for cid, summ in list(summaries.items())[-3:]:
                        print(f"- [{cid[:8]}] {summ}")
                    print("===============================\n")
    except Exception as e:
        print(f"Failed to load thread summaries: {e}")

    
    steps = [
        ("Quota", step_quota),
        ("Jules Quota", step_jules_quota),
        ("Perplexity", step_pplx_quota),
        ("Task Triager", lambda: step_triage(args.role, args.verbose)),
        ("Rules", step_rules),
        ("Thread Bloat", step_bloat),
        ("Git", step_git),
        ("Watcher", step_watcher),
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

