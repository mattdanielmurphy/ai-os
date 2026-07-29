#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

DAILY_LIMIT = 100

def get_jules_status():
    key_file = os.path.expanduser("~/.jules/api_key")
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key and os.path.exists(key_file):
        with open(key_file) as f:
            api_key = f.read().strip()
    
    if not api_key:
        return {"status": "UNCONFIGURED", "message": "No JULES_API_KEY found"}

    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sessions = data.get("sessions", [])
            count = len(sessions)
            remaining = max(0, DAILY_LIMIT - count)
            return {
                "status": "OK",
                "active_today": count,
                "remaining_estimated": remaining,
                "daily_limit": DAILY_LIMIT
            }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    status = get_jules_status()
    if status["status"] == "OK":
        print(f"Jules Quota: OK - {status['remaining_estimated']}/{status['daily_limit']} sessions remaining today ({status['active_today']} active)")
    else:
        print(f"Jules Quota: {status['status']} - {status.get('message', '')}")
