#!/usr/bin/env python3
import json
import os
import sys
import time
import datetime
import argparse
from pathlib import Path

# Add parent directory to sys.path to import telemetry_db
sys.path.append(str(Path(__file__).parent))
try:
    import telemetry_db
except ImportError:
    # Fallback if telemetry_db is in the same directory but sys.path isn't updated
    pass

LIMIT_5H = 50
LIMIT_WEEK = 200

def get_stats():
    db = telemetry_db.load_db()
    sub_model_costs = db.get("sub_model_costs", [])
    agy_turns = db.get("agy_turns", [])
    
    now = time.time()
    ten_minutes_ago = now - 600
    
    # Calculate midnight today (local time)
    local_midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    
    cost_turn = 0.0
    cost_total = 0.0
    
    for item in sub_model_costs:
        ts = item.get("timestamp", 0)
        cost = item.get("calculated_cost", 0.0)
        if ts >= ten_minutes_ago:
            cost_turn += cost
        if ts >= local_midnight:
            cost_total += cost
            
    return cost_turn, cost_total, agy_turns

def main():
    parser = argparse.ArgumentParser(description="AI-OS Smart Cost Reporter")
    parser.add_argument("--agent", choices=["agy", "claude"], default="claude", help="Agent type to report for")
    args = parser.parse_args()
    
    if args.agent == "agy":
        # Log a new AGY turn first
        telemetry_db.log_agy_turn()
        
        # Calculate stats
        cost_turn, cost_total, agy_turns = get_stats()
        
        now = time.time()
        five_hours_ago = now - (5 * 3600)
        seven_days_ago = now - (7 * 24 * 3600)
        
        turns_5h = sum(1 for ts in agy_turns if ts >= five_hours_ago)
        turns_week = sum(1 for ts in agy_turns if ts >= seven_days_ago)
        
        rem_5h = max(0, LIMIT_5H - turns_5h)
        rem_week = max(0, LIMIT_WEEK - turns_week)
        
        print("[AGY TELEMETRY]")
        print(f"Delegated Sub-Model Cost (Turn): ${cost_turn:.4f}")
        print(f"Delegated Sub-Model Cost (Total): ${cost_total:.4f}")
        print(f"AGY Quota Remaining (5hr): {rem_5h}/{LIMIT_5H}")
        print(f"AGY Quota Remaining (Weekly): {rem_week}/{LIMIT_WEEK}")
        
    else:  # claude
        cost_turn, cost_total, _ = get_stats()
        print(f"[TELEMETRY] Sub-Model Cost This Turn: ${cost_turn:.4f} | Total Delegated Cost: ${cost_total:.4f}")

if __name__ == "__main__":
    main()