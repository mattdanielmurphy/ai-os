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

    if not cookie_header:
        return {"status": "UNCONFIGURED", "message": "No Perplexity session cookies found"}

    req = urllib.request.Request(
        "https://www.perplexity.ai/rest/rate-limit/all",
        headers={
            "Cookie": cookie_header,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            remaining_pro = data.get("remaining_pro", "?")
            remaining_research = data.get("remaining_research", "?")
            remaining_labs = data.get("remaining_labs", "?")
            
            # Fetch upload limit
            upload_limit = "?"
            try:
                req_settings = urllib.request.Request(
                    "https://www.perplexity.ai/rest/user/settings",
                    headers={
                        "Cookie": cookie_header,
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                )
                with urllib.request.urlopen(req_settings, timeout=5) as resp_settings:
                    settings_data = json.loads(resp_settings.read().decode("utf-8"))
                    upload_limit = settings_data.get("upload_limit", "?")
            except Exception:
                pass

            status_data = {
                "status": "OK",
                "remaining_pro": remaining_pro,
                "remaining_research": remaining_research,
                "remaining_labs": remaining_labs,
                "remaining_uploads": upload_limit
            }
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump({"timestamp": time.time(), "data": status_data}, f)
            except Exception:
                pass
            return status_data
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    q = get_pplx_quota(force=True)
    if q.get("status") == "OK":
        print(f"Perplexity Quota: OK (Pro: {q.get('remaining_pro')}, Research: {q.get('remaining_research')}, Labs: {q.get('remaining_labs')}, Uploads: {q.get('remaining_uploads')})")
    else:
        print(f"Perplexity Quota: {q.get('status')} - {q.get('message')}")
