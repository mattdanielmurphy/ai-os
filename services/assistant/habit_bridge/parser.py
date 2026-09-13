"""YAML Frontmatter Parser for Obsidian Habit Definitions."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger("assistant.habit_bridge.parser")


@dataclass
class HabitDefinition:
    name: str
    category: str
    frequency: str
    target_days: int
    emergency_version: str
    description: str
    file_path: Path


class HabitParser:
    def __init__(self, definitions_dir: Path):
        self.definitions_dir = definitions_dir

    def _parse_file(self, file_path: Path) -> Optional[HabitDefinition]:
        if not file_path.exists() or file_path.suffix.lower() != ".md":
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                # No YAML frontmatter
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter_raw = parts[1]
            body = parts[2].strip()
            data = yaml.safe_load(frontmatter_raw) or {}

            if data.get("type") != "habit":
                return None

            name = file_path.stem
            category = data.get("category", "General")
            frequency = data.get("frequency", "daily")
            target_days = int(data.get("target_days", 7))
            emergency_version = data.get("emergency_version", "2-Minute Version")

            return HabitDefinition(
                name=name,
                category=category,
                frequency=frequency,
                target_days=target_days,
                emergency_version=emergency_version,
                description=body,
                file_path=file_path,
            )
        except Exception as e:
            logger.error(f"Error parsing habit definition file {file_path}: {e}")
            return None

    def get_all_habits(self) -> List[HabitDefinition]:
        if not self.definitions_dir.exists():
            return []

        habits: List[HabitDefinition] = []
        for file_path in self.definitions_dir.glob("*.md"):
            h = self._parse_file(file_path)
            if h:
                habits.append(h)
        return habits

    def get_habit(self, name: str) -> Optional[HabitDefinition]:
        file_path = self.definitions_dir / f"{name}.md"
        return self._parse_file(file_path)
