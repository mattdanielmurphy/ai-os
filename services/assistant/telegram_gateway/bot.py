"""Telegram Bot Gateway managing messages, inline keyboards, and mutable message lifecycles."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

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

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = ParseMode.HTML,
    ) -> bool:
        """
        Edits a previously sent message in place with new text, handling chunking and plain-text fallback.
        If content exceeds 4000 characters, edits message_id with chunk 0 and sends remaining chunks.
        """
        if not self.config.is_telegram_ready() or not self.app:
            if message_id in self._dry_run_messages:
                self._dry_run_messages[message_id]["text"] = text
                logger.info(f"[DRY-RUN] Edited Message (id={message_id}):\n{text}")
                return True
            return False

        chunks = split_message_chunks(text, max_chars=4000)
        first_chunk = chunks[0] if chunks else ""
        formatted_first = (
            markdown_to_telegram_html(first_chunk) if parse_mode == ParseMode.HTML else first_chunk
        )

        success = False
        try:
            await self.app.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=formatted_first,
                parse_mode=parse_mode,
            )
            logger.info(f"Edited Telegram message (msg_id={message_id})")
            success = True
        except Exception as e:
            logger.warning(
                f"Failed to edit Telegram message {message_id} with HTML ({e}). Retrying plain text..."
            )
            try:
                await self.app.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=first_chunk,
                )
                logger.info(f"Edited Telegram message with plain text fallback (msg_id={message_id})")
                success = True
            except Exception as e2:
                logger.error(f"Failed to edit Telegram message {message_id}: {e2}")
                # If editing failed, send message afresh
                await self.send_message(chat_id, first_chunk, parse_mode=parse_mode)

        if len(chunks) > 1:
            for extra_chunk in chunks[1:]:
                await self.send_message(chat_id, extra_chunk, parse_mode=parse_mode)

        return success

    async def send_audio(
        self,
        chat_id: int,
        audio_path: Union[str, Path],
        caption: Optional[str] = None,
        title: Optional[str] = None,
        performer: Optional[str] = None,
    ) -> Optional[int]:
        """Sends an audio file (.mp3, .wav, .m4a, etc.) to Telegram."""
        path = Path(audio_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_audio failed: file does not exist: {path}")
            return None

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "type": "audio",
                "path": str(path),
                "caption": caption,
                "title": title,
                "performer": performer,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Audio (id={msg_id}) to chat {chat_id}: {path.name}")
            return msg_id

        caption_clean = markdown_to_telegram_html(caption) if caption else None
        try:
            with open(path, "rb") as f:
                msg = await self.app.bot.send_audio(
                    chat_id=chat_id,
                    audio=f,
                    caption=caption_clean,
                    title=title or path.stem,
                    performer=performer or "Assistor",
                    parse_mode=ParseMode.HTML if caption_clean else None,
                )
                logger.info(f"Sent audio to Telegram (msg_id={msg.message_id}, file={path.name})")
                return msg.message_id
        except Exception as e:
            logger.warning(f"Failed to send audio as HTML caption ({e}). Retrying plain caption...")
            try:
                with open(path, "rb") as f:
                    msg = await self.app.bot.send_audio(
                        chat_id=chat_id,
                        audio=f,
                        caption=caption,
                        title=title or path.stem,
                        performer=performer or "Assistor",
                    )
                    logger.info(f"Sent audio with plain caption fallback (msg_id={msg.message_id})")
                    return msg.message_id
            except Exception as e2:
                logger.warning(f"Failed to send as audio ({e2}). Retrying as document fallback...")
                return await self.send_document(chat_id, path, caption=caption)

    async def send_voice(
        self,
        chat_id: int,
        voice_path: Union[str, Path],
        caption: Optional[str] = None,
    ) -> Optional[int]:
        """Sends a voice message (.ogg or Opus) to Telegram with voice bubble UI."""
        path = Path(voice_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_voice failed: file does not exist: {path}")
            return None

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "type": "voice",
                "path": str(path),
                "caption": caption,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Voice (id={msg_id}) to chat {chat_id}: {path.name}")
            return msg_id

        caption_clean = markdown_to_telegram_html(caption) if caption else None
        try:
            with open(path, "rb") as f:
                msg = await self.app.bot.send_voice(
                    chat_id=chat_id,
                    voice=f,
                    caption=caption_clean,
                    parse_mode=ParseMode.HTML if caption_clean else None,
                )
                logger.info(f"Sent voice to Telegram (msg_id={msg.message_id}, file={path.name})")
                return msg.message_id
        except Exception as e:
            logger.warning(f"Failed to send voice bubble ({e}). Retrying via send_audio fallback...")
            return await self.send_audio(chat_id, path, caption=caption)

    async def send_photo(
        self,
        chat_id: int,
        photo_path: Union[str, Path],
        caption: Optional[str] = None,
    ) -> Optional[int]:
        """Sends an image/photo (.jpg, .png, .webp, etc.) to Telegram."""
        path = Path(photo_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_photo failed: file does not exist: {path}")
            return None

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "type": "photo",
                "path": str(path),
                "caption": caption,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Photo (id={msg_id}) to chat {chat_id}: {path.name}")
            return msg_id

        caption_clean = markdown_to_telegram_html(caption) if caption else None
        try:
            with open(path, "rb") as f:
                msg = await self.app.bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=caption_clean,
                    parse_mode=ParseMode.HTML if caption_clean else None,
                )
                logger.info(f"Sent photo to Telegram (msg_id={msg.message_id}, file={path.name})")
                return msg.message_id
        except Exception as e:
            logger.warning(f"Failed to send photo as HTML caption ({e}). Retrying plain caption...")
            try:
                with open(path, "rb") as f:
                    msg = await self.app.bot.send_photo(
                        chat_id=chat_id,
                        photo=f,
                        caption=caption,
                    )
                    logger.info(f"Sent photo with plain caption fallback (msg_id={msg.message_id})")
                    return msg.message_id
            except Exception as e2:
                logger.warning(f"Failed to send photo ({e2}). Retrying as document fallback...")
                return await self.send_document(chat_id, path, caption=caption)

    async def send_video(
        self,
        chat_id: int,
        video_path: Union[str, Path],
        caption: Optional[str] = None,
    ) -> Optional[int]:
        """Sends a video (.mp4, .mov, etc.) to Telegram."""
        path = Path(video_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_video failed: file does not exist: {path}")
            return None

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "type": "video",
                "path": str(path),
                "caption": caption,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Video (id={msg_id}) to chat {chat_id}: {path.name}")
            return msg_id

        caption_clean = markdown_to_telegram_html(caption) if caption else None
        try:
            with open(path, "rb") as f:
                msg = await self.app.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption=caption_clean,
                    parse_mode=ParseMode.HTML if caption_clean else None,
                )
                logger.info(f"Sent video to Telegram (msg_id={msg.message_id}, file={path.name})")
                return msg.message_id
        except Exception as e:
            logger.warning(f"Failed to send video ({e}). Retrying as document fallback...")
            return await self.send_document(chat_id, path, caption=caption)

    async def send_document(
        self,
        chat_id: int,
        document_path: Union[str, Path],
        caption: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Optional[int]:
        """Sends an arbitrary document/file to Telegram."""
        path = Path(document_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_document failed: file does not exist: {path}")
            return None

        if not self.config.is_telegram_ready() or not self.app:
            self._mock_message_id_seq += 1
            msg_id = self._mock_message_id_seq
            self._dry_run_messages[msg_id] = {
                "chat_id": chat_id,
                "type": "document",
                "path": str(path),
                "caption": caption,
                "filename": filename or path.name,
                "status": "SENT",
            }
            logger.info(f"[DRY-RUN] Sent Document (id={msg_id}) to chat {chat_id}: {path.name}")
            return msg_id

        caption_clean = markdown_to_telegram_html(caption) if caption else None
        try:
            with open(path, "rb") as f:
                msg = await self.app.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=filename or path.name,
                    caption=caption_clean,
                    parse_mode=ParseMode.HTML if caption_clean else None,
                )
                logger.info(f"Sent document to Telegram (msg_id={msg.message_id}, file={path.name})")
                return msg.message_id
        except Exception as e:
            logger.warning(f"Failed to send document as HTML caption ({e}). Retrying plain caption...")
            try:
                with open(path, "rb") as f:
                    msg = await self.app.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=filename or path.name,
                        caption=caption,
                    )
                    logger.info(f"Sent document with plain caption fallback (msg_id={msg.message_id})")
                    return msg.message_id
            except Exception as e2:
                logger.error(f"Failed to send document to Telegram: {e2}")
                return None

    async def send_media(
        self,
        chat_id: int,
        file_path: Union[str, Path],
        caption: Optional[str] = None,
        is_voice: bool = False,
        as_document: bool = False,
    ) -> Optional[int]:
        """
        Unified media sender: automatically classifies the file type and delivers it
        using the native Telegram method (photo, audio, voice, video, or document).
        """
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            logger.warning(f"send_media failed: file not found: {path}")
            return None

        if as_document:
            return await self.send_document(chat_id, path, caption=caption)

        ext = path.suffix.lower()
        if is_voice:
            return await self.send_voice(chat_id, path, caption=caption)

        if ext in (".mp3", ".wav", ".m4a", ".aac", ".flac", ".alac", ".aiff"):
            return await self.send_audio(chat_id, path, caption=caption)
        elif ext in (".ogg", ".opus"):
            return await self.send_voice(chat_id, path, caption=caption)
        elif ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"):
            return await self.send_photo(chat_id, path, caption=caption)
        elif ext in (".mp4", ".mov", ".mkv", ".webm", ".m4v"):
            return await self.send_video(chat_id, path, caption=caption)
        else:
            return await self.send_document(chat_id, path, caption=caption)


