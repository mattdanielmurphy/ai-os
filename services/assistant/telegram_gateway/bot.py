"""Telegram Bot Gateway managing messages, inline keyboards, and mutable message lifecycles."""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, ContextTypes

from ..config import AssistantConfig

# Silence httpx URL requests so Telegram bot token in endpoint URL is never logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from .formatter import markdown_to_telegram_html, split_message_chunks

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

    def add_handler(self, handler) -> None:
        if self.app:
            self.app.add_handler(handler)

    def add_callback_handler(self, handler_fn: Callable) -> None:
        if self.app:
            self.app.add_handler(CallbackQueryHandler(handler_fn))

    async def send_chat_action(self, chat_id: int, action: str = "typing") -> None:
        if self.config.is_telegram_ready() and self.app:
            try:
                await self.app.bot.send_chat_action(chat_id=chat_id, action=action)
            except Exception as e:
                logger.debug(f"Failed to send chat action: {e}")

    async def send_message(
        self,
        chat_id: int,
        text: str,
        keyboard_rows: Optional[List[List[Dict[str, str]]]] = None,
        parse_mode: str = ParseMode.HTML,
    ) -> Optional[int]:
        """
        Sends a standard or interactive message to a chat, formatted as HTML by default.
        Automatically converts Markdown to Telegram HTML and handles long messages.
        """
        if keyboard_rows:
            return await self.send_prompt(chat_id, text, keyboard_rows, parse_mode=parse_mode)

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "text": text,
                "keyboard": [],
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Message (id={msg_id}) to chat {chat_id}:\n{text}")
            return msg_id

        chunks = split_message_chunks(text, max_chars=4000)
        last_msg_id: Optional[int] = None

        for chunk in chunks:
            formatted_text = (
                markdown_to_telegram_html(chunk) if parse_mode == ParseMode.HTML else chunk
            )
            try:
                message = await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=formatted_text,
                    parse_mode=parse_mode,
                )
                last_msg_id = message.message_id
                logger.info(f"Sent message to Telegram (msg_id={message.message_id})")
            except Exception as e:
                logger.warning(
                    f"Failed to send formatted Telegram message ({e}). Retrying as plain text..."
                )
                try:
                    message = await self.app.bot.send_message(
                        chat_id=chat_id,
                        text=chunk,
                    )
                    last_msg_id = message.message_id
                    logger.info(f"Sent plain text fallback to Telegram (msg_id={message.message_id})")
                except Exception as e2:
                    logger.error(f"Failed to send Telegram message: {e2}")
                    return None

        return last_msg_id

    async def send_prompt(
        self,
        chat_id: int,
        text: str,
        keyboard_rows: List[List[Dict[str, str]]],
        parse_mode: str = ParseMode.HTML,
    ) -> Optional[int]:
        """
        Sends an interactive prompt with inline buttons.
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

        formatted_text = (
            markdown_to_telegram_html(text) if parse_mode == ParseMode.HTML else text
        )

        keyboard = []
        for row in keyboard_rows:
            btn_row = [
                InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
                for btn in row
            ]
            keyboard.append(btn_row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            message = await self.app.bot.send_message(
                chat_id=chat_id,
                text=formatted_text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            logger.info(f"Sent prompt to Telegram (msg_id={message.message_id})")
            return message.message_id
        except Exception as e:
            logger.warning(f"Failed to send HTML prompt ({e}). Retrying with plain text...")
            try:
                message = await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                )
                logger.info(f"Sent plain prompt fallback to Telegram (msg_id={message.message_id})")
                return message.message_id
            except Exception as e2:
                logger.error(f"Failed to send prompt to Telegram: {e2}")
                return None

    async def edit_prompt(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        remove_keyboard: bool = True,
        keyboard_rows: Optional[List[List[Dict[str, str]]]] = None,
        parse_mode: str = ParseMode.HTML,
    ) -> bool:
        """
        Edits a previously sent message in place (e.g. progressive elaboration, transition to struggle rating, or mute).
        """
        if not self.config.is_telegram_ready() or not self.app:
            # Dry-run mode simulation
            if message_id in self._dry_run_messages:
                self._dry_run_messages[message_id]["text"] = text
                if keyboard_rows is not None:
                    self._dry_run_messages[message_id]["keyboard"] = keyboard_rows
                elif remove_keyboard:
                    self._dry_run_messages[message_id]["keyboard"] = []
                logger.info(f"[DRY-RUN] Edited Prompt (id={message_id}):\n{text}")
                return True
            return False

        formatted_text = (
            markdown_to_telegram_html(text) if parse_mode == ParseMode.HTML else text
        )

        reply_markup = None
        if keyboard_rows is not None:
            keyboard = []
            for row in keyboard_rows:
                btn_row = [
                    InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
                    for btn in row
                ]
                keyboard.append(btn_row)
            reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await self.app.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=formatted_text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            logger.info(f"Edited Telegram message (msg_id={message_id})")
            return True
        except Exception as e:
            logger.warning(
                f"Failed to edit Telegram message {message_id} with HTML ({e}). Retrying plain text..."
            )
            try:
                await self.app.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=reply_markup,
                )
                logger.info(f"Edited Telegram message with plain text fallback (msg_id={message_id})")
                return True
            except Exception as e2:
                logger.error(f"Failed to edit Telegram message {message_id}: {e2}")
                return False
