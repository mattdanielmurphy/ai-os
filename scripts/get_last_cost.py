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
        return None, None, False
    
    try:
        token_data = json.loads(TOKEN_PATH.read_text())
    except Exception:
        return None, None, False

    token_info = token_data.get("token", {})
    refresh_token_val = token_info.get("refresh_token")
    access_token = token_info.get("access_token")
    expiry_str = token_info.get("expiry")

    if not refresh_token_val:
        return None, None, False

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
        return None, None, False

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
    
    quota_5h = None
    quota_week = None
    is_real = False
    try:
        with urllib.request.urlopen(req) as res:
            resp = json.loads(res.read().decode())
            buckets = resp.get("buckets", [])
            for bucket in buckets:
                model_id = bucket.get("modelId")
                fraction = bucket.get("remainingFraction", 1.0)
                if model_id == "gemini-2.5-pro":
                    quota_5h = fraction
                    is_real = True
                elif model_id == "gemini-2.5-flash":
                    quota_week = fraction
                    is_real = True
    except Exception:
        pass

    return quota_5h, quota_week, is_real

def get_local_quotas():
    try:
        db = telemetry_db.load_db()
        turns = db.get("agy_turns", [])
    except Exception:
        turns = []
    
    now = time.time()
    five_hours_ago = now - 5 * 3600
    one_week_ago = now - 7 * 24 * 3600
    
    turns_5h = [t for t in turns if t >= five_hours_ago]
    turns_week = [t for t in turns if t >= one_week_ago]
    
    quota_5h_rem = max(0, LIMIT_5H - len(turns_5h))
    quota_week_rem = max(0, LIMIT_WEEK - len(turns_week))
    
    quota_5h_pct = (quota_5h_rem / LIMIT_5H)
    quota_week_pct = (quota_week_rem / LIMIT_WEEK)
    
    return quota_5h_pct, quota_week_pct

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
        quota_5h, quota_week, is_real = get_antigravity_quota()
        
        if not is_real or quota_5h is None or quota_week is None:
            quota_5h_pct_val, quota_week_pct_val = get_local_quotas()
            quota_5h_pct = int(quota_5h_pct_val * 100)
            quota_week_pct = int(quota_week_pct_val * 100)
            real_tag_5h = ""
            real_tag_week = ""
        else:
            quota_5h_pct = int(quota_5h * 100)
            quota_week_pct = int(quota_week * 100)
            real_tag_5h = " (Real)"
            real_tag_week = " (Real)"
        
        print("[AGY TELEMETRY]")
        print(f"Delegated Sub-Model Cost (Turn): ${cost_turn:.4f}")
        print(f"Delegated Sub-Model Cost (Total): ${cost_total:.4f}")
        print(f"AGY Quota Remaining (5hr): {quota_5h_pct}%{real_tag_5h}")
        print(f"AGY Quota Remaining (Weekly): {quota_week_pct}%{real_tag_week}***")
    else:
        cost_turn, cost_total = get_stats()
        print(f"[TELEMETRY] Sub-Model Cost This Turn: ${cost_turn:.4f} | Total Delegated Cost: ${cost_total:.4f}")

if __name__ == "__main__":
    main()
