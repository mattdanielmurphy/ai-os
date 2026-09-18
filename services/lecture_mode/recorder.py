# services/lecture_mode/recorder.py
import logging
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Optional

logger = logging.getLogger("lecture_mode.recorder")

class AudioRecorder:
    def __init__(self, mock: bool = False):
        self.mock = mock
        self.process: Optional[subprocess.Popen] = None
        self.output_dir: Optional[Path] = None
        self.chunks_dir: Optional[Path] = None
        self.start_time: Optional[float] = None
        self.processed_chunks: set[str] = set()

    def start(
        self,
        output_dir: Path | str,
        chunk_seconds: int = 10,
        sample_rate: int = 16000,
    ) -> None:
        if self.process and self.process.poll() is None:
            logger.warning("Audio recorder is already running")
            return

        self.output_dir = Path(output_dir)
        self.chunks_dir = self.output_dir / "chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        self.processed_chunks = set()
        self.start_time = time.time()

        if self.mock:
            logger.info("Starting AudioRecorder in MOCK mode")
            return

        # Use ffmpeg with avfoundation to record from default mic and segment into rolling WAV chunks
        chunk_pattern = str(self.chunks_dir / "chunk_%04d.wav")
        full_audio_path = str(self.output_dir / "lecture_full.wav")

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "avfoundation",
            "-i", ":default",
            "-ar", str(sample_rate),
            "-ac", "1",
            # Write continuous full lecture audio
            full_audio_path,
            # Simultaneously write rolling chunks for near-instant transcription
            "-f", "segment",
            "-segment_time", str(chunk_seconds),
            "-reset_timestamps", "1",
            chunk_pattern,
        ]

        logger.info(f"Launching ffmpeg audio capture: {' '.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid if hasattr(os, "setsid") else None,
        )

    def get_new_completed_chunks(self) -> list[Path]:
        """
        Returns newly completed chunk files in chronological order.
        Excludes the currently active (highest index) chunk since ffmpeg is still writing to it.
        """
        if self.mock:
            return []

        if not self.chunks_dir or not self.chunks_dir.exists():
            return []

        # Find all chunk files
        chunk_files = sorted(self.chunks_dir.glob("chunk_*.wav"))
        if len(chunk_files) <= 1:
            # Only 0 or 1 chunk exists; 1 chunk means it is still being actively recorded
            return []

        # All chunks except the last one are fully written and closed by ffmpeg segment muxer
        completed = chunk_files[:-1]
        new_chunks = []
        for c in completed:
            if c.name not in self.processed_chunks:
                # Ensure chunk has non-zero size
                if c.stat().st_size > 1024:
                    self.processed_chunks.add(c.name)
                    new_chunks.append(c)

        return new_chunks

    def stop(self) -> Optional[Path]:
        if self.mock:
            logger.info("Stopped mock recorder")
            return self.output_dir / "lecture_full.wav" if self.output_dir else None

        if not self.process:
            return None

        logger.info("Stopping ffmpeg audio recording...")
        try:
            # Send SIGINT to allow ffmpeg to finalize WAV headers
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        except Exception as e:
            logger.error(f"Error stopping recorder process: {e}")
        finally:
            self.process = None

        full_path = self.output_dir / "lecture_full.wav" if self.output_dir else None
        return full_path if full_path and full_path.exists() else None

    @property
    def is_recording(self) -> bool:
        if self.mock:
            return self.start_time is not None
        return self.process is not None and self.process.poll() is None
