import sys
import os
from pathlib import Path

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
        return f"{val:.1f}M".replace(".0M", "M") if (val % 1 >= 0.05 and val % 1 <= 0.95) else f"{round(val)}M"
    if tokens >= 100_000:
        k_val = round(tokens / 10_000) * 10
        return f"{k_val}k"
    if tokens >= 20_000:
        k_val = round(tokens / 5_000) * 5
        return f"{k_val}k"
    if tokens >= 1_000:
        return f"{round(tokens / 1_000)}k"
    return str(tokens)

def compute_thread_metrics(conv_id: str = None, agent: str = "antigravity") -> dict:
    from agent_tokens import get_tokens
    import thread_economics
    from check_thread_bloat import find_transcript_file, get_sys_prompt_tokens
    from pplx_quota import get_pplx_quota

    token_count, source = get_tokens(agent, conv_id=conv_id)
    token_display = format_tokens(token_count)
    
    cache_display = "1h"
    breakeven_str = "0"
    indicator = "🟢"
    brief_str = ""
    pplx_quota_str = ""

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

    try:
        q = get_pplx_quota()
        if q and q.get("status") == "OK":
            remaining_pro = q.get('remaining_pro')
            remaining_uploads = q.get('remaining_uploads')
            if remaining_uploads:
                pplx_quota_str = f"{remaining_pro} ❓, {remaining_uploads} 📤"
            else:
                pplx_quota_str = f"{remaining_pro} ❓"
    except Exception:
        pass

    return {
        "token_display": token_display,
        "cache_display": cache_display,
        "indicator": indicator,
        "brief_str": brief_str,
        "breakeven_str": breakeven_str,
        "pplx_quota_str": pplx_quota_str
    }

def format_metrics_table(metrics: dict, conv_id: str = None) -> str:
    headers = ["Tokens", "Expiry"]
    values = [
        f"~{metrics['token_display']} / ~{metrics['breakeven_str']} {metrics['indicator']}{metrics['brief_str']}",
        metrics['cache_display']
    ]

    if metrics.get('pplx_quota_str'):
        headers.append("PPLX Quota")
        values.append(metrics['pplx_quota_str'])

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join([":---"] * len(headers)) + " |"
    value_row = "| " + " | ".join(values) + " |"
    return f"\n\n{header_row}\n{separator_row}\n{value_row}\n\n"

def has_uncommitted_changes(repo_root: str) -> bool:
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False
