---
title: "Fixing Variable Initialization Logic"
date: "2026-08-14"
conversation_id: "7796cf9c-dc5b-49e4-af5f-118e79bbc6ac"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Fix /Users/matt/projects/ai-os/scripts/postflight.py in `main()`:

Ensure all variables (`token_display`, `cache_display`, `breakeven_str`, `indicator`, `brief_str`, `pplx_quota_str`) have safe default values before the try blocks:

```python

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
            pplx_quota_str = f"{q.get('remaining_pro')} Pro, {q.get('remaining_research')} 🔬, {q.get('remaining_uploads')} 📤"
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

    try:
        from link_formatter import enrich_file_links
        metrics = enrich_file_links(metrics)
        if content:
            content = enrich_file_links(content)
    except Exception:
        pass

    if content:
        final_output = content + metrics
    else:
        final_output = metrics
```

Ensure the syntax is valid.

</span>



<span title="Responded at 1:02am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The `/Users/matt/projects/ai-os/scripts/postflight.py` script has been updated. The variables `token_display`, `cache_display`, `breakeven_str`, `indicator`, `brief_str`, and `pplx_quota_str` are now safely initialized with default values before any logic that might raise exceptions. The metrics table is now constructed dynamically, ensuring `Perplexity Quota` is only added if data is successfully retrieved.

</span>



</span>

</span>