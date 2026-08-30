#!/usr/bin/env python3
# services/wake-hal/hal_listener.py
# Unified Hal Wake Word Listener & aios Triage Dispatcher.

import sys
import os
import time
import math
import logging
import subprocess
import threading
import shutil
import re
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
CHUNK_SIZE = 1024          # 64ms per chunk
SILENCE_THRESHOLD = 0.014  # RMS audio threshold to detect speech vs silence
SILENCE_CHUNKS = 12        # ~0.76 seconds of trailing silence to finalize utterance
INTERIM_MIN_CHUNKS = 6     # Check after ~384ms of audio
INTERIM_CHECK_INTERVAL = 5 # Check every ~320ms while speaking
FOLLOWUP_TIMEOUT = 10.0    # Wait up to 10 seconds for follow-up command

TRIAGE_LAUNCHER = Path("/Users/matt/projects/ai-os/bin/triage-launcher.sh")

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
    
    # Strip leftover leading punctuation
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
    # 1. Try Hammerspoon HUD alert (instant centered on-screen badge)
    try:
        lua = f'hs.alert.closeAll(); hs.alert.show([[{message}]], {duration})'
        applescript = f'tell application "Hammerspoon" to execute lua code "{lua}"'
        res = subprocess.run(
            ["osascript", "-e", applescript],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=0.6
        )
        if res.returncode == 0:
            return
    except Exception:
        pass

    # 2. Fallback to native macOS Notification Center banner
    try:
        clean_msg = message.replace('"', '\\"')
        subprocess.Popen(
            ["osascript", "-e", f'display notification "{clean_msg}" with title "🎙️ Hal"'],
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
    early_wake_detected = False
    last_interim_check_chunks = 0

    try:
        while True:
            # Check for timeout if in active listening state
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

                # Real-time interim wake detection WHILE STILL SPEAKING:
                # If we haven't triggered wake word yet for this utterance and we're not in active mode,
                # check the partial audio buffer every ~320ms once we have >= ~384ms of audio.
                curr_chunks = len(buffer)
                if (not early_wake_detected and not is_active_listening and
                        curr_chunks >= INTERIM_MIN_CHUNKS and
                        (curr_chunks - last_interim_check_chunks) >= INTERIM_CHECK_INTERVAL):
                    
                    last_interim_check_chunks = curr_chunks
                    partial_bytes = b"".join(buffer)
                    partial_np = np.frombuffer(partial_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    try:
                        segments, _ = model.transcribe(partial_np, beam_size=1, language="en")
                        partial_transcript = " ".join([s.text.strip() for s in segments]).strip()
                        if partial_transcript and is_wake_word_present(partial_transcript):
                            early_wake_detected = True
                            logger.info(f"🎯 Early wake word detected while speaking ('{partial_transcript}')! Triggering HUD notification immediately.")
                            show_gui_overlay("🎙️ Hal is listening...", 4.0)
                            play_chime("Tink")
                    except Exception as e:
                        logger.debug(f"Interim transcription check error: {e}")

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
                        
                        contains_wake = early_wake_detected or is_wake_word_present(raw_transcript)
                        command_part = sanitize_command(raw_transcript)

                        if contains_wake:
                            if command_part:
                                # Single utterance with command: "Hal, open google"
                                logger.info(f"🎯 Wake word + command detected: '{command_part}'")
                                show_gui_overlay(f"⚡ Hal: {command_part}", 2.0)
                                is_active_listening = False
                                dispatch_to_triage(command_part)
                            else:
                                # Just said "Hal" -> Enter active listening mode for 10s
                                logger.info("🎯 Wake word matched! Arming active listening for 10 seconds...")
                                show_gui_overlay("🎙️ Hal is listening...", 4.0)
                                is_active_listening = True
                                active_until = time.time() + FOLLOWUP_TIMEOUT
                        elif is_active_listening:
                            # We are in active listening mode and received a follow-up command!
                            logger.info(f"⚡ Follow-up command received in active window: '{raw_transcript}'")
                            show_gui_overlay(f"⚡ Hal: {raw_transcript}", 2.0)
                            is_active_listening = False
                            dispatch_to_triage(raw_transcript)
                    
                    # Reset state for next utterance
                    buffer = []
                    is_speaking = False
                    silent_count = 0
                    early_wake_detected = False
                    last_interim_check_chunks = 0

    except KeyboardInterrupt:
        logger.info("Stopping Hal listener...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == "__main__":
    main()
