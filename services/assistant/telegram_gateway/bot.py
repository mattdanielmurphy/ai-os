"""Telegram Bot Gateway managing messages, inline keyboards, and mutable message lifecycles."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, ContextTypes

from ..config import AssistantConfig

logger = logging.getLogger("assistant.telegram_gateway.bot")


class TelegramGateway:
    def __init__(self, config: AssistantConfig):
        self.config = config
        self.app: Optional[Application] = None
        self._mock_message_id_seq = 1000
        self._dry_run_messages: Dict[int, Dict[str, Any]] = {}
        self._is_running = False

    async def initialize(self) -> None:
        if self.config.is_telegram_ready():
            try:
                self.app = ApplicationBuilder().token(self.config.telegram_bot_token).build()
                await self.app.initialize()
                logger.info("Telegram Gateway initialized with live bot token.")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram application: {e}")
                self.app = None
        else:
            logger.info("Telegram Gateway running in DRY-RUN mode (credentials not configured).")

    async def start(self) -> None:
        if self.app:
            await self.app.start()
            await self.app.updater.start_polling()
            self._is_running = True
            logger.info("Telegram Bot polling started.")

    async def stop(self) -> None:
        if self.app and self._is_running:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            self._is_running = False
            logger.info("Telegram Bot polling stopped.")

    def add_callback_handler(self, handler_fn: Callable) -> None:
        if self.app:
            self.app.add_handler(CallbackQueryHandler(handler_fn))

    async def send_prompt(
        self,
        chat_id: int,
        text: str,
        keyboard_rows: List[List[Dict[str, str]]],
        parse_mode: str = ParseMode.MARKDOWN,
    ) -> Optional[int]:
        """
        Sends an interactive prompt with inline buttons.
        Returns:
            message_id (int) or None on failure.
        """
        if not self.config.is_telegram_ready() or not self.app:
            # Dry-run mode simulation
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "text": text,
                "keyboard": keyboard_rows,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Prompt (id={msg_id}) to chat {chat_id}:\n{text}")
            return msg_id

        try:
            keyboard = []
            for row in keyboard_rows:
                btn_row = [
                    InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
                    for btn in row
                ]
                keyboard.append(btn_row)

            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            logger.info(f"Sent prompt to Telegram (msg_id={message.message_id})")
            return message.message_id
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return None

    async def edit_prompt(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        remove_keyboard: bool = True,
        parse_mode: str = ParseMode.MARKDOWN,
    ) -> bool:
        """
        Edits a previously sent message in place (e.g. progressive elaboration or mute on timeout).
        """
        if not self.config.is_telegram_ready() or not self.app:
            # Dry-run mode simulation
            if message_id in self._dry_run_messages:
                self._dry_run_messages[message_id]["text"] = text
                if remove_keyboard:
                    self._dry_run_messages[message_id]["keyboard"] = []
                logger.info(f"[DRY-RUN] Edited Prompt (id={message_id}):\n{text}")
                return True
            return False

        try:
            reply_markup = None if remove_keyboard else None
            await self.app.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            logger.info(f"Edited Telegram message (msg_id={message_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to edit Telegram message {message_id}: {e}")
            return False
