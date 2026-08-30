#!/usr/bin/env python3
"""
services/wake-hal/daemon.py
Hal Wake Word Listener Daemon.

Listens on the default microphone using Sherpa-ONNX Zipformer KWS (Keyword Spotting)
for the wake word "Hal" / "Hey Hal".
When detected:
1. Plays an activation feedback sound (e.g. Tink / Pop).
2. Triggers TypeWhisper dictation hotkey (double-tap Option).
3. Tells the bridge to expect a wake session.
"""

import os
import sys
import time
import logging
import threading
import subprocess
import numpy as np
import pyaudio
import sherpa_onnx
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parent
MODEL_DIR = SERVICE_DIR / "models" / "sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01"

from bridge import TypeWhisperDBWatcher, dispatch_to_triage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("wake-hal-daemon")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024  # 64ms at 16kHz
COOLDOWN_SECONDS = 2.5

def play_chime(sound_name: str = "Tink"):
    """Plays a built-in macOS alert sound for immediate audio feedback."""
    try:
        subprocess.Popen(
            ["afplay", f"/System/Library/Sounds/{sound_name}.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.debug(f"Audio playback error: {e}")

def trigger_typewhisper():
    """Triggers TypeWhisper dictation.
    TypeWhisper is configured for double-tap Option or Fn key.
    We simulate Option double-tap via osascript System Events.
    """
    logger.info("Triggering TypeWhisper dictation hotkey...")
    applescript = '''
    tell application "System Events"
        key code 58
        delay 0.08
        key code 58
    end tell
    '''
    try:
        subprocess.Popen(
            ["osascript", "-e", applescript],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Failed to trigger TypeWhisper hotkey: {e}")

class HalWakeWordListener:
    def __init__(self):
        logger.info(f"Loading Sherpa-ONNX model from {MODEL_DIR}...")
        self.kws = sherpa_onnx.KeywordSpotter(
            tokens=str(MODEL_DIR / "tokens.txt"),
            encoder=str(MODEL_DIR / "encoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx"),
            decoder=str(MODEL_DIR / "decoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx"),
            joiner=str(MODEL_DIR / "joiner-epoch-12-avg-2-chunk-16-left-64.int8.onnx"),
            keywords_file=str(MODEL_DIR / "hal_keywords.txt"),
            num_threads=2,
            keywords_score=1.0,
            keywords_threshold=0.20,
            provider="cpu"
        )
        self.stream = self.kws.create_stream()
        self.pa = pyaudio.PyAudio()
        self.last_detection_time = 0.0
        self.running = False
        
        # Start DB watcher in background thread
        self.db_watcher = TypeWhisperDBWatcher()
        self.watcher_thread = threading.Thread(target=self.db_watcher.run, daemon=True)
        self.watcher_thread.start()

    def start(self):
        logger.info("Opening microphone stream (16kHz, mono, 16-bit PCM)...")
        audio_stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        self.running = True
        logger.info("🟢 'Hal' wake word listener is active and listening! (Say 'Hal' or 'Hey Hal')")
        play_chime("Pop")

        try:
            while self.running:
                data = audio_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                self.stream.accept_waveform(SAMPLE_RATE, samples)
                while self.kws.is_ready(self.stream):
                    self.kws.decode_stream(self.stream)
                    result = self.kws.get_result(self.stream)
                    keyword = getattr(result, "keyword", None) or (str(result) if result else None)
                    if keyword and keyword.strip():
                        now = time.time()
                        if now - self.last_detection_time > COOLDOWN_SECONDS:
                            self.last_detection_time = now
                            logger.info(f"🎯 WAKE WORD DETECTED: '{keyword}'")
                            play_chime("Tink")
                            self.db_watcher.expect_wake_session()
                            trigger_typewhisper()
                        
                        # Reset stream after keyword match
                        self.stream = self.kws.create_stream()
                        
        except KeyboardInterrupt:
            logger.info("Stopping listener...")
        finally:
            self.running = False
            audio_stream.stop_stream()
            audio_stream.close()
            self.pa.terminate()

def main():
    listener = HalWakeWordListener()
    listener.start()

if __name__ == "__main__":
    main()
