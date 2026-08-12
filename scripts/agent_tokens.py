#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path

def get_tokens(agent=None):
    if agent == "claude":
        return 0, "reported"
    elif agent == "hermes":
        try:
            import telemetry_db
            db = telemetry_db.load_db()
            return 0, "reported"
        except Exception:
            return 0, "reported"
    else:
        try:
            import check_thread_bloat
            project_root = Path(os.getcwd())
            t_sys, _ = check_thread_bloat.get_sys_prompt_tokens(project_root)
            transcript_path = check_thread_bloat.find_transcript_file()
            t_hist = check_thread_bloat.get_transcript_tokens(transcript_path)
            return t_sys + t_hist, "estimated"
        except ImportError:
            return 0, "estimated"
