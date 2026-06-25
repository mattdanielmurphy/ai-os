#!/usr/bin/env python3
"""
Track per-message OpenRouter cost by computing deltas from the credits endpoint.

Stores the last-known total usage in .last_usage so each invocation can
report the cost of the single exchange since the last call.
"""

import json
import os
import urllib.request
import urllib.error
import sys
from pathlib import Path

API_KEY = os.getenv("OPENROUTER_API_KEY")
STATE_FILE = Path(__file__).parent / ".last_usage"


def fetch_total_usage():
    """Return (total_usage, remaining_credits) from OpenRouter, or None on error."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers=headers,
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        return None, None

    data = body.get("data", {})
    total = data.get("total_usage")
    credits = data.get("total_credits")
    return total, credits


def main():
    if not API_KEY:
        print("⚠️  [Cost] OPENROUTER_API_KEY not set")
        return

    current, remaining_budget = fetch_total_usage()
    if current is None:
        print("⚠️  [Cost] Could not reach OpenRouter credits endpoint")
        return

    # Read previous total from state file
    previous = None
    if STATE_FILE.exists():
        try:
            previous = float(STATE_FILE.read_text().strip())
        except (ValueError, OSError):
            pass

    # Save current for next invocation
    STATE_FILE.write_text(str(current))

    if previous is None:
        print(f"── OpenRouter ──────────────────────")
        print(f"  Total usage:   ${current:.6f}")
        if remaining_budget is not None:
            print(f"  Remaining:     ${remaining_budget - current:.6f}")
        print(f"────────────────────────────────────")
        return

    delta = current - previous
    if delta < 0:
        # Usage reset or data issue — show running total
        print(f"── OpenRouter ──────────────────────")
        print(f"  Total usage:  ${current:.6f}")
        print(f"────────────────────────────────────")
        return

    print(f"── This Message ────────────────────")
    print(f"  Cost:        ${delta:.6f}")
    print(f"  Total spent: ${current:.6f}")
    if remaining_budget is not None:
        print(f"  Remaining:   ${remaining_budget - current:.6f}")
    print(f"────────────────────────────────────")


if __name__ == "__main__":
    main()