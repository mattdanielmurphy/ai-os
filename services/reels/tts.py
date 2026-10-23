#!/usr/bin/env python3
"""Deepgram Flux TTS: text -> mp3. Key comes from ai-os .env (DEEPGRAM_API_KEY), never printed.

  tts.py <voice> "<text>" <out.mp3>      voice = maeve, gemma, sharon ... (flux-<voice>-en), or pandora (aura-2)
"""
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ENV = Path.home() / "projects" / "ai-os" / ".env"

def key():
    """The key from the environment or ai-os .env. In a cloud session there is neither: the environment's
    Deepgram network secret is attached by Anthropic's proxy instead, so we send no key (None)."""
    if os.environ.get("DEEPGRAM_API_KEY"):
        return os.environ["DEEPGRAM_API_KEY"]
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if line.startswith("DEEPGRAM_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
        return None
    sys.exit("DEEPGRAM_API_KEY missing from ai-os .env")


def auth():
    k = key()
    return {"Authorization": f"Token {k}"} if k else {}


def call(req, timeout):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as err:
        if err.code in (401, 403) and not key():
            sys.exit("Deepgram refused the request: this cloud environment needs a Deepgram network secret "
                     "(host api.deepgram.com, header Authorization, prefix Token). See services/reels/README.md.")
        raise


# Flux has one British woman (gemma); Aura-2 voices fill the gaps (Aura is v1/speak only)
AURA = {"pandora": "aura-2-pandora-en"}

def speak(voice, text, out, speed=1.0):
    model, ver = (AURA[voice], "v1") if voice in AURA else (f"flux-{voice}-en", "v2")
    url = f"https://api.deepgram.com/{ver}/speak?model={model}&encoding=mp3&bit_rate=48000&speed={speed}"
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode(), method="POST",
                                 headers={**auth(), "Content-Type": "application/json"})
    with call(req, 60) as r:
        Path(out).write_bytes(r.read())
    return out

def words(mp3):
    """Word timings for an mp3 via Deepgram speech-to-text: [{word, start, end}, …]."""
    req = urllib.request.Request("https://api.deepgram.com/v1/listen?model=nova-3&punctuate=true",
                                 data=Path(mp3).read_bytes(), method="POST",
                                 headers={**auth(), "Content-Type": "audio/mpeg"})
    with call(req, 120) as r:
        res = json.load(r)
    return res["results"]["channels"][0]["alternatives"][0]["words"]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__.strip())
    print(speak(sys.argv[1], sys.argv[2], sys.argv[3]))
