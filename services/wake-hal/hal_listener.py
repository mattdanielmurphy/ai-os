#!/usr/bin/env python3
"""
services/wake-hal/hal_listener.py
Unified Hal Wake Word Listener & aios Triage Dispatcher.

Features:
1. Two-stage & single-utterance voice activation:
   - "Hal, open google" -> Instantly strips "Hal" and dispatches "open google" to aios triage.
   - "Hal" -> Plays chime ("Tink"), enters ACTIVE LISTENING state with a 10-second timeout window,
     listens for your follow-up command (e.g. "open google"), and dispatches it directly.
2. Fast on-device transcription via Whisper.
3. Audio feedback chimes for:
   - Wake word activation ("Tink")
   - Command captured & dispatching ("Pop")
   - Timeout / idle return ("Bottle" / "Purr")
"""

import sys
import os
import time
import math
import logging
import subprocess
import threading
import numpy as np
import pyaudio
from pathlib import Path
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("hal-listener")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 0.015  # RMS audio threshold to detect speech vs silence
SILENCE_CHUNKS = 18        # ~1.1 seconds of trailing silence to finalize utterance
FOLLOWUP_TIMEOUT = 10.0    # Wait up to 10 seconds for follow-up command

TRIAGE_LAUNCHER = Path("/Users/matt/projects/ai-os/bin/triage-launcher.sh")

import re

WAKE_PATTERNS = [
    r"^(?:hey|hi|hello)?[ ,:;?!-]*\b(?:hal|how|howl|howel|howell|hell|owl|al|pal|cal)\b[ ,:;?!-]*",
]

def sanitize_command(raw_text: str) -> str:
    """Strips leading wake words and formatting punctuation cleanly."""
    text = raw_text.strip()
    if not text:
        return ""
    
    cleaned = text
    for pat in WAKE_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE).strip()
    
    # Strip any leftover leading punctuation
    cleaned = cleaned.lstrip(" ,:;?!-\n\t").strip()
    return cleaned

def dispatch_to_triage(prompt: str):
    """Dispatches prompt directly to aios triage launcher."""
    logger.info(f"🚀 DISPATCHING TO AI-OS TRIAGE: '{prompt}'")
    play_chime("Pop")
    try:
        subprocess.Popen(
            [str(TRIAGE_LAUNCHER), prompt],
            start_new_session=True
        )
    except Exception as e:
        logger.error(f"Failed to launch triage: {e}")

def get_rms(data: bytes) -> float:
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return float(np.sqrt(np.mean(samples**2)))

def show_gui_overlay(message: str = "🎙️ Hal is listening...", duration: float = 2.0):
    """Displays a fast floating HUD overlay on macOS via Hammerspoon or osascript."""
    try:
        # 1. Fast Hammerspoon HUD alert
        subprocess.Popen(
            ["hs", "-c", f'hs.alert.closeAll(); hs.alert.show("{message}", {duration})'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def play_chime(sound_name: str):
    """Plays a macOS built-in system sound."""
    sound_path = Path(f"/System/Library/Sounds/{sound_name}.aiff")
    if sound_path.exists():
        subprocess.Popen(
            ["afplay", str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def is_wake_word_present(raw_text: str) -> bool:
    """Checks if utterance starts with or contains any wake pattern."""
    for pat in WAKE_PATTERNS:
        if re.search(pat, raw_text, flags=re.IGNORECASE):
            return True
    return False

def main():
    logger.info("Initializing Whisper model (tiny.en)...")
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    logger.info("🟢 'Hal' is online and listening! (Say 'Hal', 'Hey Hal', or 'Hal <command>')")
    play_chime("Pop")

    buffer = []
    is_speaking = False
    silent_count = 0
    
    # State tracking
    is_active_listening = False
    active_until = 0.0

    try:
        while True:
            # Check for timeout if active
            if is_active_listening and time.time() > active_until:
                logger.info("⏱️ Active listening window timed out. Returning to idle.")
                is_active_listening = False
                play_chime("Purr")

            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            rms = get_rms(data)

            if rms > SILENCE_THRESHOLD:
                is_speaking = True
                silent_count = 0
                buffer.append(data)
            elif is_speaking:
                buffer.append(data)
                silent_count += 1
                if silent_count > SILENCE_CHUNKS:
                    # Finalize utterance
                    audio_bytes = b"".join(buffer)
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    segments, _ = model.transcribe(audio_np, beam_size=1, language="en")
                    raw_transcript = " ".join([s.text.strip() for s in segments]).strip()
                    
                    if raw_transcript:
                        logger.info(f"🎤 HEARD: \"{raw_transcript}\"")
                        
                        contains_wake = is_wake_word_present(raw_transcript)
                        command_part = sanitize_command(raw_transcript)

                        if contains_wake:
                            if command_part:
                                # Single utterance with command: "Hal, open google"
                                logger.info(f"🎯 Wake word + command detected: '{command_part}'")
                                show_gui_overlay(f"⚡ Hal: {command_part}", 1.5)
                                is_active_listening = False
                                dispatch_to_triage(command_part)
                            else:
                                # Just said "Hal" -> Enter active listening mode for 10s
                                logger.info("🎯 Wake word matched! Arming active listening for 10 seconds...")
                                show_gui_overlay("🎙️ Hal is listening...", 3.0)
                                is_active_listening = True
                                active_until = time.time() + FOLLOWUP_TIMEOUT
                        elif is_active_listening:
                            # We are in active listening mode and received a follow-up command!
                            logger.info(f"⚡ Follow-up command received in active window: '{raw_transcript}'")
                            show_gui_overlay(f"⚡ Hal: {raw_transcript}", 1.5)
                            is_active_listening = False
                            dispatch_to_triage(raw_transcript)
                    
                    buffer = []
                    is_speaking = False
                    silent_count = 0

    except KeyboardInterrupt:
        logger.info("Stopping Hal listener...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == "__main__":
    main()
