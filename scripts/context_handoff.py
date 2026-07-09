#!/usr/bin/env python3
import argparse
import sys
import os
import datetime

def main():
    parser = argparse.ArgumentParser(description="Create context handoff logs for agent state transmission.")
    parser.add_argument("--goal", required=True, help="The current user goal")
    parser.add_argument("--completed", required=True, help="What has been completed so far")
    parser.add_argument("--next_steps", required=True, help="The next steps to execute")
    parser.add_argument("--discoveries", required=True, help="Key architectural discoveries or info")

    args = parser.parse_args()

    # Ensure log dir exists
    log_dir = "/Users/matt/projects/ai-os/agent-logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate filename YYYY-MM-DD_HH-MM_handoff.md
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M_handoff.md")
    filepath = os.path.join(log_dir, filename)

    # Look for the transcript file
    import json
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
{args.goal}

## Completed So Far
<!-- INDEXED HANDOFF PROTOCOL: Be succinct. Write a 1-sentence summary per step with step_<id> reference. Store granular details in agent-logs/details/step_<timestamp_or_id>.md -->
{args.completed}

## Next Steps
{args.next_steps}

## Discoveries
{args.discoveries}
{transcript_pointer}"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


    print(f"HANDOFF_FILE_PATH={filepath}")

if __name__ == "__main__":
    main()
