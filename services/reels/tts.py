"""Speechify TTS: text -> mp3 plus word timings. Key: SPEECHIFY_API_KEY (env or ai-os .env), never printed.

  tts.py <voice> "<text>" <out.mp3>      voice = a Speechify voice id (default beatrice_32); model simba-3.2

Uses /v1/audio/stream/with-timestamps (20,000 spoken chars per call), so the API returns the word timings
and the old speech-to-text pass is gone. Timings are cached next to the mp3 as <out>.marks.json.
"""
import base64, json, os, re, sys, urllib.error, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ENV = Path.home() / "projects" / "ai-os" / ".env"
HOST = "api.speechify.ai"
MODEL = "simba-3.2"
DEFAULT_VOICE = "beatrice_32"
OLD_VOICES = {"maeve", "gemma", "sharon", "pandora"}  # Deepgram names in older reel.json files


def key():
    """The key from the environment or ai-os .env. In a cloud session there is neither: the environment's
    Speechify network secret is attached by Anthropic's proxy instead, so we send no key (None)."""
    if os.environ.get("SPEECHIFY_API_KEY"):
        return os.environ["SPEECHIFY_API_KEY"]
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            if line.startswith("SPEECHIFY_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
        return None
    sys.exit("SPEECHIFY_API_KEY missing from ai-os .env")


def auth():
    k = key()
    return {"Authorization": f"Bearer {k}"} if k else {}


def call(req, timeout):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as err:
        if err.code in (401, 403) and not key():
            sys.exit(f"Speechify refused the request: this cloud environment needs a Speechify network secret "
                     f"(host {HOST}, header Authorization, prefix Bearer). See services/reels/README.md.")
        raise


def ssml(text, speed):
    """Plain text -> SSML. Blank lines and `...` lines become real pauses (<break>); `speed` is prosody rate."""
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text)]
    body = '<break time="500ms"/>'.join(escape(p) for p in paras if p.strip(". "))
    return f"<speak><prosody rate=\"{round(speed * 100)}%\">{body}</prosody></speak>"


def leaves(marks):
    """Flatten Speechify's nested speech marks to word leaves with start/end times."""
    for m in marks or []:
        if m.get("chunks"):
            yield from leaves(m["chunks"])
        elif m.get("value") and m.get("start_time") is not None:
            yield m


def speak(voice, text, out, speed=1.0):
    if not voice or voice in OLD_VOICES:
        voice = DEFAULT_VOICE
    body = {"input": ssml(text, speed), "voice_id": voice, "model": MODEL, "output_format": "mp3_24000_96",
            "options": {"text_normalization": False}}
    req = urllib.request.Request(f"https://{HOST}/v1/audio/stream/with-timestamps", data=json.dumps(body).encode(),
                                 method="POST", headers={**auth(), "Content-Type": "application/json"})
    audio, marks = bytearray(), []
    with call(req, 180) as r:
        for raw in r:
            line = raw.decode().strip()
            if not line.startswith("data:"):
                continue
            ev = json.loads(line[5:].strip())
            if ev.get("type") == "speech.chunk":
                if ev.get("audio"):
                    audio += base64.b64decode(ev["audio"])
                marks += ev.get("speech_marks") or []
            elif ev.get("type") == "speech.error":
                sys.exit(f"Speechify error: {json.dumps(ev)[:300]}")
    Path(out).write_bytes(bytes(audio))
    Path(str(out) + ".marks.json").write_text(json.dumps(marks))
    return out


def words(mp3):
    """Word timings for an mp3 from the marks saved by speak(): [{word, start, end}, …] in seconds."""
    marks = json.loads(Path(str(mp3) + ".marks.json").read_text())
    return [{"word": m["value"], "start": m["start_time"] / 1000, "end": m["end_time"] / 1000} for m in leaves(marks)]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__.strip())
    print(speak(sys.argv[1], sys.argv[2], sys.argv[3]))
