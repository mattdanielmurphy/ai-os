#!/usr/bin/env python3
"""
Antigravity IDE Live Telemetry Daemon
Monitors language server daemon logs (~/.gemini/antigravity-ide/daemon/ls_*.log)
and updates ~/.hermes/antigravity_tokens.json in real time.
"""

import os
import re
import sys
import time
import json
import signal
from pathlib import Path

DAEMON_LOG_DIR = Path.home() / ".gemini" / "antigravity-ide" / "daemon"
STATE_DIR = Path.home() / ".hermes"
STATE_FILE = STATE_DIR / "antigravity_tokens.json"

# Regex patterns for telemetry extraction
RE_INPUT_TOKENS = re.compile(r'"(?:prompt_tokens|plan_tokens)"\s*:\s*(\d+)')
RE_OUTPUT_TOKENS = re.compile(r'"(?:completion_tokens|candidates_tokens)"\s*:\s*(\d+)')
RE_TRIAGE_MODE = re.compile(r'\[Triage\]\s*Routing to mode:\s*([A-Za-z0-9_-]+)')

running = True

def handle_signal(signum, frame):
    global running
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def get_latest_log_file():
    """Finds the most recently modified ls_*.log file."""
    if not DAEMON_LOG_DIR.exists():
        return None
    log_files = list(DAEMON_LOG_DIR.glob("ls_*.log"))
    if not log_files:
        return None
    return max(log_files, key=lambda f: f.stat().st_mtime)

def read_current_state():
    """Reads current state from ~/.hermes/antigravity_tokens.json safely."""
    if not STATE_FILE.exists():
        now = time.time()
        return {
            "pid": os.getpid(),
            "timestamp": now,
            "workspace_id": "",
            "csrf_token": "",
            "cloud_code_endpoint": "https://daily-cloudcode-pa.googleapis.com",
            "promptTokens": 0,
            "completionTokens": 0,
            "triageMode": "Orchestrator",
            "lastPreflightStatus": "Ready",
            "lastUpdated": now
        }
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure required numeric fields exist
            if "promptTokens" not in data:
                data["promptTokens"] = 0
            if "completionTokens" not in data:
                data["completionTokens"] = 0
            if "triageMode" not in data:
                data["triageMode"] = "Orchestrator"
            return data
    except Exception:
        now = time.time()
        return {
            "pid": os.getpid(),
            "timestamp": now,
            "workspace_id": "",
            "csrf_token": "",
            "cloud_code_endpoint": "https://daily-cloudcode-pa.googleapis.com",
            "promptTokens": 0,
            "completionTokens": 0,
            "triageMode": "Orchestrator",
            "lastPreflightStatus": "Ready",
            "lastUpdated": now
        }

def atomic_save_state(state):
    """Atomically writes state to ~/.hermes/antigravity_tokens.json."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["lastUpdated"] = time.time()
    tmp_path = STATE_DIR / f"antigravity_tokens_{os.getpid()}_{int(time.time() * 1000)}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, STATE_FILE)
    except Exception as e:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass

def main():
    global running
    print(f"[Telemetry Daemon] Starting watcher on {DAEMON_LOG_DIR}...")
    
    current_log_path = None
    log_fp = None

    while running:
        latest = get_latest_log_file()
        
        # Handle log file rotation / initial open
        if latest != current_log_path:
            if log_fp:
                try:
                    log_fp.close()
                except Exception:
                    pass
                log_fp = None
            
            if latest and latest.exists():
                print(f"[Telemetry Daemon] Tracking new log file: {latest.name}")
                current_log_path = latest
                try:
                    log_fp = open(current_log_path, "r", encoding="utf-8", errors="replace")
                    # Seek to end on initial open to track only live turns
                    log_fp.seek(0, os.SEEK_END)
                except Exception as e:
                    print(f"[Telemetry Daemon] Error opening {current_log_path}: {e}")
                    log_fp = None
            else:
                current_log_path = None

        if not log_fp:
            time.sleep(1.0)
            continue

        # Non-blocking line reading
        line = log_fp.readline()
        if not line:
            # Check if file was rotated or deleted
            if not current_log_path.exists():
                try:
                    log_fp.close()
                except Exception:
                    pass
                log_fp = None
                current_log_path = None
            time.sleep(0.2)
            continue

        # Parse line for tokens and triage
        prompt_match = RE_INPUT_TOKENS.search(line)
        output_match = RE_OUTPUT_TOKENS.search(line)
        triage_match = RE_TRIAGE_MODE.search(line)

        if prompt_match or output_match or triage_match:
            state = read_current_state()
            updated = False

            if prompt_match:
                tokens = int(prompt_match.group(1))
                state["promptTokens"] = state.get("promptTokens", 0) + tokens
                updated = True
                print(f"[Telemetry] +{tokens} Prompt Tokens (Total: {state['promptTokens']})")

            if output_match:
                tokens = int(output_match.group(1))
                state["completionTokens"] = state.get("completionTokens", 0) + tokens
                updated = True
                print(f"[Telemetry] +{tokens} Completion Tokens (Total: {state['completionTokens']})")

            if triage_match:
                mode = triage_match.group(1)
                state["triageMode"] = mode
                updated = True
                print(f"[Telemetry] Triage mode: {mode}")

            if updated:
                atomic_save_state(state)

    if log_fp:
        try:
            log_fp.close()
        except Exception:
            pass
    print("[Telemetry Daemon] Shutdown cleanly.")

if __name__ == "__main__":
    main()
