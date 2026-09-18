"""Obsidian Gratitude Logging Utility."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("assistant.briefing.gratitude")


def record_gratitude(
    vault_path: Path, gratitude_text: str, timestamp: Optional[datetime] = None
) -> Path:
    """
    Records a gratitude entry into today's Obsidian habit log.
    Ensures both habits/logs/YYYY-MM-DD.md and Daily Notes (if present) are updated.
    """
    ts = timestamp or datetime.now()
    date_str = ts.strftime("%Y-%m-%d")
    time_str = ts.strftime("%H:%M")
    clean_text = gratitude_text.strip()

    # Primary target: habits/logs/YYYY-MM-DD.md per Habits Design.md
    habits_logs_dir = vault_path / "habits" / "logs"
    habits_logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = habits_logs_dir / f"{date_str}.md"

    bullet_entry = f"- [{time_str}] {clean_text}"

    if not log_file.exists():
        content = (
            f"---\n"
            f"type: daily-log\n"
            f"date: {date_str}\n"
            f"completed: []\n"
            f"---\n"
            f"# Daily Log: {date_str}\n\n"
            f"## Gratitude\n"
            f"{bullet_entry}\n"
        )
        log_file.write_text(content, encoding="utf-8")
        logger.info(f"Created daily habit log with gratitude at {log_file}")
    else:
        existing = log_file.read_text(encoding="utf-8")
        if "## Gratitude" in existing:
            # Insert bullet directly after heading
            parts = existing.split("## Gratitude", 1)
            updated = f"{parts[0]}## Gratitude\n{bullet_entry}{parts[1]}"
            log_file.write_text(updated, encoding="utf-8")
        else:
            updated = existing.rstrip() + f"\n\n## Gratitude\n{bullet_entry}\n"
            log_file.write_text(updated, encoding="utf-8")
        logger.info(f"Appended gratitude entry to existing log at {log_file}")

    # Optional secondary: Daily Notes/YYYY-MM-DD.md if directory exists
    daily_notes_dir = vault_path / "Daily Notes"
    if daily_notes_dir.exists() and daily_notes_dir.is_dir():
        dn_file = daily_notes_dir / f"{date_str}.md"
        if dn_file.exists():
            try:
                dn_content = dn_file.read_text(encoding="utf-8")
                if "## Gratitude" in dn_content:
                    parts = dn_content.split("## Gratitude", 1)
                    dn_updated = f"{parts[0]}## Gratitude\n{bullet_entry}{parts[1]}"
                    dn_file.write_text(dn_updated, encoding="utf-8")
                else:
                    dn_updated = dn_content.rstrip() + f"\n\n## Gratitude\n{bullet_entry}\n"
                    dn_file.write_text(dn_updated, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Could not update Daily Notes file {dn_file}: {e}")

    return log_file
