"""Telegram gateway package for the proactive assistant."""
from .bot import TelegramGateway
from .handlers import register_handlers
from .silence import AwakeSilenceWatchdog

__all__ = ["TelegramGateway", "register_handlers", "AwakeSilenceWatchdog"]
