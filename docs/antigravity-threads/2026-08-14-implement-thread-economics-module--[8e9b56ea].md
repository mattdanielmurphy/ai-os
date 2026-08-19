---
title: "Implement Thread Economics Module"
date: "2026-08-14"
conversation_id: "8e9b56ea-48c9-4d9e-b1df-127a11c6cf28"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Create the new module /Users/matt/projects/ai-os/scripts/thread_economics.py and update /Users/matt/projects/ai-os/scripts/postflight.py and /Users/matt/projects/ai-os/scripts/check_thread_bloat.py.

1. /Users/matt/projects/ai-os/scripts/thread_economics.py:
Implement:
```python

#!/usr/bin/env python3
import os
import time
import json
from datetime import datetime
from pathlib import Path

def get_last_activity_time(transcript_path: str = None) -> float:
    if transcript_path and os.path.exists(transcript_path):
        try:
            # Check last few lines of transcript for created_at
            with open(transcript_path, "rb") as f:
                f.seek(max(0, os.path.getsize(transcript_path) - 4096))
                lines = f.read().decode("utf-8", errors="ignore").strip().splitlines()
                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        step = json.loads(line)
                        ca = step.get("created_at")
                        if ca:
                            # Parse ISO string (e.g. 2026-08-14T00:40:38Z or with offset)
                            ca_clean = ca.replace("Z", "+00:00")
                            dt = datetime.fromisoformat(ca_clean)
                            return dt.timestamp()
                    except Exception:
                        pass
            return os.path.getmtime(transcript_path)
        except Exception:
            pass
    return time.time()

def calculate_thread_economics(t_current: int, t_sys: int, last_write_ts: float = None, model_name: str = None) -> dict:
    write_multiplier = 1.25
    read_multiplier = 0.10
    H = 1500  # handoff overhead tokens
    N0 = t_sys + H
    
    # Financial breakeven calculation
    n_breakeven = int((H + N0 * write_multiplier) / read_multiplier)
    
    # Context window & hard cap calculation
    model_str = (model_name or "").lower()
    if "gemini" in mode
<truncated 1671 bytes>
rting a new thread."
    elif is_cache_expired:
        recommendation_status = "CACHE_EXPIRED"
        rotation_recommendation = f"⚠️ Token cache expired at {expiry_str}. Continuing will incur full cache-write charges. Consider starting a new thread."
    else:
        recommendation_status = "OK"
        rotation_recommendation = "OK"
        
    return {
        "t_current": t_current,
        "t_sys": t_sys,
        "n_breakeven": n_breakeven,
        "n_hard_cap": n_hard_cap,
        "is_past_breakeven": is_past_breakeven,
        "is_hard_cap_breached": is_hard_cap_breached,
        "last_activity_ts": last_ts,
        "cache_expires_at": cache_expires_at,
        "cache_status": cache_status,
        "cache_display": cache_display,
        "is_cache_expired": is_cache_expired,
        "recommendation_status": recommendation_status,
        "rotation_recommendation": rotation_recommendation,
    }
```

2. /Users/matt/projects/ai-os/scripts/check_thread_bloat.py:
Import `thread_economics` and include economics and cache fields in `result` dict in `main()`:
```python

    try:
        import thread_economics
        last_ts = thread_economics.get_last_activity_time(transcript_path)
        econ = thread_economics.calculate_thread_economics(t_sys + t_hist, t_sys, last_write_ts=last_ts)
        result["economics"] = econ
    except Exception:
        pass
```

3. /Users/matt/projects/ai-os/scripts/postflight.py:
Import `thread_economics` and `check_thread_bloat`.
Calculate `econ = thread_economics.calculate_thread_economics(token_count, t_sys, last_write_ts=last_ts)`.
Display:
- Total Tokens: {token_display} (source: {source})
- Cache Expiry: {econ['cache_display']}
- Financial Rotation: {format_tokens(token_count)} / Breakeven {format_tokens(econ['n_breakeven'])} (Status: {econ['recommendation_status']})
- Perplexity Quota: ...

Make sure all imports and executions run fast and without errors.

</span>



<span title="Responded at 12:50am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The thread economics modules and updates have been implemented as requested.

### Summary of Changes
1.  **Created New Module**: [`/Users/matt/projects/ai-os/scripts/thread_economics.py`](file:///Users/matt/projects/ai-os/scripts/thread_economics.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/thread_economics.py)
    *   Provides `get_last_activity_time` for tracking thread activity from transcripts.
    *   Provides `calculate_thread_economics` for calculating financial breakeven points, context caps, and cache status.
2.  **Updated [`check_thread_bloat.py`](file:///Users/matt/projects/ai-os/scripts/check_thread_bloat.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/check_thread_bloat.py)**
    *   Integrated `thread_economics` to inject an `economics` dictionary into the bloat check results, including cache status and breakeven data.
3.  **Updated [`postflight.py`](file:///Users/matt/projects/ai-os/scripts/postflight.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/postflight.py)**
    *   Integrated `thread_economics` to display thread metrics in the postflight output, specifically:
        *   Token count/

</span>



</span>

</span>