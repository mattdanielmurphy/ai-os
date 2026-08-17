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

def get_git_commit_status(repo_root: str = "/Users/matt/projects/ai-os") -> dict:
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--ignore-submodules=dirty"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return {"state": "error", "badge": "🔴 Error", "count": 0}
        
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return {"state": "clean", "badge": "🟢 Clean", "count": 0}
        
        for l in lines:
            if l.startswith("UU") or l.startswith("AA") or l.startswith("UD") or l.startswith("DU"):
                return {"state": "error", "badge": "🔴 Conflict", "count": len(lines)}
        
        return {"state": "uncommitted", "badge": f"🟡 Uncommitted ({len(lines)})", "count": len(lines)}
    except Exception:
        return {"state": "error", "badge": "🔴 Error", "count": 0}

def extract_workspace_root(conv_id: str = None, transcript_path = None) -> Path:
    """Extract project repository root from transcript tool calls or default to ai-os."""
    import re
    if transcript_path is None and conv_id:
        from check_thread_bloat import find_transcript_file
        transcript_path = find_transcript_file(conv_id=conv_id)
        
    try:
        if transcript_path and Path(transcript_path).exists():
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    matches = re.findall(r'/Users/matt/projects/([^/"\'\s\\]+)', line)
                    for proj in matches:
                        if proj and proj not in ('.git', 'tmp', 'node_modules', 'dist'):
                            proj_path = Path(f"/Users/matt/projects/{proj}")
                            if proj_path.is_dir() and (proj_path / ".git").exists():
                                return proj_path
    except Exception:
        pass
    return Path("/Users/matt/projects/ai-os")

def compute_thread_metrics(conv_id: str = None, agent: str = "antigravity", workspace_root: str = None) -> dict:
    from agent_tokens import get_tokens
    import thread_economics
    from check_thread_bloat import find_transcript_file, get_sys_prompt_tokens
    from pplx_quota import get_pplx_quota

    transcript_path = find_transcript_file(conv_id=conv_id)
    if workspace_root is None:
        workspace_root = str(extract_workspace_root(conv_id=conv_id, transcript_path=transcript_path))

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

    commit_status = get_git_commit_status(workspace_root)

    raw_history_tokens = max(0, token_count - t_sys)
    compact_history_tokens = int(raw_history_tokens * 0.18) if raw_history_tokens > 0 else 0
    compact_total = t_sys + compact_history_tokens
    savings_pct = int(((token_count - compact_total) / max(1, token_count)) * 100) if token_count > compact_total else 0

    cost_comp = thread_economics.calculate_turn_cost_comparison(token_count, t_sys, compact_total)

    return {
        "token_display": token_display,
        "cache_display": cache_display,
        "indicator": indicator,
        "brief_str": brief_str,
        "breakeven_str": breakeven_str,
        "pplx_quota_str": pplx_quota_str,
        "commit_status": commit_status,
        "compact_display": format_tokens(compact_total),
        "savings_pct": savings_pct,
        "cost_comp": cost_comp,
        "handoff_ready": token_count > 35000
    }

def format_metrics_table(metrics: dict, conv_id: str = None) -> str:
    """Returns raw markdown table string. Must be surrounded by blank lines to render."""
    headers = ["Tokens", "Expiry", "Committed"]
    commit_badge = metrics.get('commit_status', {}).get('badge', '\U0001f7e2 Clean') if isinstance(metrics.get('commit_status'), dict) else '\U0001f7e2 Clean'

    values = [
        f"~{metrics['token_display']} / ~{metrics['breakeven_str']} {metrics['indicator']}{metrics['brief_str']}",
        metrics['cache_display'],
        commit_badge
    ]

    if metrics.get('pplx_quota_str'):
        headers.append("PPLX Quota")
        values.append(metrics['pplx_quota_str'])

    if conv_id and metrics.get('savings_pct', 0) > 25:
        headers.append("Handoff")
        handoff_url = f"http://127.0.0.1:3031/handoff?session={conv_id}"
        cost = metrics.get('cost_comp', {})
        c_cost = cost.get('continuing', 0)
        h_cost = cost.get('handoff', 0)
        
        c_tok = cost.get('continuing', 0)
        h_tok = cost.get('handoff', 0)
        
        if c_tok >= h_tok:
            cost_badge = f"-{int(((c_tok - h_tok)/max(1, c_tok))*100)}% cost T1"
        else:
            cost_badge = f"+{int(((h_tok - c_tok)/max(1, c_tok))*100)}% cost T1"
            
        values.append(f"[\u26a1 -{metrics['savings_pct']}% context \u00b7 {cost_badge}]({handoff_url})")

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join([":---"] * len(headers)) + " |"
    value_row = "| " + " | ".join(values) + " |"
    return f"\n\n{header_row}\n{separator_row}\n{value_row}\n\n"


def format_nav_toggle(kanban_path: str = None, thread_path: str = None) -> str:
    """Returns a position:absolute pill HTML element for the footer nav toggle.
    Designed to overlay inside the already-positioned pinned footer span
    without wrapping the markdown table (which would break rendering)."""
    if kanban_path:
        return (
            f'<span style="position: absolute; right: 2rem; bottom: 0.5rem; '
            f'display: inline-block; font-size: 11px; font-weight: 600; '
            f'opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); '
            f'border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;">'
            f'<a href="file://{kanban_path}" style="text-decoration:none;">\U0001f4cb Kanban</a>'
            f'</span>'
        )
    if thread_path:
        return (
            f'<span style="position: absolute; right: 2rem; bottom: 0.5rem; '
            f'display: inline-block; font-size: 11px; font-weight: 600; '
            f'opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); '
            f'border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;">'
            f'<a href="file://{thread_path}" style="text-decoration:none;">\U0001f4ac Thread</a>'
            f'</span>'
        )
    return ""

def has_uncommitted_changes(repo_root: str) -> bool:
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--ignore-submodules=dirty"],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False
