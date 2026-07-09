#!/usr/bin/env python3
import os
import json
import sys
import argparse
from pathlib import Path

def estimate_tokens(text):
    if not text:
        return 0
    try:
        import tiktoken
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            pass
    except ImportError:
        pass
    return max(1, len(text) // 3.5)

def audit_transcript(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist.", file=sys.stderr)
        return None

    steps = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                steps.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line: {e}", file=sys.stderr)

    total_steps = len(steps)
    direct_reads = []
    direct_writes = []
    delegated_calls = []
    other_calls = []

    cumulative_waste_tokens = 0

    for i, step in enumerate(steps):
        step_idx = step.get("step_index", i)
        source = step.get("source")
        step_type = step.get("type")
        content = step.get("content") or ""
        tool_calls = step.get("tool_calls") or []

        # Analyze tool calls
        for tc in tool_calls:
            name = tc.get("name")
            args = tc.get("arguments") or tc.get("args") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass

            if name in ["view_file", "read_file"]:
                path = args.get("AbsolutePath") or args.get("TargetFile") or args.get("path") or ""
                direct_reads.append({
                    "step": step_idx,
                    "tool": name,
                    "path": path,
                    "args": args,
                    "tokens": 0,
                    "remaining_steps": 0,
                    "cumulative_waste": 0
                })
            elif name in ["write_to_file", "replace_file_content", "multi_replace_file_content", "write_file"]:
                path = args.get("TargetFile") or args.get("AbsolutePath") or args.get("path") or ""
                direct_writes.append({
                    "step": step_idx,
                    "tool": name,
                    "path": path,
                    "args": args
                })
            elif name in ["run_command"]:
                cmd = args.get("CommandLine") or ""
                # Check if it ran a delegator script
                if "mechanical_editor" in cmd or "auto_commit" in cmd:
                    delegated_calls.append({
                        "step": step_idx,
                        "tool": name,
                        "cmd": cmd
                    })
                else:
                    other_calls.append({
                        "step": step_idx,
                        "tool": name,
                        "cmd": cmd
                    })
            else:
                other_calls.append({
                    "step": step_idx,
                    "tool": name,
                    "args": args
                })

        # Calculate token cost of this step's output/content
        # If it was a tool output (like a file read), that content is loaded into the prompt context for ALL subsequent steps.
        step_tokens = estimate_tokens(content)
        
        is_direct_read_result = False
        if step_type in ["VIEW_FILE", "READ_FILE"] or (source == "MODEL" and step_type == "VIEW_FILE"):
            is_direct_read_result = True

        if is_direct_read_result and step_tokens > 0:
            # Remaining steps in the conversation that will carry this context
            remaining_steps = total_steps - 1 - i
            waste = step_tokens * remaining_steps
            cumulative_waste_tokens += waste
            if direct_reads:
                direct_reads[-1]["tokens"] = step_tokens
                direct_reads[-1]["remaining_steps"] = remaining_steps
                direct_reads[-1]["cumulative_waste"] = waste

    # Format the audit results
    return {
        "file": filepath,
        "total_steps": total_steps,
        "direct_reads": direct_reads,
        "direct_writes": direct_writes,
        "delegated_calls": delegated_calls,
        "other_calls": other_calls,
        "cumulative_waste_tokens": cumulative_waste_tokens
    }

def print_markdown_report(audit):
    if not audit:
        return

    print(f"# Transcript Audit Report: {Path(audit['file']).name}")
    print(f"\n- **Total Steps**: {audit['total_steps']}")
    print(f"- **Direct File Reads (view_file)**: {len(audit['direct_reads'])}")
    print(f"- **Direct File Writes/Edits**: {len(audit['direct_writes'])}")
    print(f"- **Delegated Tasks (mechanical_editor, etc.)**: {len(audit['delegated_calls'])}")
    print(f"- **Estimated Cumulative Token Waste (from direct reads)**: {audit['cumulative_waste_tokens']:,} tokens")
    print("\n---")

    if audit["direct_reads"]:
        print("\n## Direct File Reads")
        print("| Step | Tool | Path | Size (Tokens) | Subsequent Steps | Cumulative Waste |")
        print("|------|------|------|---------------|------------------|------------------|")
        for r in audit["direct_reads"]:
            tokens = r.get("tokens", 0)
            rem = r.get("remaining_steps", 0)
            waste = r.get("cumulative_waste", 0)
            print(f"| {r['step']} | {r['tool']} | `{r['path']}` | {tokens:,} | {rem} | {waste:,} |")
    else:
        print("\n## Direct File Reads\n*None! Great job adhering to the delegation rules.*")

    if audit["direct_writes"]:
        print("\n## Direct File Writes/Edits")
        print("| Step | Tool | Path |")
        print("|------|------|------|")
        for w in audit["direct_writes"]:
            print(f"| {w['step']} | {w['tool']} | `{w['path']}` |")
    else:
        print("\n## Direct File Writes/Edits\n*None! Great job.*")

    if audit["delegated_calls"]:
        print("\n## Delegated Task Calls")
        print("| Step | Tool | Command |")
        print("|------|------|---------|")
        for d in audit["delegated_calls"]:
            print(f"| {d['step']} | {d['tool']} | `{d['cmd']}` |")

def main():
    parser = argparse.ArgumentParser(description="Audit transcript for token waste.")
    parser.add_argument("transcript_path", help="Path to transcript.jsonl or transcript_full.jsonl")
    args = parser.parse_args()

    audit = audit_transcript(args.transcript_path)
    if audit:
        print_markdown_report(audit)

if __name__ == "__main__":
    main()
