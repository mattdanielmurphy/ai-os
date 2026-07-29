#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jules_quota import get_jules_status
from compile_dynamic_prompt import compile_prompt

def evaluate_triage(prompt, files=None):
    prompt_lower = prompt.lower()
    files = files or []

    # 1. Inspect Quotas
    jules_status = get_jules_status()
    jules_avail = jules_status.get("total_remaining", 0) if jules_status.get("status") == "OK" else 0

    ag_quota_snapshot = {}
    snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path) as f:
                ag_quota_snapshot = json.load(f)
        except Exception:
            pass

    # Evaluate local quota pressure
    low_local_quota = any(val < 0.20 for val in ag_quota_snapshot.values()) if ag_quota_snapshot else True

    # 2. Keyword & Task Characteristic Matching
    keywords_heavy = ["refactor", "unit test", "tests", "boilerplate", "migrate", "docs", "documentation", "feature"]
    keywords_quick = ["typo", "fix typo", "rename", "format", "single line", "bugfix"]

    is_heavy_task = any(kw in prompt_lower for kw in keywords_heavy) or len(files) > 3
    is_quick_task = any(kw in prompt_lower for kw in keywords_quick) and len(files) <= 1

    # 3. Decision Matrix
    compiled_prompt = compile_prompt(role="orchestrator", platform="antigravity", prompt_text=prompt)
    decision = {
        "engine": "local",
        "recommended_model": "muse-spark-1.1",
        "use_jules": False,
        "jules_fanout": False,
        "auto_context_files": [],
        "reasoning": [],
        "compiled_system_prompt": compiled_prompt,
        "compiled_system_prompt_len": len(compiled_prompt)
    }

    # Context Mapping
    if "mac" in prompt_lower or "hammerspoon" in prompt_lower or "launchagent" in prompt_lower:
        mac_doc = os.path.expanduser("~/projects/ai-os/docs/MAC_ENVIRONMENT.md")
        if os.path.exists(mac_doc):
            decision["auto_context_files"].append(mac_doc)
            decision["reasoning"].append("Auto-injected MAC_ENVIRONMENT.md context based on macOS/system keywords.")

    ag_ctx = os.path.expanduser("~/projects/ai-os/AG_CONTEXT.md")
    if os.path.exists(ag_ctx):
        decision["auto_context_files"].append(ag_ctx)

    # Routing Logic
    if is_heavy_task and jules_avail > 0:
        decision["engine"] = "jules"
        decision["use_jules"] = True
        decision["recommended_model"] = "jules-remote"
        if len(files) > 2 or "parallel" in prompt_lower or "bulk" in prompt_lower:
            decision["jules_fanout"] = True
            decision["reasoning"].append(f"Heavy/bulk task detected. Offloading to Jules Parallel Fan-Out (Jules quota: {jules_avail} remaining).")
        else:
            decision["reasoning"].append(f"Heavy task detected. Offloading to Jules to conserve local Pro quota (Jules quota: {jules_avail} remaining).")
        decision["reasoning"].append("RECOMMENDATION: Preflight suggests Jules offloading. DO NOT AUTO-OFFLOAD. STOP AND ASK THE USER FOR CONFIRMATION.")
    elif low_local_quota and jules_avail > 0 and not is_quick_task:
        decision["engine"] = "jules"
        decision["use_jules"] = True
        decision["recommended_model"] = "jules-remote"
        decision["reasoning"].append("Local Pro quota is LOW. Delegating task to Jules.")
        decision["reasoning"].append("RECOMMENDATION: Preflight suggests Jules offloading. DO NOT AUTO-OFFLOAD. STOP AND ASK THE USER FOR CONFIRMATION.")
    elif is_quick_task:
        decision["engine"] = "local"
        decision["recommended_model"] = "gemini-3.5-flash-lite"
        decision["reasoning"].append("Quick inline micro-edit detected. Executing locally on fast Flash-Lite tier.")
    else:
        decision["engine"] = "local"
        decision["recommended_model"] = "muse-spark-1.1"
        decision["reasoning"].append("Standard interactive task. Executing locally via primary daily driver model.")

    if decision["use_jules"]:
        rec_msg = "RECOMMENDATION: Preflight suggests Jules offloading. DO NOT AUTO-OFFLOAD. STOP AND ASK THE USER FOR CONFIRMATION."
        if rec_msg not in decision["reasoning"]:
            decision["reasoning"].append(rec_msg)

    return decision

def main():
    parser = argparse.ArgumentParser(description="Automated Task Triaging Engine")
    parser.add_argument("--prompt", required=True, help="User prompt or task description")
    parser.add_argument("--files", nargs="*", help="Files involved in task")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()
    decision = evaluate_triage(args.prompt, args.files)

    if args.json:
        print(json.dumps(decision, indent=2))
    else:
        print("=== TASK TRIAGE DECISION ===")
        print(f"Recommended Engine: {decision['engine'].upper()} ({decision['recommended_model']})")
        print(f"Use Jules: {decision['use_jules']} (Fan-out: {decision['jules_fanout']})")
        if decision["auto_context_files"]:
            print(f"Auto-Injected Context: {', '.join([os.path.basename(f) for f in decision['auto_context_files']])}")
        print("Reasoning:")
        for r in decision["reasoning"]:
            print(f"  - {r}")

if __name__ == "__main__":
    main()
