# services/lecture_mode/transcriber.py
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("lecture_mode.transcriber")

class LectureTranscriber:
    def __init__(
        self,
        model_name: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        mock: bool = False,
    ):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.mock = mock
        self._model = None
        self.initial_prompt: str = ""

    def set_slide_vocabulary(self, terms: list[str]) -> None:
        """Sets the technical terms of art prompt to bias Whisper's attention weights."""
        from services.lecture_mode.slide_parser import build_whisper_initial_prompt
        self.initial_prompt = build_whisper_initial_prompt(terms)
        logger.info(f"Updated initial_prompt ({len(self.initial_prompt)} chars): {self.initial_prompt[:100]}...")

    def _ensure_model(self):
        if self.mock or self._model is not None:
            return
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model '{self.model_name}' on {self.device} ({self.compute_type})...")
        self._model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
        )
        logger.info("WhisperModel loaded successfully.")

    def transcribe_chunk(
        self,
        audio_path: Path | str,
        offset_seconds: float = 0.0,
    ) -> list[tuple[float, float, str]]:
        """
        Transcribes an audio chunk file.
        Returns list of (absolute_start_seconds, absolute_end_seconds, text).
        """
        if self.mock:
            return [
                (offset_seconds, offset_seconds + 5.0, "This is a synthetic mock lecture segment."),
            ]

        self._ensure_model()
        path_str = str(audio_path)

        segments, info = self._model.transcribe(
            path_str,
            beam_size=5,
            initial_prompt=self.initial_prompt if self.initial_prompt else None,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400),
        )

        results = []
        for s in segments:
            text = s.text.strip()
            if text:
                abs_start = round(offset_seconds + s.start, 2)
                abs_end = round(offset_seconds + s.end, 2)
                results.append((abs_start, abs_end, text))

        return results
