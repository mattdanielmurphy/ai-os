# services/lecture_mode/engine.py
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import subprocess
import time
from typing import Callable, Optional

from services.lecture_mode.config import LectureConfig
from services.lecture_mode.note_syncer import LectureNoteSyncer
from services.lecture_mode.recorder import AudioRecorder
from services.lecture_mode.slide_parser import extract_terms_of_art, extract_text_from_pdf
from services.lecture_mode.transcript_store import TranscriptSegment, TranscriptStore
from services.lecture_mode.transcriber import LectureTranscriber

logger = logging.getLogger("lecture_mode.engine")

class LectureEngine:
    def __init__(self, config: Optional[LectureConfig] = None, mock: bool = False):
        self.config = config or LectureConfig()
        self.mock = mock

        self.recorder = AudioRecorder(mock=mock)
        self.transcriber = LectureTranscriber(
            model_name=self.config.whisper_model,
            device=self.config.whisper_device,
            compute_type=self.config.whisper_compute_type,
            mock=mock,
        )
        self.note_syncer = LectureNoteSyncer(
            vault_path=self.config.obsidian_vault_path,
            lectures_subpath=self.config.lecture_notes_subpath,
        )

        self.active_course: Optional[str] = None
        self.session_dir: Optional[Path] = None
        self.store: Optional[TranscriptStore] = None
        self.start_time: Optional[datetime] = None
        self.start_monotonic: Optional[float] = None
        self.terms_of_art: list[str] = []

        self._processing_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._listeners: list[Callable[[TranscriptSegment], None]] = []

    def subscribe(self, listener: Callable[[TranscriptSegment], None]) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[TranscriptSegment], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _broadcast(self, segment: TranscriptSegment) -> None:
        for cb in list(self._listeners):
            try:
                cb(segment)
            except Exception as e:
                logger.error(f"Error in transcript listener: {e}")

    def ingest_slides(self, slide_path: Path | str) -> list[str]:
        """Ingests a slide deck (PDF), extracts technical terms of art, and primes transcriber."""
        path = Path(slide_path)
        logger.info(f"Ingesting lecture slides from {path}...")
        raw_text = extract_text_from_pdf(path)
        terms = extract_terms_of_art(raw_text)
        self.terms_of_art = terms
        self.transcriber.set_slide_vocabulary(terms)
        logger.info(f"Extracted {len(terms)} technical terms of art.")
        return terms

    def set_terms_of_art(self, terms: list[str]) -> None:
        self.terms_of_art = terms
        self.transcriber.set_slide_vocabulary(terms)

    async def start_lecture(
        self,
        course_name: str,
        slide_path: Optional[Path | str] = None,
        engage_hammerspoon_lock: bool = True,
    ) -> dict:
        if self._is_running:
            return {"status": "already_running", "course": self.active_course}

        self.active_course = course_name
        self.start_time = datetime.now()
        self.start_monotonic = time.monotonic()
        self._is_running = True

        # Session staging directory
        date_str = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        safe_course = course_name.replace(" ", "_").lower()
        self.session_dir = self.config.temp_dir / f"{date_str}_{safe_course}"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Transcript Store
        self.store = TranscriptStore(course_name=course_name, start_time=self.start_time)

        # Ingest slides if provided
        if slide_path:
            self.ingest_slides(slide_path)

        # Initialize Obsidian lecture note
        note_path = self.note_syncer.init_lecture_note(
            course_name=course_name,
            terms_of_art=self.terms_of_art,
            date=self.start_time,
        )

        # Start audio capture
        self.recorder.start(
            output_dir=self.session_dir,
            chunk_seconds=self.config.chunk_duration_seconds,
            sample_rate=self.config.audio_sample_rate,
        )

        # Engage Hammerspoon Lecture Mode if requested
        if engage_hammerspoon_lock and not self.mock:
            try:
                subprocess.run(
                    ["hs", "-c", "require('modules.lecture_mode').activate()"],
                    capture_output=True,
                    timeout=3,
                )
            except Exception as e:
                logger.warning(f"Could not engage Hammerspoon lecture mode: {e}")

        # Start background chunk processor
        self._processing_task = asyncio.create_task(self._process_chunks_loop())

        logger.info(f"Lecture session started for '{course_name}' at {self.start_time}")
        return {
            "status": "started",
            "course": course_name,
            "session_dir": str(self.session_dir),
            "note_path": str(note_path),
            "terms_count": len(self.terms_of_art),
        }

    async def _process_chunks_loop(self) -> None:
        logger.info("Started chunk processing loop.")
        while self._is_running:
            try:
                await asyncio.sleep(2.0)
                new_chunks = self.recorder.get_new_completed_chunks()
                for chunk in new_chunks:
                    # Determine chunk offset relative to session start
                    # chunk_%04d where index * chunk_duration gives offset
                    offset = 0.0
                    stem = chunk.stem  # chunk_0001
                    if "_" in stem:
                        try:
                            idx = int(stem.split("_")[-1])
                            offset = idx * self.config.chunk_duration_seconds
                        except ValueError:
                            pass

                    logger.info(f"Transcribing audio chunk {chunk.name} (offset: {offset:.1f}s)...")
                    segments = self.transcriber.transcribe_chunk(chunk, offset_seconds=offset)
                    for abs_start, abs_end, text in segments:
                        seg = self.store.add_segment(abs_start, abs_end, text)
                        self._broadcast(seg)

                # Persist ongoing state
                if self.session_dir and self.store:
                    self.store.save_json(self.session_dir / "transcript.json")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in chunk processing loop: {e}", exc_info=True)

    async def stop_lecture(self, disengage_hammerspoon_lock: bool = True) -> dict:
        if not self._is_running:
            return {"status": "not_running"}

        self._is_running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        # Stop audio recorder
        full_audio_path = self.recorder.stop()

        # Finalize transcript in store
        transcript_md = self.store.to_markdown() if self.store else ""
        if self.session_dir and self.store:
            self.store.save_json(self.session_dir / "transcript_final.json")

        # Finalize Obsidian lecture note
        note_path = None
        if self.active_course and self.store:
            note_path = self.note_syncer.finalize_lecture_note(
                course_name=self.active_course,
                transcript_markdown=transcript_md,
                audio_path=full_audio_path,
                date=self.start_time,
            )

        # Trigger Hammerspoon exit
        if disengage_hammerspoon_lock and not self.mock:
            try:
                subprocess.run(
                    ["hs", "-c", "require('modules.lecture_mode').requestExit()"],
                    capture_output=True,
                    timeout=3,
                )
            except Exception as e:
                logger.warning(f"Could not disengage Hammerspoon lecture mode: {e}")

        course_ended = self.active_course
        total_segments = len(self.store.segments) if self.store else 0

        self.active_course = None
        self.session_dir = None
        self.store = None

        logger.info(f"Lecture session for '{course_ended}' finalized with {total_segments} segments.")
        return {
            "status": "stopped",
            "course": course_ended,
            "segments_count": total_segments,
            "note_path": str(note_path) if note_path else None,
            "audio_path": str(full_audio_path) if full_audio_path else None,
        }

    @property
    def is_running(self) -> bool:
        return self._is_running
