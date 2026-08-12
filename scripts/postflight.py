#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

def main():
    parser = argparse.ArgumentParser(description="Two-stage async postflight and token formatter.")
    parser.add_argument("--agent", choices=["claude", "hermes", "antigravity"], default="antigravity", help="Agent type reporting metrics.")
    args, unknown = parser.parse_known_args()

    content = ""
    if not sys.stdin.isatty():
        content = sys.stdin.read().strip()
    
    if not content and unknown:
        content = " ".join(unknown).strip()
        
    try:
        from agent_tokens import get_tokens
        token_count, source = get_tokens(args.agent)
        metrics = f"\n\n**Thread Metrics:**\n- Total Tokens: {token_count} (source: {source})"
    except Exception:
        metrics = "\n\n**Thread Metrics:**\n- Total Tokens: 0 (source: error)"

    if content:
        final_output = content + metrics
    else:
        final_output = metrics

    print(final_output)

    async_script = os.path.join(SCRIPTS_DIR, "postflight_async.py")
    if os.path.exists(async_script):
        subprocess.Popen(
            [sys.executable, async_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

if __name__ == "__main__":
    main()
