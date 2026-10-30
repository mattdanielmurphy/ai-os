"""Morning call: Twilio -> Pipecat. Scripted breathing and meditation with the mic off, then a Claude check-in.

  POST /call?token=...   places the call     GET /health   says it's up
Runs on the VPS (morning-call.service) behind Caddy at https://vps.mattmurphy.ca/morning-call/
"""
import asyncio, os, re
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket

load_dotenv(Path(__file__).with_name(".env"))
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (BotStartedSpeakingFrame, BotStoppedSpeakingFrame, EndFrame, InputAudioRawFrame, InterruptionFrame, LLMRunFrame, TTSSpeakFrame)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.anthropic.llm import AnthropicLLMService, AnthropicLLMSettings
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.speechify.tts import SpeechifyHttpTTSService, SpeechifyTTSSettings
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams, FastAPIWebsocketTransport

# Feel knobs
VOICE = "marian"
MODEL = "claude-sonnet-5-5"
MAX_CALL_SECS = 20 * 60
BREATH_IN, BREATH_OUT = 4, 6     # s of quiet after each cue
SIT_SECS = 45                    # s of silent meditation

BASE = "https://vps.mattmurphy.ca/morning-call"
SAY_AS = {"CMPUT": "computing", "PHIL": "philosophy"}  # phone-tested word list

BREATHE = [("Good morning, Matt. Stay where you are for now. We'll start with three slow breaths.", 2)]
for _ in range(3):
    BREATHE += [("Breathe in.", BREATH_IN), ("And out.", BREATH_OUT)]
MEDITATE = [("Let your breathing go back to normal, and just watch it. I'll stay quiet for a little while.", SIT_SECS),
            ("Okay. Gently open your eyes.", 3)]
STAGES = {"breathe": BREATHE, "meditate": MEDITATE}

SYSTEM = """You are Matt's warm, plain-spoken morning check-in on a phone call. Sound like a good therapist who is also a friend: curious, brief, never chirpy. One or two short sentences at a
time, then listen. Ask how he's doing, then what he has to do today, then help him pick the first small step. Your real job
is getting him out of bed: before ending, ask him to put his feet on the floor and stand up, and wait until he says he has.
Then say a short goodbye. This is speech: no lists, symbols or markdown; write numbers and course codes as they're said."""


def spoken(text):
    for word, say in SAY_AS.items():
        text = re.sub(rf"\b{word}\b", say, text)
    return text


def clean(key):
    return re.sub(r"[^A-Za-z0-9_-]", "", os.environ[key])


class MicGate(FrameProcessor):
    """Drops his audio during the scripted part and while the bot talks, so it can't hear and interrupt itself."""
    open = False
    speaking = False

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        if isinstance(frame, BotStartedSpeakingFrame):
            self.speaking = True
        elif isinstance(frame, BotStoppedSpeakingFrame):
            self.speaking = False
        if not isinstance(frame, InputAudioRawFrame) or (self.open and not self.speaking):
            await self.push_frame(frame, direction)


class SpokeWatch(FrameProcessor):
    """Fires when the bot's audio has really finished, so pauses are timed from the end of the words."""
    def __init__(self):
        super().__init__()
        self.done = asyncio.Event()

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        if isinstance(frame, BotStoppedSpeakingFrame):
            self.done.set()
        await self.push_frame(frame, direction)


async def run_session(transport, session, rate, stages=("breathe", "meditate", "checkin"), skip=None, out_rate=None):
    skip = skip or asyncio.Event()  # set to jump straight to the check-in
    tts = SpeechifyHttpTTSService(api_key=clean("SPEECHIFY_API_KEY"), aiohttp_session=session,
                                  settings=SpeechifyTTSSettings(voice=VOICE, model="simba-3.2"))
    context = LLMContext([{"role": "system", "content": SYSTEM}])
    turns = LLMContextAggregatorPair(context)
    gate, watch = MicGate(), SpokeWatch()
    task = PipelineTask(Pipeline([
        transport.input(), gate, VADProcessor(vad_analyzer=SileroVADAnalyzer()),
        DeepgramSTTService(api_key=clean("DEEPGRAM_API_KEY")), turns.user(),
        AnthropicLLMService(api_key=clean("ANTHROPIC_API_KEY"), settings=AnthropicLLMSettings(model=MODEL)),
        tts, transport.output(), watch, turns.assistant()]),
        params=PipelineParams(audio_in_sample_rate=rate, audio_out_sample_rate=out_rate or rate),
        idle_timeout_secs=None)  # the default 300 s would hang up during meditation

    async def flow():
        lines = [item for name in stages for item in STAGES.get(name, [])]
        for line, pause in lines:
            if skip.is_set():
                await task.queue_frame(InterruptionFrame())
                break
            watch.done.clear()
            await task.queue_frame(TTSSpeakFrame(spoken(line)))
            await asyncio.wait_for(watch.done.wait(), 30)
            try:
                await asyncio.wait_for(skip.wait(), pause)
            except asyncio.TimeoutError:
                pass
        if "checkin" not in stages:
            await task.queue_frame(TTSSpeakFrame("That's all for this morning."))
            await task.queue_frame(EndFrame())
            return
        gate.open = True
        note = "Begin the check-in." if lines and not skip.is_set() else "He went straight to the check-in, with no breathing or meditation. Begin."
        context.add_message({"role": "user", "content": f"({note})"})
        await task.queue_frame(LLMRunFrame())

    @transport.event_handler("on_client_connected")
    async def connected(_t, _c):
        asyncio.create_task(flow())

    @transport.event_handler("on_client_disconnected")
    async def gone(_t, _c):
        await task.queue_frame(EndFrame())

    await PipelineRunner(handle_sigint=False).run(task)


async def run_call(ws):
    _, call = await parse_telephony_websocket(ws)
    async with aiohttp.ClientSession() as session:
        await run_session(FastAPIWebsocketTransport(ws, FastAPIWebsocketParams(
            audio_in_enabled=True, audio_out_enabled=True, add_wav_header=False, session_timeout=MAX_CALL_SECS,
            serializer=TwilioFrameSerializer(stream_sid=call["stream_id"], call_sid=call["call_id"],
                                             account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                                             auth_token=os.environ["TWILIO_AUTH_TOKEN"]))), session, 8000)


app = FastAPI()


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/call")
async def call(token: str):
    if token != os.environ["CALL_TOKEN"]:
        raise HTTPException(403)
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    twiml = f'<Response><Connect><Stream url="{BASE.replace("https", "wss")}/ws"/></Connect></Response>'
    auth = aiohttp.BasicAuth(sid, os.environ["TWILIO_AUTH_TOKEN"])
    async with aiohttp.ClientSession(auth=auth) as s:
        r = await s.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json", data={
            "To": os.environ["MATT_PHONE"], "From": os.environ["TWILIO_PHONE_NUMBER"], "Twiml": twiml})
        body = await r.json()
    if r.status >= 300:
        raise HTTPException(502, body.get("message", "twilio refused"))
    return {"call": body["sid"]}


@app.websocket("/ws")
async def ws(socket: WebSocket):
    await socket.accept()
    await run_call(socket)
