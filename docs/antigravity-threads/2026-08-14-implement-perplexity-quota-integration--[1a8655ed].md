---
title: "Implement Perplexity Quota Integration"
date: "2026-08-14"
conversation_id: "1a8655ed-25a6-431a-8815-d3653ba231b8"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please create/modify the following files to implement the thread size and Perplexity quota injection:

1. Create `/Users/matt/projects/ai-os/scripts/pplx_quota.py`:
```python

#!/usr/bin/env python3
import os
import json
import time
import shutil
import sqlite3
import urllib.request

CACHE_FILE = "/tmp/pplx_quota_cache.json"
CACHE_EXPIRY = 30  # seconds

def get_pplx_cookies():
    cookie_candidates = [
        os.path.expanduser("~/Library/Application Support/proxima/Partitions/perplexity/Cookies"),
        os.path.expanduser("~/Library/Application Support/proxima/Cookies"),
    ]
    for src in cookie_candidates:
        if os.path.exists(src):
            tmp = f"/tmp/pplx_cookies_{os.getpid()}.db"
            try:
                shutil.copy2(src, tmp)
                conn = sqlite3.connect(tmp)
                c = conn.cursor()
                c.execute('SELECT name, value FROM cookies WHERE host_key LIKE "%perplexity%"')
                cookie_dict = {name: val for name, val in c.fetchall() if val}
                conn.close()
                if os.path.exists(tmp):
                    os.remove(tmp)
                if cookie_dict:
                    return '; '.join([f"{k}={v}" for k, v in cookie_dict.items()])
            except Exception:
                if os.path.exists(tmp):
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
    return None

def get_pplx_quota(force=False):
    if not force and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
                if time.time() - cache.get("timestamp", 0) < CACHE_EXPIRY:
                    return cache.get("data", {})
        except Exception:
            pass

    cookie_header = get_pplx_cookies()
    if not cookie_header:
        return {"status": "UNCONFIGURED", "message": "No Perplexity session cookies found in Proxima profile"}

    req = urllib.request.Request(
   
<truncated 4738 bytes>
stflight_async.py")
    if os.path.exists(async_script):
        subprocess.Popen(
            [sys.executable, async_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

if __name__ == "__main__":
    main()
```

4. Update `/Users/matt/projects/ai-os/scripts/preflight.py` to add `step_pplx_quota`:
Include `step_pplx_quota()`:
```python

def step_pplx_quota():
    try:
        from pplx_quota import get_pplx_quota
        q = get_pplx_quota()
        if q.get("status") == "OK":
            return f"Perplexity Quota: OK ({q.get('remaining_pro')} Pro, {q.get('remaining_research')} Research)"
        return f"Perplexity Quota: {q.get('status')}"
    except Exception as e:
        return f"Perplexity Quota: ERROR ({e})"
```

Add `("Perplexity", step_pplx_quota)` to the concurrent step runner in `preflight.py`.

5. Update `AG_CONTEXT.md` to add durable knowledge about userscript locations and Perplexity quota:
Add a bullet under `Key Architecture & Domain Rules`:
`- **Userscripts Directory & Bundler (`~/projects/userscript-bundler/userscripts/`)**: All browser and webview userscripts (Gemini, Perplexity, YouTube, Control Center, etc.) live in `~/projects/userscript-bundler/userscripts/`. The auto-bundler (`watch-and-bundle.js` / `bundler.cjs`) builds them into `~/projects/userscript-bundler/compiled/`. Perplexity rate-limit and quota checks query `https://www.perplexity.ai/rest/rate-limit/all` using local browser session cookies via `scripts/pplx_quota.py`.`

6. Update `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Mac/macOS Environment.md`:
Under `## Active Custom Launch Agents`, note `com.matt.agent.userscript-bundler` watches `~/projects/userscript-bundler/userscripts/`, and document the userscript source directory and Perplexity API rate-limit integration.

Please make all of these edits cleanly.

</span>



<span title="Responded at 12:35am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The Perplexity quota and thread size injection modifications have been completed.

### Summary of Changes:
* **Perplexity Quota Logic**:
    * Created [`pplx_quota.py`](file:///Users/matt/projects/ai-os/scripts/pplx_quota.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/pplx_quota.py) to manage quota polling via local Proxima session cookies.
    * Added `step_pplx_quota` to [`preflight.py`](file:///Users/matt/projects/ai-os/scripts/preflight.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/preflight.py) and registered it in the concurrent preflight runner.
    * Integrated quota reporting into [`postflight.py`](file:///Users/matt/projects/ai-os/scripts/postflight.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/postflight.py) to provide immediate feedback after tasks.
* **Thread Size Enhancements**:
    * Updated [`agent_tokens.py`](file:///Users/matt/projects/ai-os/scripts/agent_tokens.py) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/agent_tokens.py) to accept `conv_id`, allowing accurate token count estimation for specific transcripts.
    * Updated [`postflight.py`](file:///Users/matt/projects/ai-

</span>



</span>

</span>