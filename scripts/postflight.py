#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
import select
from postflight_lib import compute_thread_metrics, format_metrics_table

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser(description="Postflight, token, and quota formatter.")
    parser.add_argument("--agent", choices=["claude", "hermes", "antigravity"], default="antigravity", help="Agent type.")
    parser.add_argument("--conv-id", default=None, help="Conversation ID.")
    args, unknown = parser.parse_known_args()

    content = ""
    if not sys.stdin.isatty():
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            content = sys.stdin.read().strip()

    if not content and unknown:
        content = " ".join(unknown).strip()

    conv_id = args.conv_id or os.environ.get("CONVERSATION_ID") or os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if not conv_id:
        try:
            from check_thread_bloat import find_transcript_file
            from pathlib import Path
            t_path = find_transcript_file()
            if t_path:
                conv_id = Path(t_path).parent.parent.parent.name
        except Exception:
            pass

    metrics = compute_thread_metrics(conv_id=conv_id, agent=args.agent)
    metrics_table = format_metrics_table(metrics, conv_id=conv_id)

    final_output = metrics_table
    if content:
        from link_formatter import enrich_file_links
        final_output = enrich_file_links(content + final_output)
    else:
        from link_formatter import enrich_file_links
        final_output = enrich_file_links(final_output)

    print(final_output)

if __name__ == "__main__":
    main()
