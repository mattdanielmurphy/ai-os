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
    if not conv_id:
        try:
            from check_thread_bloat import find_transcript_file
            from pathlib import Path
            t_path = find_transcript_file()
            if t_path:
                conv_id = Path(t_path).parent.parent.parent.name
        except Exception:
            pass

    # 1. Thread Tokens & Economics
    token_display = "0"
    source = "error"
    cache_display = "1h"
    breakeven_str = "0"
    indicator = "🟢"
    brief_str = ""

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

        cache_display = econ.get('cache_display', '1h')
        indicator = econ.get('indicator', '🟢')
        brief_str = f" ({econ['brief']})" if econ.get('brief') else ""
        breakeven_str = format_tokens(econ.get('n_breakeven', 0))
    except Exception:
        pass

    # 2. Perplexity Quota
    pplx_quota_str = ""
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q and q.get("status") == "OK":
            pplx_quota_str = f"{q.get('remaining_pro')}, {q.get('remaining_research')} 🔬, {q.get('remaining_uploads')} 📤"
    except Exception:
        pass

    headers = ["Total Tokens", "Cache Expiry", "Financial Rotation"]
    values = [f"~{token_display}", cache_display, f"~{token_display} / ~{breakeven_str} {indicator}{brief_str}"]

    if pplx_quota_str:
        headers.append("Perplexity Quota")
        values.append(pplx_quota_str)

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join([":---"] * len(headers)) + " |"
    value_row = "| " + " | ".join(values) + " |"

    metrics = f"\n\n**Thread Metrics:**\n\n{header_row}\n{separator_row}\n{value_row}"

    if content:
        from link_formatter import enrich_file_links
        final_output = enrich_file_links(content + metrics)
    else:
        from link_formatter import enrich_file_links
        final_output = enrich_file_links(metrics)

    print(final_output)

    if conv_id:
        try:
            from pathlib import Path
            app_data_dir = Path.home() / ".gemini/antigravity"
            from gen_conversation_md import generate
            import io
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                generate(conv_id, "Conversation", app_data_dir=app_data_dir)
        except Exception:
            pass

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
