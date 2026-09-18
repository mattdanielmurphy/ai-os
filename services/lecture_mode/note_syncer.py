# services/lecture_mode/note_syncer.py
from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Optional

logger = logging.getLogger("lecture_mode.note_syncer")

class LectureNoteSyncer:
    def __init__(self, vault_path: Path | str, lectures_subpath: str = "School/Lectures"):
        self.vault_path = Path(vault_path)
        self.lectures_dir = self.vault_path / lectures_subpath
        self.lectures_dir.mkdir(parents=True, exist_ok=True)

    def get_note_path(self, course_name: str, date: Optional[datetime] = None) -> Path:
        d = date or datetime.now()
        date_str = d.strftime("%Y-%m-%d")
        safe_course = re.sub(r'[\\/*?:"<>|]', "", course_name).strip()
        filename = f"{date_str} - {safe_course}.md"
        return self.lectures_dir / filename

    def init_lecture_note(
        self,
        course_name: str,
        terms_of_art: list[str],
        date: Optional[datetime] = None,
    ) -> Path:
        d = date or datetime.now()
        note_path = self.get_note_path(course_name, d)
        date_str = d.strftime("%Y-%m-%d")
        time_str = d.strftime("%H:%M")

        # Format terms as inline chips
        if terms_of_art:
            terms_md = " ".join(f"`{t}`" for t in terms_of_art[:25])
        else:
            terms_md = "_No slides ingested yet._"

        if note_path.exists():
            logger.info(f"Lecture note already exists at {note_path}, updating headers...")
            content = note_path.read_text(encoding="utf-8")
            # If terms were updated and terms section exists, update it
            if "## 🧠 Key Terms of Art" in content and terms_of_art:
                content = re.sub(
                    r"## 🧠 Key Terms of Art\n[^\n#]+",
                    f"## 🧠 Key Terms of Art\n{terms_md}\n",
                    content,
                )
                note_path.write_text(content, encoding="utf-8")
            return note_path

        template = f"""---
date: {date_str}
time: "{time_str}"
course: "{course_name}"
type: lecture-notes
tags:
  - school/lecture
  - ualberta
---

# {course_name} — {date_str}

## 🧠 Key Terms of Art
{terms_md}

## 📝 Live Notes
- 

## 🎙️ Spoken Transcript
> [!quote]- Full Audio-Synced Transcript
> _Recording in progress... Transcript will be finalized upon lecture completion._
"""
        note_path.write_text(template, encoding="utf-8")
        logger.info(f"Initialized new lecture note: {note_path}")
        return note_path

    def finalize_lecture_note(
        self,
        course_name: str,
        transcript_markdown: str,
        audio_path: Optional[Path | str] = None,
        date: Optional[datetime] = None,
    ) -> Path:
        d = date or datetime.now()
        note_path = self.get_note_path(course_name, d)
        if not note_path.exists():
            self.init_lecture_note(course_name, [], d)

        content = note_path.read_text(encoding="utf-8")

        # Indent transcript lines into callout
        callout_lines = []
        for line in transcript_markdown.splitlines():
            if line.strip():
                callout_lines.append(f"> {line}")
        indented_transcript = "\n".join(callout_lines)

        audio_ref = ""
        if audio_path:
            p = Path(audio_path)
            audio_ref = f"\n> **Audio File**: `file://{p.resolve()}`\n>"

        transcript_section = f"""## 🎙️ Spoken Transcript
> [!quote]- Full Audio-Synced Transcript{audio_ref}
{indented_transcript}"""

        # Replace existing transcript section or append at bottom
        if "## 🎙️ Spoken Transcript" in content:
            new_content = re.sub(
                r"## 🎙️ Spoken Transcript[\s\S]*$",
                transcript_section + "\n",
                content,
            )
        else:
            new_content = content.rstrip() + "\n\n" + transcript_section + "\n"

        note_path.write_text(new_content, encoding="utf-8")
        logger.info(f"Finalized lecture note transcript in {note_path}")
        return note_path
