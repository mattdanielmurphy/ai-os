#!/usr/bin/env python3
"""
services/tts-hal/speak.py
CLI & Module for HAL-9000 speech playback and lifecycle control.

Usage:
  python3 services/tts-hal/speak.py "The square root of 64 is 8."
  python3 services/tts-hal/speak.py --stop
"""

import sys
import os
import signal
import subprocess
import tempfile
from pathlib import Path

PID_FILE = Path("/tmp/hal_tts_playback.pid")
CURRENT_DIR = Path(__file__).resolve().parent

def stop_playback():
    """Stops any currently active HAL speech playback process."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        try:
            PID_FILE.unlink()
        except Exception:
            pass
    # Also kill any lingering afplay instances tagged with hal_
    subprocess.run(["pkill", "-f", "afplay /tmp/hal_"], stderr=subprocess.DEVNULL)

def speak(text: str, non_blocking: bool = True, voice_name: str = "Daniel"):
    """Synthesizes and plays speech in HAL-9000 voice."""
    stop_playback()

    venv_python = Path("/Users/matt/projects/ai-os/services/wake-hal/.venv/bin/python3")
    py_exec = str(venv_python) if venv_python.exists() else sys.executable

    # Playback script runner
    script = f"""
import sys
import os
from pathlib import Path
import subprocess

sys.path.insert(0, "{CURRENT_DIR}")
from engine import HalVoiceEngine

PID_FILE = Path("{PID_FILE}")
PID_FILE.write_text(str(os.getpid()))

try:
    engine = HalVoiceEngine(voice_name="{voice_name}")
    wav_path = engine.synthesize({repr(text)})
    proc = subprocess.run(["afplay", str(wav_path)])
    try:
        wav_path.unlink()
    except Exception:
        pass
finally:
    if PID_FILE.exists():
        try:
            PID_FILE.unlink()
        except Exception:
            pass
"""
    if non_blocking:
        subprocess.Popen(
            [py_exec, "-c", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    else:
        subprocess.run([py_exec, "-c", script])

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 speak.py <text> | --stop")
        sys.exit(0)

    if "--stop" in args:
        stop_playback()
        sys.exit(0)

    sync_mode = "--sync" in args
    filtered_args = [a for a in args if a not in ["--sync", "--stop"]]
    phrase = " ".join(filtered_args)

    speak(phrase, non_blocking=not sync_mode)

if __name__ == "__main__":
    main()
