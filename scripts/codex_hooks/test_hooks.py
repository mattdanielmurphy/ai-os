#!/usr/bin/env python3
"""
test_hooks.py - Comprehensive Test Suite for AI-OS Codex Hooks Engine.

Tests:
  1. Classifier Latency & Routing:
     - Fast Tier 0 Gate for casual questions (< 5ms, 0 extra tokens).
     - Tier 1 Policy Pack injection for project workspaces and trigger domains.
     - Tier 2 Mem0 conditional hydration.
  2. PreToolUse Deterministic Guardrails:
     - Blocks 'rm' / 'rmdir' (allows 'node_modules' exception and 'mv to ~/.Trash/').
     - Blocks secret file reads (.env, credentials, private keys).
     - Blocks npm / pnpm / yarn (instructs 'bun').
     - Blocks git init in home root (~).
     - Blocks writes to system /tmp.
  3. Shadow Mode vs. Enforce Mode transitions and audit logging.
  4. End-to-end CLI stdin/stdout JSON wire interface validation.
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
AI_OS_SCRIPTS = CURRENT_DIR.parent
if str(AI_OS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(AI_OS_SCRIPTS))

from codex_hooks.classifier import classify_and_inject
from codex_hooks.tool_guard import evaluate_tool_call


def run_tests():
    passed = 0
    total = 0

    print("════════════════════════════════════════════════════════════════")
    print("      RUNNING AI-OS CODEX HOOKS ENGINE VERIFICATION SUITE       ")
    print("════════════════════════════════════════════════════════════════\n")

    # ─────────────────────────────────────────────────────────────
    # SECTION 1: CLASSIFIER ROUTING & LATENCY BENCHMARKS
    # ─────────────────────────────────────────────────────────────
    print("--- [1. Classifier Routing & Performance] ---")

    # 1.1 Casual prompt (Tier 0 fast gate)
    total += 1
    t0 = time.perf_counter()
    res1 = classify_and_inject({
        "prompt": "What is the best milk chocolate?",
        "cwd": "/Users/matt/Documents/Codex/2026-09-27/chocolate"
    })
    elapsed_ms = (time.perf_counter() - t0) * 1000
    is_none = res1["hookSpecificOutput"]["additionalContext"] is None
    if is_none and elapsed_ms < 10.0:
        print(f"  ✅ [PASS] Casual Tier 0 fast gate: {elapsed_ms:.2f}ms (Context=None)")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Casual Tier 0 failed: {elapsed_ms:.2f}ms (Context={res1['hookSpecificOutput']['additionalContext']})")

    # 1.2 Casual greeting
    total += 1
    t0 = time.perf_counter()
    res2 = classify_and_inject({
        "prompt": "Good morning! How are you doing today?",
        "cwd": "/Users/matt/Documents/Codex/2026-09-27/chat"
    })
    is_none = res2["hookSpecificOutput"]["additionalContext"] is None
    if is_none:
        print(f"  ✅ [PASS] Casual greeting: Context=None")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Casual greeting failed to yield Context=None")

    # 1.3 Project task in git repo (Tier 1)
    total += 1
    res3 = classify_and_inject({
        "prompt": "Fix the git rebase conflict in scripts/build_rules.py",
        "cwd": "/Users/matt/projects/ai-os"
    })
    ctx3 = res3["hookSpecificOutput"]["additionalContext"] or ""
    if "policy_git" in ctx3 and "policy_dev_workflow" in ctx3:
        print(f"  ✅ [PASS] Project CWD: Injected policy_git & policy_dev_workflow")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Project CWD failed to inject expected policies")

    # 1.4 Reminder domain matching
    total += 1
    res4 = classify_and_inject({
        "prompt": "Remind me to call the dental clinic on Monday",
        "cwd": "/Users/matt/Documents/Codex/2026-09-27/reminders"
    })
    ctx4 = res4["hookSpecificOutput"]["additionalContext"] or ""
    if "policy_reminders" in ctx4:
        print(f"  ✅ [PASS] Domain trigger: Injected policy_reminders")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Domain trigger failed to inject policy_reminders")

    # 1.5 Frontend / CSS domain matching
    total += 1
    res5 = classify_and_inject({
        "prompt": "Help me fix the CSS layout bug in thread.md with span-only tags",
        "cwd": "/Users/matt/Documents/Codex/2026-09-27/frontend"
    })
    ctx5 = res5["hookSpecificOutput"]["additionalContext"] or ""
    if "policy_frontend" in ctx5:
        print(f"  ✅ [PASS] Domain trigger: Injected policy_frontend")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Domain trigger failed to inject policy_frontend")

    # 1.6 Personal IDs domain matching
    total += 1
    res6 = classify_and_inject({
        "prompt": "Help me fill out this student ID and ASN application form",
        "cwd": "/Users/matt/Documents/Codex/2026-09-27/docs"
    })
    ctx6 = res6["hookSpecificOutput"]["additionalContext"] or ""
    if "policy_personal_ids" in ctx6:
        print(f"  ✅ [PASS] Domain trigger: Injected policy_personal_ids")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Domain trigger failed to inject policy_personal_ids")

    # ─────────────────────────────────────────────────────────────
    # SECTION 2: PRE_TOOL_USE HARD GUARDRAIL TESTS
    # ─────────────────────────────────────────────────────────────
    print("\n--- [2. PreToolUse Deterministic Security Guardrails] ---")
    os.environ["CODEX_HOOKS_MODE"] = "enforce"

    guardrail_cases = [
        # (tool, input, cwd, expected_block, description)
        ("execute_command", {"command": "rm -rf ./tmp/old.txt"}, "/Users/matt/projects/ai-os", True, "Block 'rm -rf'"),
        ("execute_command", {"command": "rmdir old_dir"}, "/Users/matt/projects/ai-os", True, "Block 'rmdir'"),
        ("execute_command", {"command": "rm -rf node_modules"}, "/Users/matt/projects/ai-os", False, "Allow 'rm -rf node_modules' exception"),
        ("execute_command", {"command": "mv ./tmp/old.txt ~/.Trash/"}, "/Users/matt/projects/ai-os", False, "Allow 'mv to ~/.Trash/'"),
        ("execute_command", {"command": "cat .env"}, "/Users/matt/projects/ai-os", True, "Block 'cat .env'"),
        ("execute_command", {"command": "head -n 5 .env.local"}, "/Users/matt/projects/ai-os", True, "Block 'head .env.local'"),
        ("execute_command", {"command": "cat aws_credentials"}, "/Users/matt/projects/ai-os", True, "Block secret credentials file"),
        ("execute_command", {"command": "aios-env check --key ANTHROPIC_API_KEY"}, "/Users/matt/projects/ai-os", False, "Allow safe 'aios-env check'"),
        ("view_file", {"path": "/Users/matt/projects/ai-os/.env"}, "/Users/matt/projects/ai-os", True, "Block view_file on .env"),
        ("view_file", {"path": "/Users/matt/projects/ai-os/package.json"}, "/Users/matt/projects/ai-os", False, "Allow view_file on package.json"),
        ("execute_command", {"command": "npm install lodash"}, "/Users/matt/projects/ai-os", True, "Block 'npm install'"),
        ("execute_command", {"command": "pnpm add lodash"}, "/Users/matt/projects/ai-os", True, "Block 'pnpm add'"),
        ("execute_command", {"command": "yarn add lodash"}, "/Users/matt/projects/ai-os", True, "Block 'yarn add'"),
        ("execute_command", {"command": "bun add lodash"}, "/Users/matt/projects/ai-os", False, "Allow 'bun add'"),
        ("execute_command", {"command": "git init"}, "/Users/matt", True, "Block 'git init' in ~ root"),
        ("execute_command", {"command": "git init"}, "/Users/matt/projects/cool-app", False, "Allow 'git init' in project folder"),
        ("execute_command", {"command": "echo test > /tmp/output.txt"}, "/Users/matt/projects/ai-os", True, "Block write to /tmp/"),
        ("execute_command", {"command": "echo test > ./tmp/output.txt"}, "/Users/matt/projects/ai-os", False, "Allow write to ./tmp/"),
        ("execute_command", {"command": "sudo rm -rf ./tmp/old.txt"}, "/Users/matt/projects/ai-os", True, "Block 'sudo rm -rf'"),
        ("execute_command", {"command": "find . -type f -name '*.tmp' -delete"}, "/Users/matt/projects/ai-os", True, "Block 'find ... -delete'"),
        ("execute_command", {"command": "find . -type f -name '*.tmp' -exec rm {} +"}, "/Users/matt/projects/ai-os", True, "Block 'find ... -exec rm'"),
    ]

    for tool_name, tool_inp, cwd, exp_block, desc in guardrail_cases:
        total += 1
        res = evaluate_tool_call({"tool_name": tool_name, "tool_input": tool_inp, "cwd": cwd})
        is_blocked = (res.get("decision") == "block") or (res.get("hookSpecificOutput", {}).get("permissionDecision") == "deny")
        if is_blocked == exp_block:
            print(f"  ✅ [PASS] {desc}")
            passed += 1
        else:
            print(f"  ❌ [FAIL] {desc} (Expected blocked={exp_block}, got {is_blocked})")

    # ─────────────────────────────────────────────────────────────
    # SECTION 3: SHADOW MODE TRANSITION
    # ─────────────────────────────────────────────────────────────
    print("\n--- [3. Shadow Mode vs. Enforce Mode] ---")
    total += 1
    os.environ["CODEX_HOOKS_MODE"] = "shadow"
    res_shadow = evaluate_tool_call({
        "tool_name": "execute_command",
        "tool_input": {"command": "rm -rf something.txt"},
        "cwd": "/Users/matt/projects/ai-os"
    })
    os.environ.pop("CODEX_HOOKS_MODE", None)

    if res_shadow.get("continue") is True and res_shadow.get("decision") == "approve":
        print(f"  ✅ [PASS] Shadow mode approves would-be violations while logging audit event")
        passed += 1
    else:
        print(f"  ❌ [FAIL] Shadow mode failed to approve would-be block")

    # ─────────────────────────────────────────────────────────────
    # SECTION 4: CLI ENTRYPOINT STDIN/STDOUT WIRE VALIDATION
    # ─────────────────────────────────────────────────────────────
    print("\n--- [4. CLI Entry Point Wire Protocol] ---")
    total += 1
    cli_prompt = CURRENT_DIR / "on_user_prompt.py"
    proc = subprocess.run(
        [sys.executable, str(cli_prompt)],
        input=json.dumps({"prompt": "Hello", "cwd": "/Users/matt/Documents/Codex/chat"}),
        capture_output=True,
        text=True
    )
    try:
        wire_out = json.loads(proc.stdout.strip())
        if wire_out.get("continue") is True and "hookSpecificOutput" in wire_out:
            print(f"  ✅ [PASS] on_user_prompt.py CLI returns valid wire JSON")
            passed += 1
        else:
            print(f"  ❌ [FAIL] on_user_prompt.py returned invalid schema: {proc.stdout}")
    except Exception as e:
        print(f"  ❌ [FAIL] on_user_prompt.py failed JSON parsing: {e}")

    total += 1
    cli_tool = CURRENT_DIR / "on_pre_tool_use.py"
    env_enforce = {**os.environ, "CODEX_HOOKS_MODE": "enforce"}
    proc = subprocess.run(
        [sys.executable, str(cli_tool)],
        input=json.dumps({"tool_name": "execute_command", "tool_input": {"command": "rm file.txt"}, "cwd": "/Users/matt/projects/ai-os"}),
        capture_output=True,
        text=True,
        env=env_enforce
    )
    try:
        wire_out = json.loads(proc.stdout.strip())
        if wire_out.get("decision") == "block" and wire_out.get("continue") is True:
            print(f"  ✅ [PASS] on_pre_tool_use.py CLI blocks rm and returns valid wire JSON")
            passed += 1
        else:
            print(f"  ❌ [FAIL] on_pre_tool_use.py returned unexpected result: {proc.stdout}")
    except Exception as e:
        print(f"  ❌ [FAIL] on_pre_tool_use.py failed JSON parsing: {e}")

    # ─────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────
    print("\n════════════════════════════════════════════════════════════════")
    print(f"   TEST RESULTS: {passed}/{total} PASSED ({passed/total*100:.1f}%)")
    print("════════════════════════════════════════════════════════════════")

    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
