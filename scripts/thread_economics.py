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
    if "gemini" in model_str or model_str == "" or t_sys > 20000:
        max_context = 1_000_000
    elif "claude" in model_str or "200k" in model_str:
        max_context = 200_000
    else:
        max_context = 500_000
        
    safety_factor = 0.55
    n_hard_cap = int(max_context * safety_factor)
    
    # Cache TTL (1 hour = 3600 seconds)
    now = time.time()
    last_ts = last_write_ts if last_write_ts else now
    cache_expires_at = last_ts + 3600
    is_cache_expired = now > cache_expires_at
    
    expiry_dt = datetime.fromtimestamp(cache_expires_at).astimezone()
    expiry_str = expiry_dt.strftime("%-I:%M%p").lower()

    if is_cache_expired:
        cache_display = f"{expiry_str} (⚠️ Expired)"
        cache_status = "EXPIRED"
    else:
        cache_display = f"{expiry_str}"
        cache_status = "ACTIVE"
        
    is_past_breakeven = t_current >= n_breakeven
    is_hard_cap_breached = t_current >= n_hard_cap
    
    if is_hard_cap_breached:
        recommendation_status = "DEFINITELY_NEW_THREAD"
        rotation_recommendation = f"🛑 Context cap reached ({t_current:,} >= {n_hard_cap:,}). Model reasoning degrades significantly. Definitely start a new thread!"
    elif is_past_breakeven:
        recommendation_status = "CONSIDER_NEW_THREAD"
        rotation_recommendation = f"⚠️ Past financial breakeven ({t_current:,} >= {n_breakeven:,}). Marginal cost of continuing exceeds fresh thread initialization. Consider starting a new thread."
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
