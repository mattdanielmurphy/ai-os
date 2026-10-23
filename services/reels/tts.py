#!/usr/bin/env python3
"""Deepgram Flux TTS: text -> mp3. Key comes from ai-os .env (DEEPGRAM_API_KEY), never printed.

  tts.py <voice> "<text>" <out.mp3>      voice = maeve, gemma, sharon ... (flux-<voice>-en)
"""
import json, os, sys, urllib.request
from pathlib import Path

ENV = Path.home() / "projects" / "ai-os" / ".env"

def key():
    if os.environ.get("DEEPGRAM_API_KEY"):
        return os.environ["DEEPGRAM_API_KEY"]
    for line in ENV.read_text().splitlines():
        if line.startswith("DEEPGRAM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("DEEPGRAM_API_KEY missing from ai-os .env")

def speak(voice, text, out, speed=1.0):
    url = f"https://api.deepgram.com/v2/speak?model=flux-{voice}-en&encoding=mp3&bit_rate=48000&speed={speed}"
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode(), method="POST",
                                 headers={"Authorization": f"Token {key()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        Path(out).write_bytes(r.read())
    return out

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__.strip())
    print(speak(sys.argv[1], sys.argv[2], sys.argv[3]))
