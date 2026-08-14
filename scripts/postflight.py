#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
import select

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

def format_tokens(tokens: int) -> str:
    try:
        tokens = int(tokens)
    except (ValueError, TypeError):
        return "0"
    if tokens <= 0:
        return "0"
    if tokens >= 1_000_000:
        val = tokens / 1_000_000
        return f"{val:.1f}M" if (val % 1 >= 0.05 and val % 1 <= 0.95) else f"{round(val)}M"
    if tokens >= 1_000:
        return f"{round(tokens / 1_000)}k"
    return str(tokens)

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

    # 1. Thread Tokens & Economics
    econ_metric = ""
    try:
        from agent_tokens import get_tokens
        token_count, source = get_tokens(args.agent, conv_id=conv_id)
        token_display = format_tokens(token_count)
        
        # Economics
        import thread_economics
        from check_thread_bloat import find_transcript_file, get_sys_prompt_tokens
        from pathlib import Path
        transcript_path = find_transcript_file(conv_id=conv_id)
        last_ts = thread_economics.get_last_activity_time(transcript_path)
        
        try:
            t_sys_val, _ = get_sys_prompt_tokens(Path(os.getcwd()))
            t_sys = int(t_sys_val)
        except Exception:
            t_sys = int(min(25000, token_count // 2) if token_count > 0 else 25000)
        econ = thread_economics.calculate_thread_economics(token_count, t_sys, last_write_ts=last_ts)
        
        token_metric = f"- Total Tokens: {token_display} (source: {source})"
        cache_expiry = f"- Cache Expiry: {econ['cache_display']}"
        status = econ['recommendation_status']
        if status == "OK":
            rotation_str = "OK"
        else:
            rotation_str = f"⚠️ {status}"
        econ_rotation = f"- Financial Rotation: {token_display} / Breakeven {format_tokens(econ['n_breakeven'])} (Status: {rotation_str})"
        econ_metric = f"\n{cache_expiry}\n{econ_rotation}"
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

    metrics = f"\n\n**Thread Metrics:**\n{token_metric}{econ_metric}{pplx_metric}"

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
