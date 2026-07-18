#!/usr/bin/env python3
import os
import sys
import datetime
import json
import re

def get_in_progress_task():
    features_dir = "/Users/matt/projects/ai-os/.devtool/features"
    if not os.path.isdir(features_dir):
        return None, None

    for filename in os.listdir(features_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(features_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Simple frontmatter parser
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]
                    if 'status: "in-progress"' in frontmatter or 'status: in-progress' in frontmatter:
                        # Extract title from body
                        title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
                        title = title_match.group(1).strip() if title_match else filename
                        return filepath, title
        except Exception:
            pass
    return None, None

def update_task_status(filepath, new_status):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                # Replace status
                updated_frontmatter = re.sub(
                    r"status:\s*[\"']?[a-zA-Z0-9_-]+[\"']?",
                    f'status: "{new_status}"',
                    frontmatter
                )
                updated_content = f"---{updated_frontmatter}---{body}"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"Updated task status in {os.path.basename(filepath)} to '{new_status}'")
    except Exception as e:
        print(f"Error updating task status: {e}")

def get_multiline_input(prompt_text):
    print(prompt_text + " (Press Ctrl+D or type EOF on a blank line when done):")
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines).strip()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compile context and handover task execution to another agent instance.")
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompting the user.")
    parser.add_argument("--to-model", default="claude-fable-ds-v4-pro-med", help="Target model to spin up.")
    parser.add_argument("--completed", help="Details of what has been completed so far.")
    parser.add_argument("--next-steps", help="Details of what needs to be done next.")
    parser.add_argument("--discoveries", help="Any key discoveries or architecture notes.")
    parser.add_argument("--title", help="Optional title/goal override for this handoff.")
    args = parser.parse_args()

    # 1. Identify active task
    task_filepath, task_title = get_in_progress_task()
    
    if args.non_interactive:
        if args.title:
            task_title = args.title
        elif not task_title:
            task_title = "Automated Triage Handoff"
        is_completed = False
        completed = args.completed if args.completed else "N/A"
        next_steps = args.next_steps if args.next_steps else "N/A"
        discoveries = args.discoveries if args.discoveries else "N/A"
    else:
        if task_title:
            print(f"Detected Active Task: {task_title}")
        else:
            print("No active 'in-progress' task detected.")
            task_title = input("Enter a goal or title for this handoff: ").strip()
            if not task_title:
                task_title = "General Context Handoff"

        # 2. Ask if task is completed
        is_completed = False
        if task_filepath:
            complete_input = input("Has this task been fully completed? (y/N): ").strip().lower()
            if complete_input in ('y', 'yes'):
                is_completed = True

        # 3. Gather handoff details interactively
        completed = get_multiline_input("What has been completed so far?")
        next_steps = get_multiline_input("What are the next steps?")
        discoveries = get_multiline_input("Any key discoveries or architecture notes?")

    # 4. Generate the handoff markdown file
    log_dir = "/Users/matt/projects/ai-os/agent-logs"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M_handoff.md")
    filepath = os.path.join(log_dir, filename)

    # Transcript pointer
    metadata_str = os.environ.get("ANTIGRAVITY_SOURCE_METADATA")
    transcript_pointer = ""
    if metadata_str:
        try:
            metadata = json.loads(metadata_str)
            conv_id = metadata.get("tool", {}).get("conversationId")
            if conv_id:
                paths_to_check = [
                    f"/Users/matt/.gemini/antigravity-ide/brain/{conv_id}/.system_generated/logs/transcript.jsonl",
                    f"/Users/matt/.gemini/antigravity-cli/brain/{conv_id}/.system_generated/logs/transcript.jsonl"
                ]
                for p in paths_to_check:
                    if os.path.exists(p):
                        transcript_pointer = f"\n[Full Transcript for this conversation](file://{p})\n"
                        break
        except Exception:
            pass

    content = f"""## Goal
{task_title}

## Completed So Far
{completed if completed else "N/A"}

## Next Steps
{next_steps if next_steps else "N/A"}

## Discoveries
{discoveries if discoveries else "N/A"}
{transcript_pointer}"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nCreated handoff log: {filepath}")

    # 5. Transition task status if completed
    if is_completed and task_filepath:
        update_task_status(task_filepath, "review")

    # 6. Execute process replacement with a fresh agy thread
    prompt_msg = f"Continuing task: {task_title}. Read the handoff log at file://{filepath} and execute the next steps."
    print(f"\nReplacing process with a fresh agy thread using model {args.to_model}...\nPrompt: {prompt_msg}\n")
    
    # Run execvp to replace the current shell/python process with agy
    os.execvp("agy", ["agy", "--model", args.to_model, "--prompt-interactive", prompt_msg])

if __name__ == "__main__":
    main()
