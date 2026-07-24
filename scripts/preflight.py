#!/usr/bin/env python3
import subprocess
import sys
import os

def run_cmd(args, check=False):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return res.stdout.strip(), res.returncode
    except Exception as e:
        return "", 1

def main():
    print("=== PRE-FLIGHT CHECK ===")
    
    # 1. Quota Check
    print("--- Running Quota Check (ag-quota) ---")
    out, code = run_cmd(["ag-quota", "--all", "-j"])
    if code == 0 and out:
        try:
            import json
            data = json.loads(out)
            warnings = []
            if isinstance(data, list):
                for acct in data:
                    email = acct.get("email") or acct.get("quota_summary", {}).get("Email", "unknown")
                    models = acct.get("quota_summary", {}).get("Models", [])
                    for m in models:
                        frac = m.get("RemainingFraction", 1)
                        is_ex = m.get("IsExhausted", False)
                        disp = m.get("DisplayName") or m.get("ModelID", "")
                        if is_ex or (isinstance(frac, (int, float)) and frac < 0.25):
                            warnings.append(f"{email} ({disp}): {frac*100:.0f}% remaining")
            if warnings:
                print(f"ag-quota status: WARNING - Low quota detected ({'; '.join(warnings[:3])})")
            else:
                print("ag-quota status: OK (Quota healthy)")
        except Exception:
            print("ag-quota status: OK")
    else:
        print("ag-quota execution skipped or produced no output.")

    # 2. Git Pull
    print("\n--- Running Git Pull ---")
    if os.path.exists(".git"):
        # Check uncommitted work
        _, diff_code = run_cmd(["git", "diff", "--quiet"])
        _, status_code = run_cmd(["git", "diff", "--cached", "--quiet"])
        if diff_code != 0 or status_code != 0:
            print("Local uncommitted work detected. Running `git pull --rebase`...")
            pull_out, pull_code = run_cmd(["git", "pull", "--rebase"])
        else:
            print("Running `git pull`...")
            pull_out, pull_code = run_cmd(["git", "pull"])
        print(pull_out if pull_out else "Git pull finished.")
    else:
        print("Not a git repository. Skipping git pull.")

if __name__ == "__main__":
    main()
