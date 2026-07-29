#!/usr/bin/env python3
import subprocess
import sys
import os
from compile_dynamic_prompt import compile_prompt

def run_cmd(args, check=False):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return res.stdout.strip(), res.returncode
    except Exception as e:
        return "", 1

def main():
    print("=== PRE-FLIGHT CHECK ===")
    
    # Dynamic Prompt Check
    print("\n--- Running Dynamic Prompt Compiler (compile_dynamic_prompt.py) ---")
    try:
        from compile_dynamic_prompt import compile_prompt
        prompt_text = compile_prompt(role="orchestrator", platform="antigravity")
        approx_tokens = len(prompt_text) // 4
        print(f"Dynamic Prompt: OK (Role: Orchestrator | ~{approx_tokens:,} tokens)")
    except Exception as e:
        print(f"Dynamic Prompt: ERROR ({e})")
    
    # 1. Quota Check
    print("--- Running Quota Check (ag-quota) ---")
    out, code = run_cmd(["ag-quota", "--all", "-j"])
    if code == 0 and out:
        try:
            import json
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

            # Save quota snapshot for postflight delta comparison
            snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)

            if warnings:
                print(f"ag-quota status: WARNING - Low quota detected ({'; '.join(warnings[:3])})")
            else:
                print("ag-quota status: OK (Quota healthy)")
        except Exception:
            print("ag-quota status: OK")
    else:
        print("ag-quota execution skipped or produced no output.")

    # 1b. Jules Delegation Quota Check
    print("\n--- Running Jules Quota Check (jules_quota.py) ---")
    jules_quota_script = os.path.expanduser("~/projects/ai-os/scripts/jules_quota.py")
    if os.path.exists(jules_quota_script):
        jq_out, jq_code = run_cmd(["python3", jules_quota_script])
        if jq_code == 0 and jq_out:
            print(jq_out)
        else:
            print("Jules Quota Check: UNCONFIGURED or ERROR")
    else:
        print("jules_quota.py missing.")

    # 1c. Automated Task Triaging
    print("\n--- Running Task Triager (triage_task.py) ---")
    triage_script = os.path.expanduser("~/projects/ai-os/scripts/triage_task.py")
    if os.path.exists(triage_script):
        t_out, t_code = run_cmd(["python3", triage_script, "--prompt", "preflight check"])
        if t_code == 0 and t_out:
            print(t_out)
        else:
            print("Task Triager: OK")

    # 1d. LiteLLM Model Stack Context Dump
    print("\n--- LiteLLM Model Stack Header ---")
    model_parser = os.path.expanduser("~/projects/ai-os/scripts/parse_litellm_models.py")
    if os.path.exists(model_parser):
        hdr_out, code_hdr = run_cmd(["python3", model_parser, "--header"])
        if code_hdr == 0 and hdr_out:
            print(hdr_out)
        else:
            print("LiteLLM Header parse: WARNING (Failed to parse header)")
    else:
        print("parse_litellm_models.py missing.")

    # 2. Rules Build & Sync
    print("\n--- Running Rules Bundler (build_rules.py) ---")
    rules_script = os.path.expanduser("~/projects/ai-os/scripts/build_rules.py")
    if os.path.exists(rules_script):
        out_r, code_r = run_cmd(["python3", rules_script])
        if code_r == 0:
            print("rules status: OK (CLAUDE.md & GEMINI.md built)")
        else:
            print("rules status: WARNING (build_rules.py failed)")

    # 3. Git Pull
    print("\n--- Running Git Pull ---")
    if os.path.exists(".git"):
        _, diff_code = run_cmd(["git", "diff", "--quiet"])
        _, status_code = run_cmd(["git", "diff", "--cached", "--quiet"])
        if diff_code != 0 or status_code != 0:
            print("Local uncommitted work detected. Running `git pull --rebase`...")
            pull_out, pull_code = run_cmd(["git", "pull", "--rebase"])
        else:
            print("Running `git pull`...")
            pull_out, pull_code = run_cmd(["git", "pull"])
        print(pull_out if pull_out else "Git pull finished.")

    # 4. Thread Bloat Check
    print("\n--- Running Thread Bloat Check (check_thread_bloat.py) ---")
    bloat_script = os.path.expanduser("~/projects/ai-os/scripts/check_thread_bloat.py")
    if os.path.exists(bloat_script):
        b_out, code_b = run_cmd(["python3", bloat_script, "-j"])
        if code_b == 0 and b_out:
            try:
                import json
                b_data = json.loads(b_out)
                t_sys = b_data.get("t_sys", 0)
                t_hist = b_data.get("t_hist", 0)
                t_thresh = b_data.get("t_hist_threshold", 0)
                is_bloated = b_data.get("is_bloated", False)
                status_str = "WARNING (Bloated)" if is_bloated else "OK"
                print(f"thread bloat status: {status_str} [T_sys: {t_sys}, T_hist: {t_hist}/{t_thresh}]")
            except Exception:
                print("thread bloat status: OK")
        else:
            print("thread bloat status: OK")

if __name__ == "__main__":
    main()
