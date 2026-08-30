#!/usr/bin/env python3
"""
services/wake-hal/monitor.py
Real-time audio listener & live speech transcription monitor.

Displays:
1. Live microphone audio input level (VU meter).
2. Live on-device speech-to-text (transcribes whatever you say into the mic).
3. Detects if "Hal" or any wake word is spoken and shows the match.
"""

import sys
import time
import math
import numpy as np
import pyaudio
from faster_whisper import WhisperModel
import subprocess

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 0.015  # RMS audio threshold to detect speech vs silence
SILENCE_CHUNKS = 20        # ~1.2 seconds of silence to finalize utterance

def get_rms(data: bytes) -> float:
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return float(np.sqrt(np.mean(samples**2)))

def vu_bar(rms: float, width: int = 25) -> str:
    level = min(width, int(rms * 150))
    bar = "█" * level + "░" * (width - level)
    return bar

def main():
    print("=" * 60)
    print("🎙️  HAL AUDIO & SPEECH LIVE MONITOR")
    print("=" * 60)
    print("Loading fast on-device Whisper model (tiny.en)...")
    model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    print("✅ Model loaded! Opening default microphone...")

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    print("\n🟢 LISTENING NOW! Speak into your microphone:")
    print("------------------------------------------------------------")

    buffer = []
    is_speaking = False
    silent_count = 0

    try:
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            rms = get_rms(data)
            
            # Print live VU meter on same line
            bar = vu_bar(rms)
            status = "🗣️ SPEECH" if rms > SILENCE_THRESHOLD else "💤 IDLE  "
            sys.stdout.write(f"\r[{status}] VU: |{bar}| (RMS: {rms:.4f})")
            sys.stdout.flush()

            if rms > SILENCE_THRESHOLD:
                is_speaking = True
                silent_count = 0
                buffer.append(data)
            elif is_speaking:
                buffer.append(data)
                silent_count += 1
                if silent_count > SILENCE_CHUNKS:
                    # Finalize utterance
                    sys.stdout.write("\nTranscribing utterance...\n")
                    sys.stdout.flush()
                    
                    audio_bytes = b"".join(buffer)
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    segments, _ = model.transcribe(audio_np, beam_size=1, language="en")
                    text = " ".join([s.text.strip() for s in segments]).strip()
                    
                    if text:
                        print(f"👉 HEARD: \"{text}\"")
                        if any(w in text.lower() for w in ["hal", "hey hal", "how", "hello hal", "hi hal"]):
                            print(f"🎯 >>> MATCHED HAL WAKE WORD! <<<")
                            subprocess.Popen(["afplay", "/System/Library/Sounds/Tink.aiff"])
                    
                    print("------------------------------------------------------------")
                    buffer = []
                    is_speaking = False
                    silent_count = 0

    except KeyboardInterrupt:
        print("\nExiting monitor.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

if __name__ == "__main__":
    main()
