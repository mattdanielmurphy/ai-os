"""Telegram gateway package for the proactive assistant."""
from .bot import TelegramGateway
from .formatter import markdown_to_telegram_html, split_message_chunks
from .handlers import register_handlers
from .silence import AwakeSilenceWatchdog

__all__ = [
    "TelegramGateway",
    "register_handlers",
    "AwakeSilenceWatchdog",
    "markdown_to_telegram_html",
    "split_message_chunks",
]
