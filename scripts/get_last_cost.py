#!/usr/bin/env python3
import json
import os
import sys
import time
import datetime
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Add parent directory to sys.path to import telemetry_db
sys.path.append(str(Path(__file__).parent))
try:
    import telemetry_db
except ImportError:
    pass

LIMIT_5H = 50
LIMIT_WEEK = 200
TOKEN_PATH = Path.home() / ".gemini" / "antigravity-cli" / "antigravity-oauth-token"
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
CLIENT_SECRET = "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"

def get_antigravity_quota():
    if not TOKEN_PATH.exists():
        return 1.0, 1.0
    
    try:
        token_data = json.loads(TOKEN_PATH.read_text())
    except Exception:
        return 1.0, 1.0

    token_info = token_data.get("token", {})
    refresh_token_val = token_info.get("refresh_token")
    access_token = token_info.get("access_token")
    expiry_str = token_info.get("expiry")

    if not refresh_token_val:
        return 1.0, 1.0

    is_expired = True
    if expiry_str:
        try:
            expiry = datetime.datetime.fromisoformat(expiry_str)
            now = datetime.datetime.now(datetime.timezone.utc) if expiry.tzinfo else datetime.datetime.now()
            if expiry > now + datetime.timedelta(seconds=60):
                is_expired = False
        except Exception:
            pass

    if is_expired or not access_token:
        url = "https://oauth2.googleapis.com/token"
        req_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token_val,
            "grant_type": "refresh_token"
        }
        encoded_data = urllib.parse.urlencode(req_data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, method="POST")
        try:
            with urllib.request.urlopen(req) as res:
                resp_data = json.loads(res.read().decode())
                access_token = resp_data.get("access_token")
                expires_in = resp_data.get("expires_in", 3600)
                if access_token:
                    token_info["access_token"] = access_token
                    new_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
                    token_info["expiry"] = new_expiry.isoformat()
                    token_data["token"] = token_info
                    TOKEN_PATH.write_text(json.dumps(token_data, indent=2))
        except Exception:
            pass

    if not access_token:
        return 1.0, 1.0

    quota_url = "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota"
    req = urllib.request.Request(
        quota_url,
        data=b"{}",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    quota_5h = 1.0
    quota_week = 1.0
    try:
        with urllib.request.urlopen(req) as res:
            resp = json.loads(res.read().decode())
            buckets = resp.get("buckets", [])
            for bucket in buckets:
                model_id = bucket.get("modelId")
                fraction = bucket.get("remainingFraction", 1.0)
                if model_id == "gemini-2.5-pro":
                    quota_5h = fraction
                elif model_id == "gemini-2.5-flash":
                    quota_week = fraction
    except Exception:
        pass

    return quota_5h, quota_week

def get_stats():
    db = telemetry_db.load_db()
    sub_model_costs = db.get("sub_model_costs", [])
    
    now = time.time()
    ten_minutes_ago = now - 600
    
    local_midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    
    cost_turn = 0.0
    cost_total = 0.0
    
    for item in sub_model_costs:
        ts = item.get("timestamp", 0)
        cost = item.get("calculated_cost", 0.0)
        if ts >= ten_minutes_ago:
            cost_turn += cost
        if ts >= local_midnight:
            cost_total += cost
            
    return cost_turn, cost_total

def main():
    parser = argparse.ArgumentParser(description="AI-OS Smart Cost Reporter")
    parser.add_argument("--agent", choices=["agy", "claude"], default="claude", help="Agent type to report for")
    args = parser.parse_args()
    
    if args.agent == "agy":
        cost_turn, cost_total = get_stats()
        quota_5h, quota_week = get_antigravity_quota()
        
        quota_5h_pct = int(quota_5h * 100)
        quota_week_pct = int(quota_week * 100)
        
        print("[AGY TELEMETRY]")
        print(f"Delegated Sub-Model Cost (Turn): ${cost_turn:.4f}")
        print(f"Delegated Sub-Model Cost (Total): ${cost_total:.4f}")
        print(f"AGY Quota Remaining (5hr): {quota_5h_pct}% (Real)")
        print(f"AGY Quota Remaining (Weekly): {quota_week_pct}% (Real)")
    else:
        cost_turn, cost_total = get_stats()
        print(f"[TELEMETRY] Sub-Model Cost This Turn: ${cost_turn:.4f} | Total Delegated Cost: ${cost_total:.4f}")

if __name__ == "__main__":
    main()