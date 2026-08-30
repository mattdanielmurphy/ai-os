#!/usr/bin/env python3
"""
services/wake-hal/monitor.py
Real-time diagnostic monitor for the live background Hal wake-word service.

Taps directly into ~/.hermes/logs/wake-hal-err.log and ~/.hermes/logs/wake-hal.log,
streaming live background service events (microphone capture, transcription,
wake-word matches, triage dispatches, and errors).
"""

import sys
import os
import time
import subprocess
from pathlib import Path

LOG_PATH = Path.home() / ".hermes" / "logs" / "wake-hal-err.log"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.aios.wake-hal.plist"

def check_service_status():
    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    running = "com.aios.wake-hal" in res.stdout
    return running

def main():
    print("=" * 65)
    print("🎙️  HAL BACKGROUND SERVICE LIVE MONITOR")
    print("=" * 65)
    
    is_running = check_service_status()
    if is_running:
        print("🟢 Background Service Status: ACTIVE (Loaded in launchd)")
    else:
        print("🔴 Background Service Status: INACTIVE (Run 'launchctl load -w ~/Library/LaunchAgents/com.aios.wake-hal.plist')")

    print(f"📁 Streaming logs from: {LOG_PATH}")
    print("=" * 65)
    print("Speak into your mic: Say 'Hal' or 'Hal, open google'...")
    print("-----------------------------------------------------------------\n")

    if not LOG_PATH.exists():
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.touch()

    # Stream the log file live (like tail -f)
    with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
        # Move to the end of the file
        f.seek(0, os.SEEK_END)
        
        try:
            while True:
                line = f.readline()
                if line:
                    line_str = line.strip()
                    if "HEARD:" in line_str:
                        print(f"\n🎤 {line_str.split('HEARD:', 1)[1].strip()}")
                    elif "Wake word" in line_str or "WAKE" in line_str:
                        print(f"🎯 {line_str}")
                    elif "DISPATCHING" in line_str:
                        print(f"🚀 {line_str}")
                    elif "Fast-path" in line_str or "direct execution" in line_str:
                        print(f"⚡ {line_str}")
                    elif "ERROR" in line_str or "Error" in line_str or "Traceback" in line_str:
                        print(f"❌ {line_str}")
                    else:
                        print(f"   {line_str}")
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting monitor.")

if __name__ == "__main__":
    main()
