---
title: "Optimize Postflight Script Robustness"
date: "2026-08-14"
conversation_id: "ed572bfe-8720-4449-b66b-2ee4f8731219"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Fix /Users/matt/projects/ai-os/scripts/postflight.py so `main()` is fully correct and robust:

```python

    # 1. Thread Tokens & Economics
    token_display = "0"
    source = "error"
    cache_display = "1h"
    rotation_str = "OK"
    breakeven_str = "0"
    
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
        
        cache_display = econ['cache_display']
        status = econ['recommendation_status']
        rotation_str = "OK" if status == "OK" else f"⚠️ {status}"
        breakeven_str = format_tokens(econ['n_breakeven'])
    except Exception:
        pass

    # 2. Perplexity Quota
    pplx_quota_str = ""
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q.get("status") == "OK":
            pplx_quota_str = f"{q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research, {q.get('remaining_uploads')} Uploads"
    except Exception:
        pass

    headers = ["Total Tokens", "Cache Expiry", "Financial Rotation"]
    values = [f"{token_display} ({source})", cache_display, f"{token_display} / Breakeven {breakeven_str} (Status: {rotation_str})"]

    if pplx_quota_str:
        headers.append("Perplexity Quota")
        values.append(pplx_quota_str)

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join([":---"] * len(headers)) + " |"
    value_row = "| " + " | ".join(values) + " |"
    
    metrics = f"\n\n**Thread Metrics:**\n\n{header_row}\n{separator_row}\n{value_row}"
```

Make sure the file syntax is completely valid and tested.

</span>



<span title="Responded at 12:55am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested modifications to `/Users/matt/projects/ai-os/scripts/postflight.py` have been completed. The `main()` function has been updated to be more robust by:
1.  **Robust Exception Handling**: Wrapping token/economic data and Perplexity quota retrieval in `try...except` blocks to prevent script failure if external dependencies are unavailable.
2.  **Logic Fixes**: Correctly initializing local variables (`token_display`, `source`, `cache_display`, `rotation_str`, `breakeven_str`) and ensuring `pplx_quota_str` is properly populated and checked.
3.  **Table Formatting**: Dynamically assembling the Markdown table based on the availability of metrics.
All necessary imports and logic from your request have been integrated into the file.

</span>



</span>

</span>