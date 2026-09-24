import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import FrozenSet, Optional

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
    telegram_allowed_chat_ids: FrozenSet[int] = field(
        default_factory=lambda: frozenset(
            int(value.strip())
            for value in os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")
            if value.strip()
        )
    )
    dry_run: bool = field(
        default_factory=lambda: os.getenv("ASSISTANT_DRY_RUN", "0") in ("1", "true", "True")
    )

    # Cloud STT & Media
    groq_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GROQ_API_KEY")
    )
    media_tmp_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "ASSISTANT_MEDIA_DIR",
                os.path.expanduser("~/projects/ai-os/services/assistant/tmp/telegram_media"),
            )
        )
    )

    # Direct Codex transport. Telegram deliberately does not route through Hermes.
    codex_command: str = field(
        default_factory=lambda: os.getenv(
            "CODEX_CLI_PATH", "/Applications/ChatGPT.app/Contents/Resources/codex"
        )
    )

    # Context Gate & Silence Dynamics
    event_routine_buffer_minutes: int = 45  # Delay after class/event ends before contacting
    # Interactive check-ins remain answerable until Matt responds. A non-positive value means
    # unlimited; keep the awake-time accounting available for an explicitly configured timeout.
    silence_timeout_seconds: int = 0
    silence_cooldown_seconds: int = 120 * 60  # 2 hours backoff when Matt ignores a prompt
    sleep_gap_threshold_seconds: float = 120.0  # Delta between wall clock and monotonic indicating sleep
    poll_interval_seconds: int = 30  # Scheduler loop tick

    # FSRS Defaults
    retention_cold_storage: float = 0.90
    retention_baby_facts: float = 0.85

    # Morning Grounding & Briefing Schedule
    morning_briefing_hour: int = 8
    morning_briefing_minute: int = 0
    morning_reminder_interval_seconds: int = 15 * 60
    morning_reminder_cutoff_hour: int = 12

    @property
    def habits_definitions_dir(self) -> Path:
        return self.obsidian_vault_path / "habits" / "definitions"

    @property
    def habits_logs_dir(self) -> Path:
        return self.obsidian_vault_path / "habits" / "logs"

    def is_telegram_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id and not self.dry_run)

    @property
    def effective_telegram_allowed_chat_ids(self) -> FrozenSet[int]:
        """Configured allowlist, with the outbound chat retained as the safe default."""
        if self.telegram_allowed_chat_ids:
            return self.telegram_allowed_chat_ids
        return frozenset({self.telegram_chat_id}) if self.telegram_chat_id else frozenset()

    def is_authorized_telegram_chat(self, chat_id: Optional[int]) -> bool:
        return chat_id is not None and chat_id in self.effective_telegram_allowed_chat_ids
