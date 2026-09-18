import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    # Load from centralized ~/.hermes/.env and project root .env
    load_dotenv(Path.home() / ".hermes" / ".env")
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    load_dotenv(Path(__file__).resolve().parent / ".env")
    load_dotenv(Path.cwd() / ".env")
except ImportError:
    pass


@dataclass
class AssistantConfig:
    # Storage and Vault Paths
    db_path: Path = field(
        default_factory=lambda: Path(
            os.getenv("ASSISTANT_DB_PATH", os.path.expanduser("~/.hermes/assistant.db"))
        )
    )
    obsidian_vault_path: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "OBSIDIAN_VAULT_PATH",
                os.path.expanduser(
                    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
                ),
            )
        )
    )

    # Telegram Credentials
    telegram_bot_token: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN")
    )
    telegram_chat_id: Optional[int] = field(
        default_factory=lambda: int(os.getenv("TELEGRAM_CHAT_ID"))
        if os.getenv("TELEGRAM_CHAT_ID")
        else None
    )
    dry_run: bool = field(
        default_factory=lambda: os.getenv("ASSISTANT_DRY_RUN", "0") in ("1", "true", "True")
    )

    # Context Gate & Silence Dynamics
    event_routine_buffer_minutes: int = 45  # Delay after class/event ends before contacting
    silence_timeout_seconds: int = 45 * 60  # 45 minutes of awake time before mutes
    silence_cooldown_seconds: int = 120 * 60  # 2 hours backoff when Matt ignores a prompt
    sleep_gap_threshold_seconds: float = 120.0  # Delta between wall clock and monotonic indicating sleep
    poll_interval_seconds: int = 30  # Scheduler loop tick

    # FSRS Defaults
    retention_cold_storage: float = 0.90
    retention_baby_facts: float = 0.85

    # Morning Grounding & Briefing Schedule
    morning_briefing_hour: int = 8
    morning_briefing_minute: int = 0

    @property
    def habits_definitions_dir(self) -> Path:
        return self.obsidian_vault_path / "habits" / "definitions"

    @property
    def habits_logs_dir(self) -> Path:
        return self.obsidian_vault_path / "habits" / "logs"

    def is_telegram_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id and not self.dry_run)
