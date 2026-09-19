"""Groq Cloud Speech-to-Text (STT) Client using whisper-large-v3-turbo."""

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Optional
import httpx

logger = logging.getLogger("assistant.telegram_gateway.stt")

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_WHISPER_MODEL = "whisper-large-v3-turbo"


def extract_audio_from_video(video_path: Path, output_audio_path: Optional[Path] = None) -> Optional[Path]:
    """
    Extracts the audio stream from a video or video-note file using ffmpeg.
    Returns the path to the extracted mp3 audio file or None if ffmpeg is missing/fails.
    """
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        logger.error("ffmpeg binary not found for video audio extraction.")
        return None

    if output_audio_path is None:
        output_audio_path = video_path.with_suffix(".mp3")

    try:
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "4",
            str(output_audio_path),
        ]
        import subprocess
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if output_audio_path.exists() and output_audio_path.stat().st_size > 0:
            logger.info(f"Extracted audio from video {video_path.name} to {output_audio_path.name}")
            return output_audio_path
        return None
    except Exception as e:
        logger.error(f"Failed to extract audio from video {video_path}: {e}")
        return None


async def transcribe_audio_file(
    audio_path: Path,
    api_key: Optional[str] = None,
    model: str = DEFAULT_WHISPER_MODEL,
    prompt: Optional[str] = None,
) -> Optional[str]:
    """
    Transcribes an audio file (.ogg, .oga, .mp3, .wav, .m4a, .webm, etc.) using Groq's cloud Whisper API.
    Returns the transcribed text string or None if transcription failed.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        logger.error("No GROQ_API_KEY found for audio transcription.")
        return None

    if not audio_path.exists():
        logger.error(f"Audio file does not exist: {audio_path}")
        return None

    headers = {
        "Authorization": f"Bearer {key}",
    }

    filename = audio_path.name
    ext = audio_path.suffix.lower()
    if ext in (".ogg", ".oga"):
        content_type = "audio/ogg"
    elif ext == ".mp3":
        content_type = "audio/mpeg"
    elif ext == ".wav":
        content_type = "audio/wav"
    elif ext == ".m4a":
        content_type = "audio/m4a"
    elif ext == ".webm":
        content_type = "audio/webm"
    elif ext == ".flac":
        content_type = "audio/flac"
    else:
        content_type = f"audio/{ext.lstrip('.')}"

    data = {
        "model": model,
        "response_format": "json",
    }
    if prompt:
        data["prompt"] = prompt

    try:
        with open(audio_path, "rb") as f:
            file_bytes = f.read()

        files = {
            "file": (filename, file_bytes, content_type)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                GROQ_TRANSCRIPTION_URL,
                headers=headers,
                data=data,
                files=files,
            )
            if resp.status_code != 200:
                logger.error(f"Groq STT API returned status {resp.status_code}: {resp.text}")
                return None

            result = resp.json()
            transcript = result.get("text", "").strip()
            logger.info(f"Groq STT transcription complete ({len(transcript)} chars)")
            return transcript
    except Exception as e:
        logger.error(f"Error during Groq STT transcription: {e}")
        return None
