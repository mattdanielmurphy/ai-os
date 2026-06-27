#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path
import argparse

DB_PATH = Path.home() / ".ai-os-telemetry.json"

def load_db():
    if not DB_PATH.exists():
        return {"sub_model_costs": [], "agy_turns": []}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sub_model_costs": [], "agy_turns": []}

def save_db(data):
    tmp_path = DB_PATH.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(DB_PATH)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise e

def log_sub_model_cost(model: str, prompt_tokens: int, completion_tokens: int):
    # DeepSeek pricing: $0.14 / 1M input tokens, $0.28 / 1M output tokens
    input_rate = 0.14 / 1_000_000
    output_rate = 0.28 / 1_000_000
    calculated_cost = (prompt_tokens * input_rate) + (completion_tokens * output_rate)
    
    timestamp = time.time()
    db = load_db()
    if "sub_model_costs" not in db:
        db["sub_model_costs"] = []
    
    db["sub_model_costs"].append({
        "timestamp": timestamp,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "calculated_cost": calculated_cost
    })
    save_db(db)
    return calculated_cost

def log_agy_turn():
    db = load_db()
    if "agy_turns" not in db:
        db["agy_turns"] = []
    
    timestamp = time.time()
    db["agy_turns"].append(timestamp)
    save_db(db)
    return timestamp

def main():
    parser = argparse.ArgumentParser(description="Centralized AI OS Telemetry Database")
    parser.add_argument("--log-cost", action="store_true")
    parser.add_argument("--model", type=str, default="deepseek")
    parser.add_argument("--prompt-tokens", type=int)
    parser.add_argument("--completion-tokens", type=int)
    
    parser.add_argument("--log-turn", action="store_true")
    
    args = parser.parse_args()
    
    if args.log_cost:
        if args.prompt_tokens is None or args.completion_tokens is None:
            parser.error("--prompt-tokens and --completion-tokens are required with --log-cost")
        cost = log_sub_model_cost(args.model, args.prompt_tokens, args.completion_tokens)
        print(f"Logged cost: ${cost:.6f}")
    elif args.log_turn:
        ts = log_agy_turn()
        print(f"Logged AGY Turn at: {ts}")
    else:
        db = load_db()
        print(f"Sub-Model Cost Logs: {len(db.get('sub_model_costs', []))}")
        print(f"AGY Turn Logs: {len(db.get('agy_turns', []))}")

if __name__ == "__main__":
    main()
