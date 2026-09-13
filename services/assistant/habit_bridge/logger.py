"""Appends habit completions to Obsidian Daily Logs adhering to Habits Design.md."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from .parser import HabitDefinition

logger = logging.getLogger("assistant.habit_bridge.logger")


class HabitLogger:
    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir

    def log_completion(
        self, habit_name: str, variant: str = "full", timestamp: Optional[datetime] = None
    ) -> Path:
        """
        Logs habit completion to vault/habits/logs/YYYY-MM-DD.md.
        Updates both the YAML frontmatter 'completed' list and appends a markdown task.
        """
        now = timestamp or datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        log_file = self.logs_dir / f"{date_str}.md"

        self.logs_dir.mkdir(parents=True, exist_ok=True)

        wikilink = f"[[{habit_name}]]"
        entry_line = f"- [x] [[habits/definitions/{habit_name}|{habit_name}]] ({variant}) @ {time_str}"

        if not log_file.exists():
            # Create fresh daily log file
            initial_content = (
                f"---\n"
                f"type: daily-log\n"
                f"date: {date_str}\n"
                f"completed:\n"
                f"  - \"{wikilink}\"\n"
                f"notes: \"\"\n"
                f"---\n"
                f"# Daily Log: {date_str}\n\n"
                f"{entry_line}\n"
            )
            log_file.write_text(initial_content, encoding="utf-8")
            logger.info(f"Created new daily habit log: {log_file}")
            return log_file

        # Update existing log
        content = log_file.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_raw = parts[1]
                body = parts[2]
                try:
                    data = yaml.safe_load(frontmatter_raw) or {}
                    completed_list = data.get("completed", [])
                    if not isinstance(completed_list, list):
                        completed_list = []

                    # Add wikilink if not present
                    if wikilink not in completed_list and f"[[{habit_name}]]" not in completed_list:
                        completed_list.append(wikilink)
                        data["completed"] = completed_list

                    new_frontmatter = yaml.safe_dump(data, sort_keys=False).strip()
                    # Append entry line to body if not already present
                    if entry_line not in body:
                        new_body = body.rstrip() + f"\n{entry_line}\n"
                    else:
                        new_body = body

                    updated_content = f"---\n{new_frontmatter}\n---{new_body}"
                    log_file.write_text(updated_content, encoding="utf-8")
                    logger.info(f"Updated daily habit log with completion: {log_file}")
                    return log_file
                except Exception as e:
                    logger.error(f"Error updating YAML frontmatter in {log_file}: {e}")

        # Fallback: append line directly to end of file
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"\n{entry_line}\n")
        return log_file


def format_habit_prompt(habit: HabitDefinition) -> Tuple[str, List[List[Dict[str, str]]]]:
    """Formats Telegram prompt for a habit check-in."""
    text = (
        f"🌱 *Daily Habit Check-in* · _{habit.category}_\n\n"
        f"*{habit.name}*\n"
        f"⚡️ _Emergency fallback:_ {habit.emergency_version}\n\n"
        f"Tap an option below:"
    )

    name = habit.name
    keyboard = [
        [
            {"text": "🌟 Full Session", "callback_data": f"habit:{name}:full"},
            {"text": "⚡️ 2-Min Emergency", "callback_data": f"habit:{name}:emergency"},
        ],
        [
            {"text": "⏭ Skip Today", "callback_data": f"habit:{name}:skip"},
        ],
    ]
    return text, keyboard


def format_habit_completed(habit_name: str, variant: str, time_str: str) -> str:
    """Formats in-place confirmation message for habit completion."""
    if variant == "skip":
        return f"⏭ *Habit Skipped:* **{habit_name}** noted for today. Zero streak penalties."

    variant_label = "🌟 Full Session" if variant == "full" else "⚡️ 2-Min Emergency"
    return (
        f"✅ *Habit Completed!* ({variant_label})\n\n"
        f"**{habit_name}** logged at `{time_str}` in your Obsidian Daily Log."
    )
