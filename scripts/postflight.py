#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
import select

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

def main():
    parser = argparse.ArgumentParser(description="Two-stage async postflight, token, and quota formatter.")
    parser.add_argument("--agent", choices=["claude", "hermes", "antigravity"], default="antigravity", help="Agent type reporting metrics.")
    parser.add_argument("--conv-id", default=None, help="Conversation ID for transcript token lookup.")
    args, unknown = parser.parse_known_args()

    content = ""
    # Non-blocking read from stdin if available
    if not sys.stdin.isatty():
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            content = sys.stdin.read().strip()
    
    if not content and unknown:
        content = " ".join(unknown).strip()

    conv_id = args.conv_id or os.environ.get("CONVERSATION_ID") or os.environ.get("ANTIGRAVITY_CONVERSATION_ID")

    # 1. Thread Tokens
    try:
        from agent_tokens import get_tokens
        token_count, source = get_tokens(args.agent, conv_id=conv_id)
        token_metric = f"- Total Tokens: {token_count} (source: {source})"
    except Exception:
        token_metric = "- Total Tokens: 0 (source: error)"

    # 2. Perplexity Quota
    pplx_metric = ""
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q.get("status") == "OK":
            pplx_metric = f"\n- Perplexity Quota: {q.get('remaining_pro')} Pro remaining, {q.get('remaining_research')} Research remaining"
    except Exception:
        pass

    metrics = f"\n\n**Thread Metrics:**\n{token_metric}{pplx_metric}"

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
