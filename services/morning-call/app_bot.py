"""Morning session for the iPhone app: same flow as bot.py, over a plain WebSocket of 16 kHz 16-bit mono PCM.

  uvicorn app_bot:app --host 0.0.0.0 --port 8798     (Mac, reached from the iPhone over Tailscale)
"""
import asyncio
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket

load_dotenv(Path.home()/"projects/ai-os/.env")
from pipecat.frames.frames import InputAudioRawFrame, OutputAudioRawFrame
from pipecat.serializers.base_serializer import FrameSerializer
import bot

RATE = 16000


class RawPCM(FrameSerializer):
    def __init__(self, skip):
        super().__init__()
        self.skip = skip

    async def serialize(self, frame):
        return frame.audio if isinstance(frame, OutputAudioRawFrame) else None

    async def deserialize(self, data):
        if data == "skip":
            self.skip.set()
        if isinstance(data, bytes):
            return InputAudioRawFrame(audio=data, sample_rate=RATE, num_channels=1)


app = FastAPI()


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/voices")
async def voices():
    """English Speechify voices for the app's picker."""
    data, cursor = [], None
    async with aiohttp.ClientSession() as session:
        while True:
            r = await session.get("https://api.speechify.ai/v1/voices", params={"cursor": cursor} if cursor else None,
                                  headers={"Authorization": "Bearer " + bot.clean("SPEECHIFY_API_KEY")})
            page = await r.json()
            data += page["voices"]
            cursor = page.get("next_cursor")
            if not page.get("has_more"):
                break
    english = [v for v in data if v.get("locale", "").startswith("en")]
    return sorted(({"id": v["id"], "name": v.get("display_name") or v["id"]} for v in english), key=lambda v: v["name"].lower())


@app.websocket("/ws")
async def ws(socket: WebSocket, stages: str = "breathe,meditate,checkin", voice: str = bot.VOICE, speed: int = bot.SPEED):
    await socket.accept()
    skip = asyncio.Event()
    async with aiohttp.ClientSession() as session:
        transport = bot.FastAPIWebsocketTransport(socket, bot.FastAPIWebsocketParams(
            audio_in_enabled=True, audio_out_enabled=True, add_wav_header=False,
            session_timeout=bot.MAX_CALL_SECS, serializer=RawPCM(skip)))
        await bot.run_session(transport, session, RATE, tuple(stages.split(",")), skip, 24000, voice, speed)
