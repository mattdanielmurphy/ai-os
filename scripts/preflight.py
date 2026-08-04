import subprocess
import sys
import os
import datetime
import concurrent.futures
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_cmd(args, check=False):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return res.stdout.strip(), res.returncode
    except Exception as e:
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
    out, code = run_cmd(["ag-quota", "--all", "-j"])
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
            snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            if warnings:
                return f"ag-quota status: WARNING - Low quota detected ({'; '.join(warnings[:3])})"
            return "ag-quota status: OK (Quota healthy)"
        except Exception:
            return "ag-quota status: OK"
    return "ag-quota execution skipped or produced no output."

def step_jules_quota():
    from jules_quota import get_jules_status
    status = get_jules_status()
    if status["status"] == "OK":
        acct_summary = ", ".join([f"{a['name']}: {a['remaining']}/{a['limit']}" for a in status["accounts"] if a["status"] == "OK"])
        return f"Jules Quota: OK - {status['total_remaining']}/{status['total_limit']} total sessions remaining ({acct_summary})"
    return f"Jules Quota: {status['status']} - {status.get('message', '')}"

def step_triage(role="orchestrator"):
    from triage_task import evaluate_triage
    decision = evaluate_triage(prompt="preflight check", role=role)
    output = [f"Recommended Engine: {decision['engine'].upper()} ({decision['recommended_model']})",
              f"Use Jules: {decision['use_jules']}"]
    if decision["reasoning"]:
        output.append("Reasoning:")
        for r in decision["reasoning"]:
            output.append(f"  - {r}")
    prompt_out = f"\n=== INJECTED SYSTEM DIRECTIVE ===\n{decision.get('compiled_system_prompt', '')}\n================================="
    output.append(prompt_out)
    return "\n".join(output)

def step_litellm():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/parse_litellm_models.py"), "--header"])
    return out if code == 0 else "LiteLLM Header parse: WARNING"

def step_rules():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/build_rules.py")])
    return "rules status: OK" if code == 0 else "rules status: WARNING"

def step_bloat():
    out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/check_thread_bloat.py"), "-j"])
    return f"thread bloat status: {'WARNING (Bloated)' if 'true' in out.lower() else 'OK'}" if code == 0 else "thread bloat status: OK"

def step_git():
    if os.path.exists(".git"):
        _, diff_code = run_cmd(["git", "diff", "--quiet"])
        _, status_code = run_cmd(["git", "diff", "--cached", "--quiet"])
        cmd = ["git", "pull", "--rebase"] if diff_code != 0 or status_code != 0 else ["git", "pull"]
        out, _ = run_cmd(cmd)
        return f"Git pull finished: {out[:50]}"
    return "Git pull skipped"

def step_conversation_response():
    brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
    if not os.path.exists(brain_dir):
        return "Conversation Response: Skipped (no brain dir)"
    
    recent_convs = []
    now = datetime.datetime.now().timestamp()
    for entry in os.listdir(brain_dir):
        t_path = os.path.join(brain_dir, entry, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(t_path):
            mtime = os.path.getmtime(t_path)
            if (now - mtime) < 7200: # updated in last 2h
                recent_convs.append(entry)
    
    if not recent_convs:
        return "Conversation Response: OK (No recent active threads)"
    
    updated = []
    for conv_id in recent_convs:
        out, code = run_cmd(["python3", os.path.expanduser("~/projects/ai-os/scripts/gen_conversation_md.py"), conv_id])
        if code == 0:
            updated.append(conv_id[:8])
            
    return f"Conversation Response: Updated ({', '.join(updated)})"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", default="orchestrator", choices=["orchestrator", "leaf"], help="Agent role")
    args = parser.parse_args()

    log_preflight("STARTED")
    print("=== PRE-FLIGHT CHECK ===")
    
    steps = [
        ("Quota", step_quota),
        ("Jules Quota", step_jules_quota),
        ("Task Triager", lambda: step_triage(args.role)),
        ("LiteLLM", step_litellm),
        ("Rules", step_rules),
        ("Thread Bloat", step_bloat),
        ("Git", step_git),
        ("Conversation Response", step_conversation_response)
    ]
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_step = {executor.submit(run_step, name, func): name for name, func in steps}
        for future in concurrent.futures.as_completed(future_to_step):
            name, result = future.result()
            results[name] = result
            
    for name, _ in steps:
        print(f"\n--- {name} ---")
        print(results[name])

    ts = log_preflight("COMPLETED")
    print(f"\n[PREFLIGHT LOGGED] Timestamp: {ts} | Written to ~/.preflight.log")

if __name__ == "__main__":
    main()
