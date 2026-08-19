---
title: "Update Token Formatting Script"
date: "2026-08-14"
conversation_id: "d1db506f-e3f3-4bf3-9104-6defadeeca49"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `/Users/matt/projects/ai-os/scripts/postflight.py` to format token counts cleanly and concisely (e.g. `54k` instead of `54,332`, `547k` instead of `547381`):

Add a `format_tokens` helper and use it in `postflight.py`:
```python

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
```

And update the token metric line:
```python

        token_display = format_tokens(token_count)
        token_metric = f"- Total Tokens: {token_display} (source: {source})"
```

Please update the file now.

</span>



<span title="Responded at 12:37am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates have been successfully applied to `/Users/matt/projects/ai-os/scripts/postflight.py`.
*   Added the `format_tokens` helper function after the imports.
*   Updated the token metric generation line (now line 49) to use `format_tokens`.

</span>



</span>

</span>