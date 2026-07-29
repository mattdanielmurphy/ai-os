#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

DAILY_LIMIT_PER_ACCT = 100

def get_keys():
    keys = []
    
    # Key 1
    k1 = os.environ.get("JULES_API_KEY")
    if not k1:
        f1 = os.path.expanduser("~/.jules/api_key")
        if os.path.exists(f1):
            with open(f1) as f:
                k1 = f.read().strip()
    if k1:
        keys.append(("Account 1 (iammattmurphy)", k1))

    # Key 2
    k2 = os.environ.get("JULES_API_KEY_ALT")
    if not k2:
        f2 = os.path.expanduser("~/.jules/api_key_alt")
        if os.path.exists(f2):
            with open(f2) as f:
                k2 = f.read().strip()
    if k2:
        keys.append(("Account 2 (darryl.l.murphy)", k2))

    return keys

def query_account_quota(name, api_key):
    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sessions = data.get("sessions", [])
            active_count = len(sessions)
            remaining = max(0, DAILY_LIMIT_PER_ACCT - active_count)
            return {"name": name, "status": "OK", "active": active_count, "remaining": remaining, "limit": DAILY_LIMIT_PER_ACCT}
    except Exception as e:
        return {"name": name, "status": "ERROR", "message": str(e), "active": 0, "remaining": 0, "limit": DAILY_LIMIT_PER_ACCT}

def get_jules_status():
    keys = get_keys()
    if not keys:
        return {"status": "UNCONFIGURED", "message": "No JULES_API_KEY or JULES_API_KEY_ALT found"}

    results = []
    total_remaining = 0
    total_limit = 0
    
    for name, key in keys:
        res = query_account_quota(name, key)
        results.append(res)
        if res["status"] == "OK":
            total_remaining += res["remaining"]
            total_limit += res["limit"]

    return {
        "status": "OK" if any(r["status"] == "OK" for r in results) else "ERROR",
        "total_remaining": total_remaining,
        "total_limit": total_limit,
        "accounts": results
    }

if __name__ == "__main__":
    status = get_jules_status()
    if status["status"] == "OK":
        acct_summary = ", ".join([f"{a['name']}: {a['remaining']}/{a['limit']}" for a in status["accounts"] if a["status"] == "OK"])
        print(f"Jules Quota: OK - {status['total_remaining']}/{status['total_limit']} total sessions remaining ({acct_summary})")
    else:
        print(f"Jules Quota: {status['status']} - {status.get('message', '')}")
