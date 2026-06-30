#!/usr/bin/env python3
import sys
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="View untruncated historical thread logs for Personal AI OS.")
    parser.add_argument("thread_id", help="Full or partial thread ID (UUID)")
    parser.add_argument("--step", type=int, help="Show only a specific step index (1-based)")
    parser.add_argument("--last", type=int, help="Show only the last N steps")
    args = parser.parse_args()

    home = os.environ.get("HOME")
    if not home:
        print("Error: HOME environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    brain_dir = os.path.join(home, ".gemini", "antigravity-cli", "brain")
    if not os.path.exists(brain_dir):
        print(f"Error: Brain directory not found at {brain_dir}", file=sys.stderr)
        sys.exit(1)

    # Resolve partial thread ID
    matches = []
    for entry in os.listdir(brain_dir):
        if entry.startswith(args.thread_id):
            matches.append(entry)

    if not matches:
        # Check if the thread_id is actually a path or something else
        if os.path.exists(args.thread_id):
            thread_dir = args.thread_id
        else:
            print(f"Error: No thread ID matching '{args.thread_id}' found in {brain_dir}", file=sys.stderr)
            sys.exit(1)
    elif len(matches) > 1:
        print(f"Multiple matches found for '{args.thread_id}':", file=sys.stderr)
        for m in matches:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)
    else:
        thread_dir = os.path.join(brain_dir, matches[0])

    transcript_path = os.path.join(thread_dir, ".system_generated", "logs", "transcript_full.jsonl")
    if not os.path.exists(transcript_path):
        transcript_path = os.path.join(thread_dir, ".system_generated", "logs", "transcript.jsonl")

    if not os.path.exists(transcript_path):
        print(f"Error: No transcript file found for thread at {thread_dir}", file=sys.stderr)
        sys.exit(1)

    steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                steps.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not steps:
        print("Thread log is empty.")
        return

    # Filter steps
    if args.step is not None:
        idx = args.step - 1
        if idx < 0 or idx >= len(steps):
            print(f"Error: Step index {args.step} out of bounds (1 to {len(steps)}).", file=sys.stderr)
            sys.exit(1)
        steps = [steps[idx]]
    elif args.last is not None:
        steps = steps[-args.last:]

    # Output formatted steps
    for i, step in enumerate(steps):
        step_idx = step.get("step_index", i + 1)
        source = step.get("source", "UNKNOWN")
        step_type = step.get("type", "UNKNOWN")
        content = step.get("content", "")
        status = step.get("status", "DONE")
        tool_calls = step.get("tool_calls", [])

        print("=" * 80)
        print(f"Step {step_idx} | Source: {source} | Type: {step_type} | Status: {status}")
        print("=" * 80)

        if content:
            print(content)
            print()

        if tool_calls:
            print("Tool Calls:")
            for call in tool_calls:
                name = call.get("name", "unknown")
                c_args = call.get("args", {})
                print(f"  - Tool: {name}")
                print(f"    Arguments: {json.dumps(c_args, indent=4)}")
            print()

if __name__ == "__main__":
    main()
