---
title: "Update Perplexity Quota Tracking"
date: "2026-08-14"
conversation_id: "5b5c13f4-c812-4f58-b20d-db88d9b2c28e"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/projects/ai-os/scripts/pplx_quota.py, /Users/matt/projects/ai-os/scripts/postflight.py, and /Users/matt/projects/ai-os/scripts/preflight.py:

1. /Users/matt/projects/ai-os/scripts/pplx_quota.py:
In `get_pplx_quota()`:
Along with querying `https://www.perplexity.ai/rest/rate-limit/all`, also query `https://www.perplexity.ai/rest/user/settings` (using the same cookie header and User-Agent) to extract `upload_limit` (defaulting to '?' or 0 if missing).
In status_data, return:
```python

status_data = {
    "status": "OK",
    "remaining_pro": remaining_pro,
    "remaining_research": remaining_research,
    "remaining_labs": remaining_labs,
    "remaining_uploads": upload_limit
}
```

2. /Users/matt/projects/ai-os/scripts/postflight.py:
In the horizontal table:
If `remaining_uploads` is present, format Perplexity Quota as:
`f"{q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research, {q.get('remaining_uploads')} Uploads"`
Ensure the table is rendered horizontally:
```markdown

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| {token_display} ({source}) | {econ['cache_display']} | {token_display} / Breakeven {format_tokens(econ['n_breakeven'])} (Status: {rotation_str}) | {pplx_quota_str} |
```

3. /Users/matt/projects/ai-os/scripts/preflight.py:
In `step_pplx_quota()`:
Include uploads:
`return f"Perplexity Quota: OK ({q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research, {q.get('remaining_uploads')} Uploads)"`

Make sure everything runs quickly and cleanly.

</span>



<span title="Responded at 12:54am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The updates to the specified scripts are complete:
- [`pplx_quota.py`](file:///Users/matt/projects/ai-os/scripts/pplx_quota.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/pplx_quota.py): Now queries `https://www.perplexity.ai/rest/user/settings` to retrieve `upload_limit` (defaulting to '?' if unavailable) and includes it in the returned dictionary and stdout.
- [`postflight.py`](file:///Users/matt/projects/ai-os/scripts/postflight.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/postflight.py): Updated to display Perplexity quota including Uploads in the horizontal table.
- [`preflight.py`](file:///Users/matt/projects/ai-os/scripts/preflight.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py): Updated to include Uploads in the Perplexity Quota check summary.

</span>



</span>

</span>