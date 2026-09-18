# services/lecture_mode/transcript_store.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional

@dataclass
class TranscriptSegment:
    id: int
    start_seconds: float
    end_seconds: float
    timestamp_str: str
    text: str
    created_at_iso: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def markdown_line(self) -> str:
        return f"- **{self.timestamp_str}** {self.text}"

class TranscriptStore:
    def __init__(self, course_name: str = "Lecture", start_time: Optional[datetime] = None):
        self.course_name = course_name
        self.start_time = start_time or datetime.now()
        self.segments: list[TranscriptSegment] = []
        self._next_id = 1

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"[{mins:02d}:{secs:02d}]"

    def add_segment(self, start_sec: float, end_sec: float, text: str) -> TranscriptSegment:
        clean_text = text.strip()
        timestamp_str = self.format_timestamp(start_sec)
        seg = TranscriptSegment(
            id=self._next_id,
            start_seconds=start_sec,
            end_seconds=end_sec,
            timestamp_str=timestamp_str,
            text=clean_text,
        )
        self.segments.append(seg)
        self._next_id += 1
        return seg

    def get_all(self) -> list[TranscriptSegment]:
        return list(self.segments)

    def get_recent(self, seconds_back: float = 60.0) -> list[TranscriptSegment]:
        if not self.segments:
            return []
        latest_end = self.segments[-1].end_seconds
        cutoff = max(0.0, latest_end - seconds_back)
        return [s for s in self.segments if s.end_seconds >= cutoff]

    def search(self, query: str) -> list[TranscriptSegment]:
        q_low = query.lower()
        return [s for s in self.segments if q_low in s.text.lower()]

    def to_markdown(self) -> str:
        if not self.segments:
            return "_No spoken transcript recorded yet._"
        return "\n".join(s.markdown_line for s in self.segments)

    def to_json(self) -> list[dict]:
        return [s.to_dict() for s in self.segments]

    def save_json(self, output_path: Path | str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "course": self.course_name,
                    "start_time": self.start_time.isoformat(),
                    "segment_count": len(self.segments),
                    "segments": self.to_json(),
                },
                f,
                indent=2,
            )
