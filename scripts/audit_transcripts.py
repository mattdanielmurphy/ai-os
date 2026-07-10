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
            return int(len(encoding.encode(text)))
        except Exception:
            pass
    except ImportError:
        pass
    return int(max(1, len(text) // 3.5))

def get_step_text(step):
    source = step.get("source")
    step_type = step.get("type")
    content = step.get("content") or ""
    thinking = step.get("thinking") or ""
    tool_calls = step.get("tool_calls") or []
    
    parts = []
    if step_type == "USER_INPUT":
        parts.append(f"=== USER INPUT ===\n{content}")
    elif step_type == "CONVERSATION_HISTORY":
        parts.append(f"=== SYSTEM CONVERSATION HISTORY ===\n{content}")
    elif step_type == "SYSTEM_MESSAGE":
        parts.append(f"=== SYSTEM MESSAGE ===\n{content}")
    elif step_type == "KNOWLEDGE_ARTIFACTS":
        parts.append(f"=== SYSTEM KNOWLEDGE ARTIFACTS ===\n{content}")
    elif step_type == "PLANNER_RESPONSE":
        if thinking:
            parts.append(f"=== MODEL THOUGHTS ===\n{thinking}")
        if tool_calls:
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("arguments") or tc.get("args") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                parts.append(f"=== MODEL TOOL CALL: {name} ===\n{json.dumps(args, indent=2)}")
        if content:
            parts.append(f"=== MODEL RESPONSE ===\n{content}")
    elif content:
        parts.append(f"=== TOOL OUTPUT ({step_type}) ===\n{content}")
        
    return "\n\n".join(parts)

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
    step_tokens_list = []
    compressed_transcript_parts = []
    step_breakdowns = []
    
    cumulative_input_tokens = 0
    cumulative_output_tokens = 0
    
    # Pre-calculate token size of each step
    for step in steps:
        step_text = get_step_text(step)
        step_tokens_list.append(estimate_tokens(step_text))

    for i, step in enumerate(steps):
        step_idx = step.get("step_index", i)
        source = step.get("source")
        step_type = step.get("type")
        content = step.get("content") or ""
        thinking = step.get("thinking") or ""
        tool_calls = step.get("tool_calls") or []
        
        step_tokens = int(step_tokens_list[i])
        
        # Build human-readable formatted representation for the compressed transcript
        formatted_parts = []
        if step_type == "USER_INPUT":
            formatted_parts.append(f"### Step {step_idx} (USER)\n{content}")
        elif step_type == "CONVERSATION_HISTORY":
            formatted_parts.append(f"### Step {step_idx} (SYSTEM - CONVERSATION HISTORY)\n```markdown\n{content[:1000] + '...' if len(content) > 1000 else content}\n```")
        elif step_type == "SYSTEM_MESSAGE":
            formatted_parts.append(f"### Step {step_idx} (SYSTEM MESSAGE)\n{content}")
        elif step_type == "KNOWLEDGE_ARTIFACTS":
            formatted_parts.append(f"### Step {step_idx} (SYSTEM - KNOWLEDGE ARTIFACTS)\n{content or '*Empty*'}")
        elif step_type == "PLANNER_RESPONSE":
            formatted_parts.append(f"### Step {step_idx} (GEMINI)")
            if thinking:
                formatted_parts.append(f"**Thinking:**\n> " + thinking.replace("\n", "\n> "))
            if tool_calls:
                for tc in tool_calls:
                    name = tc.get("name")
                    args = tc.get("arguments") or tc.get("args") or {}
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            pass
                    formatted_parts.append(f"**Tool Call:** \n- Name: `{name}`\n- Args:\n```json\n{json.dumps(args, indent=2)}\n```")
            if content:
                formatted_parts.append(f"**Response:**\n{content}")
        elif content:
            formatted_parts.append(f"### Step {step_idx} (TOOL OUTPUT - {step_type})\n```\n{content[:2000] + '...' if len(content) > 2000 else content}\n```")
            
        if formatted_parts:
            compressed_transcript_parts.append("\n\n".join(formatted_parts))
            
        # Context calculation: prompt at this step is the concatenation of all previous steps
        context_tokens = int(sum(step_tokens_list[:i])) if step_type == "PLANNER_RESPONSE" else 0
        
        if step_type == "PLANNER_RESPONSE":
            cumulative_input_tokens += context_tokens
            cumulative_output_tokens += step_tokens
            
        # Get brief content summary
        summary = ""
        if step_type == "USER_INPUT":
            summary = content.strip().replace("\n", " ")[:60]
        elif step_type == "PLANNER_RESPONSE":
            if tool_calls:
                summary = f"Tool Calls: " + ", ".join([tc.get("name") for tc in tool_calls])
            else:
                summary = content.strip().replace("\n", " ")[:60]
        elif content:
            summary = content.strip().replace("\n", " ")[:60]
            
        step_breakdowns.append({
            "step": step_idx,
            "source": source,
            "type": step_type,
            "tokens": int(step_tokens),
            "context_tokens": int(context_tokens),
            "summary": summary
        })

        # Analyze tool calls for direct read/write/delegate reporting
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
                # Detect shell redirects for direct_writes
                if ">" in cmd or ">>" in cmd or "<<" in cmd:
                    try:
                        # Attempt to find the target path, handling different redirect types
                        parts = cmd.split('>')
                        if len(parts) > 1:
                            path_str = parts[-1].strip()
                            path_parts = path_str.split(' ')
                            # Take the first part if there are multiple elements after the redirect
                            # More robust check for actual command followed by redirect
                            # This is a heuristic to prevent false positives from generic '>' in commands.
                            # We look for common patterns like 'echo ... > file', 'cat ... >> file', etc.
                            command_prefix = parts[0].strip()
                            if command_prefix.startswith(("echo ", "cat ", "python -c", "sh -c")):
                                target_path = path_parts[0] if path_parts else ''
                            else:
                                target_path = '' # Not a recognized direct write command

                        else: # Handle << for heredocs, etc., though less common for direct writes from shell
                            # Handle << for heredocs, etc. This is more complex as the redirect is often at the end.
                            # Look for patterns like 'cmd << EOF > file' or 'cmd > file << EOF'
                            if '<<' in cmd and '>' in cmd:
                                # Check for command leveraging heredoc then redirect
                                cmd_parts = cmd.split('>')
                                if len(cmd_parts) > 1:
                                    # Assume redirect target is the last part if it looks like a file path
                                    potential_path = cmd_parts[-1].strip()
                                    # Basic check: if it doesn't contain spaces and looks like a path
                                    if ' ' not in potential_path and potential_path not in ('&1', '&2', '/dev/null'):
                                        target_path = potential_path
                                    else:
                                        target_path = ''
                                else:
                                    target_path = ''
                            else:
                                target_path = '' # No clear heredoc-based redirect to a file

                            target_path = parts[-1].strip().split(' ')[0] if len(parts) > 1 else ''

                        if target_path:
                            direct_writes.append({
                                "step": step_idx,
                                "tool": "run_command (Shell Redirect)",
                                "path": target_path,
                                "args": {"CommandLine": cmd}
                            })
                            continue # Skip further processing for this run_command as it's a direct write
                    except (IndexError, AttributeError):
                        # Gracefully handle cases where parsing fails
                        pass

                if "mechanical_editor" in cmd or "auto_commit" in cmd or "housekeep" in cmd:
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

        # Keep legacy token waste calculations
        is_direct_read_result = False
        if step_type in ["VIEW_FILE", "READ_FILE"] or (source == "MODEL" and step_type == "VIEW_FILE"):
            is_direct_read_result = True

        if is_direct_read_result and step_tokens > 0:
            remaining_steps = total_steps - 1 - i
            waste = step_tokens * remaining_steps
            cumulative_waste_tokens += waste
            if direct_reads:
                direct_reads[-1]["tokens"] = int(step_tokens)
                direct_reads[-1]["remaining_steps"] = int(remaining_steps)
                direct_reads[-1]["cumulative_waste"] = int(waste)

    plain_text_size = sum(step_tokens_list)

    return {
        "file": filepath,
        "total_steps": total_steps,
        "direct_reads": direct_reads,
        "direct_writes": direct_writes,
        "delegated_calls": delegated_calls,
        "other_calls": other_calls,
        "cumulative_waste_tokens": int(cumulative_waste_tokens),
        "cumulative_input_tokens": int(cumulative_input_tokens),
        "cumulative_output_tokens": int(cumulative_output_tokens),
        "total_gemini_tokens": int(cumulative_input_tokens + cumulative_output_tokens),
        "plain_text_size": int(plain_text_size),
        "step_breakdowns": step_breakdowns,
        "compressed_transcript": "\n\n---\n\n".join(compressed_transcript_parts)
    }

def print_markdown_report(audit):
    if not audit:
        return

    print(f"# Transcript Audit Report: {Path(audit['file']).name}")
    print(f"\n- **Total Steps**: {audit['total_steps']}")
    print(f"- **Direct File Reads (view_file)**: {len(audit['direct_reads'])}")
    print(f"- **Direct File Writes/Edits**: {len(audit['direct_writes'])}")
    print(f"- **Delegated Tasks (mechanical_editor, etc.)**: {len(audit['delegated_calls'])}")
    print(f"- **Estimated Cumulative Token Waste (from direct reads)**: {int(audit['cumulative_waste_tokens']):,} tokens")
    print(f"- **Total Gemini Tokens Consumed (API Cost)**: {int(audit['total_gemini_tokens']):,} tokens")
    print(f"  - **Input Context (Cumulative)**: {int(audit['cumulative_input_tokens']):,} tokens")
    print(f"  - **Output Generation (Thoughts/Tools)**: {int(audit['cumulative_output_tokens']):,} tokens")
    print(f"- **Plain Text Conversation Size**: {int(audit['plain_text_size']):,} tokens")
    print("\n---")

    print("\n## Step-by-Step Token Breakdown")
    print("| Step | Source | Type / Action | Size (Tokens) | Context Size (Tokens) | Summary |")
    print("|------|--------|---------------|---------------|-----------------------|---------|")
    for s in audit["step_breakdowns"]:
        print(f"| {s['step']} | {s['source']} | {s['type']} | {int(s['tokens']):,} | {int(s['context_tokens']):,} | `{s['summary']}` |")

    print("\n---")

    if audit["direct_reads"]:
        print("\n## Direct File Reads")
        print("| Step | Tool | Path | Size (Tokens) | Subsequent Steps | Cumulative Waste |")
        print("|------|------|------|---------------|------------------|------------------|")
        for r in audit["direct_reads"]:
            tokens = r.get("tokens", 0)
            rem = r.get("remaining_steps", 0)
            waste = r.get("cumulative_waste", 0)
            print(f"| {r['step']} | {r['tool']} | `{r['path']}` | {int(tokens):,} | {int(rem):,} | {int(waste):,} |")
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

    print("\n---")
    print("\n## Compressed Conversation Transcript")
    print("\n<details>")
    print(f"<summary>Expand to view plain text transcript ({int(audit['plain_text_size']):,} tokens)</summary>\n")
    print(audit['compressed_transcript'])
    print("\n</details>")

def find_most_recent_transcript():
    search_paths = [
        Path('/Users/matt/.gemini/antigravity-ide/brain'),
        Path('/Users/matt/.gemini/antigravity-cli/brain')
    ]

    transcript_files = []
    for sp in search_paths:
        if sp.exists() and sp.is_dir():
            transcript_files.extend(sp.rglob('transcript.jsonl'))
            transcript_files.extend(sp.rglob('transcript_full.jsonl'))

    if not transcript_files:
        return None

    # Sort by modification time, most recent first
    transcript_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return transcript_files[0]

def main():
    parser = argparse.ArgumentParser(description="Audit transcript for token waste.")
    parser.add_argument("transcript_path", nargs='?', help="Path to transcript.jsonl or transcript_full.jsonl (optional)")
    args = parser.parse_args()

    transcript_to_audit = args.transcript_path
    if not transcript_to_audit:
        most_recent_transcript = find_most_recent_transcript()
        if most_recent_transcript:
            print(f"Auditing most recent transcript: {most_recent_transcript}")
            transcript_to_audit = str(most_recent_transcript)
        else:
            print("Error: No transcript_path provided and no recent transcripts found.", file=sys.stderr)
            sys.exit(1)

    audit = audit_transcript(transcript_to_audit)
    if audit:
        print_markdown_report(audit)

if __name__ == "__main__":
    main()
