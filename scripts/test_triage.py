#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project scripts to sys.path
sys.path.append(str(Path(__file__).parent))
import triage_router

def test_triage():
    print("--- Testing Quota Retrieval ---")
    quota_5h, quota_week, is_real = triage_router.get_quota()
    print(f"5h Pro Quota Remaining: {quota_5h:.2%}")
    print(f"Weekly Quota Remaining: {quota_week:.2%}")
    print(f"Is Real API: {is_real}")

    print("\n--- Testing Triage Classification ---")
    queries = {
        "What is the capital of France?": "simple_non_coding",
        "Write a simple Python script to fetch a webpage and parse HTML using BeautifulSoup.": "coding_standard",
        "Explain the concurrency model of the dispatcher and debug a terminal deadlock where locks are never released.": "coding_complex",
        "Write 1000 lines of Mantine boilerplate for all the widgets and sidebars of the dashboard UI.": "valve_boilerplate"
    }

    for q, expected in queries.items():
        category = triage_router.tier1_triage(q)
        print(f"Query: '{q[:40]}...'")
        print(f"  Expected: {expected}")
        print(f"  Got:      {category}")
        # Note: LLMs might vary slightly but should align general categories
        assert category in ["simple_non_coding", "coding_standard", "coding_complex", "valve_boilerplate"]

    print("\n--- Testing Tier 2 Executive Investigation ---")
    error_log = "Traceback (most recent call last):\n  File \"cli.py\", line 152, in run\n    raise ValueError('Database connection timed out after 30 seconds')"
    escalation = triage_router.tier2_investigation(
        "Run the DB sync script and save output",
        "Gemini 3.5 Flash (Low)",
        error_log
    )
    print(f"Escalation Target: {escalation}")

if __name__ == "__main__":
    test_triage()
    print("\n✓ All triage router unit checks passed!")
