#!/usr/bin/env python3
"""
triage_task.py - Automated Task Triaging and Delegation Evaluator for ai-os

Evaluates incoming user tasks against local quota and task complexity to determine
whether to route to agy (default for substantive work with healthy quota) or keep
direct in ChatGPT / local engine.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from triage_router import evaluate_routing, format_routing_visibility
from compile_dynamic_prompt import compile_prompt


def evaluate_triage(prompt: str, files=None, role: str = "orchestrator", mock_quota_status: str = None) -> dict:
    files = files or []
    decision = evaluate_routing(prompt, mock_quota_status=mock_quota_status)

    compiled_prompt = compile_prompt(role=role, platform="antigravity", prompt_text=prompt)

    reasoning = [
        f"Backend selected: {decision['backend']} ({decision['selection_method']})",
        f"Quota status: {decision['quota_status']} ({decision['quota_details']})",
    ]

    if decision.get("override_reason"):
        reasoning.append(f"Override reason: {decision['override_reason']}")
    elif decision.get("is_lightweight"):
        reasoning.append(f"Lightweight request detected: {decision['lightweight_reason']} -> keeping direct in ChatGPT.")
    elif decision.get("fallback_occurred"):
        reasoning.append(f"Substantive request fell back to direct ChatGPT: {decision['fallback_reason']}.")
    else:
        reasoning.append("Substantive request routed to agy as default capable reasoning/execution agent.")

    if decision.get("thin_handoff"):
        reasoning.append("Thin handoff generated with verbatim request and repository context.")

    result = {
        "engine": decision["backend"],
        "recommended_model": decision["model"],
        "backend": decision["backend"],
        "selection_method": decision["selection_method"],
        "quota_status": decision["quota_status"],
        "remaining_fraction": decision["remaining_fraction"],
        "fallback_occurred": decision["fallback_occurred"],
        "fallback_reason": decision["fallback_reason"],
        "is_lightweight": decision["is_lightweight"],
        "lightweight_reason": decision["lightweight_reason"],
        "thin_handoff": decision["thin_handoff"],
        "reasoning": reasoning,
        "routing_visibility": format_routing_visibility(decision),
        "compiled_system_prompt": compiled_prompt,
        "compiled_system_prompt_len": len(compiled_prompt),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Automated Task Triaging Engine")
    parser.add_argument("--prompt", required=True, help="User prompt or task description")
    parser.add_argument("--files", nargs="*", help="Files involved in task")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()
    decision = evaluate_triage(args.prompt, args.files)

    if args.json:
        print(json.dumps(decision, indent=4))
    else:
        print(f"Recommended Model: {decision.get('recommended_model', 'N/A')}")
        print(f"Engine: {decision.get('engine', 'N/A')}")
        print("Reasoning:")
        for r in decision.get("reasoning", []):
            print(f"  - {r}")


if __name__ == "__main__":
    main()
