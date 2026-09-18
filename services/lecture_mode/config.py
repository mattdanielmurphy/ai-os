# services/lecture_mode/config.py
from dataclasses import dataclass, field
from pathlib import Path
import os

@dataclass
class LectureConfig:
    obsidian_vault_path: Path = field(
        default_factory=lambda: Path(
            os.path.expanduser(
                "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
            )
        )
    )
    lecture_notes_subpath: str = "School/Lectures"
    temp_dir: Path = field(
        default_factory=lambda: Path(os.path.expanduser("~/projects/ai-os/tmp/lectures"))
    )
    server_host: str = "127.0.0.1"
    server_port: int = 4141
    whisper_model: str = "base.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    chunk_duration_seconds: int = 10
    audio_sample_rate: int = 16000
    allowed_apps: list[str] = field(
        default_factory=lambda: [
            "Obsidian",
            "Notability",
            "Google Chrome",
            "Finder",
            "QSpace Pro",
        ]
    )

    @property
    def lecture_notes_dir(self) -> Path:
        return self.obsidian_vault_path / self.lecture_notes_subpath
