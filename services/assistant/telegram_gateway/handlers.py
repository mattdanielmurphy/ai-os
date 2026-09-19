"""Telegram handlers for callbacks, text messages, executive commands, and quick capture."""

import asyncio
import html
import json
import logging
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ..config import AssistantConfig
from ..briefing.engine import MorningBriefingBuilder
from ..briefing.gratitude import record_gratitude
from ..context_gate.calendar import CalendarProbe
from ..habit_bridge.logger import HabitLogger, format_habit_completed
from ..habit_bridge.parser import HabitParser
from ..spaced_repetition.cards import (
    format_feedback_prompt,
    format_review_completed,
    format_review_prompt,
)
from ..spaced_repetition.engine import FSRSEngine
from ..storage.db import AssistantDB
from .bot import TelegramGateway
from .stt import transcribe_audio_file, extract_audio_from_video

logger = logging.getLogger("assistant.telegram_gateway.handlers")

# ---------------------------------------------------------------------------
# Telegram Native Media Delivery Constants & Extraction Utilities
# ---------------------------------------------------------------------------
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".alac", ".aiff", ".ogg", ".opus", ".oga"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".svg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
DOCUMENT_EXTENSIONS = {
    ".pdf", ".zip", ".tar", ".gz", ".csv", ".tsv", ".txt", ".md",
    ".json", ".yaml", ".yml", ".py", ".sh", ".html", ".docx", ".xlsx", ".pptx", ".epub",
}
ALL_MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | DOCUMENT_EXTENSIONS

MEDIA_TAG_RE = re.compile(
    r"[`\"'*_]{0,3}MEDIA:\s*([^\s`\"'*]+)[`\"'*_]{0,3}",
    re.IGNORECASE,
)


def extract_media_from_text(raw_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts MEDIA:<path> tags and platform directives ([[audio_as_voice]], [[as_document]])
    from the raw model response. Returns cleaned user-facing text and a list of media dicts.
    """
    if not raw_text:
        return "", []

    has_voice_directive = "[[audio_as_voice]]" in raw_text
    as_document_directive = "[[as_document]]" in raw_text

    media_items: List[Dict[str, Any]] = []
    seen_paths = set()

    for match in MEDIA_TAG_RE.finditer(raw_text):
        raw_path_str = match.group(1).strip()
        try:
            expanded = Path(os.path.expanduser(raw_path_str)).resolve()
            if expanded.exists() and expanded.is_file():
                if expanded not in seen_paths:
                    seen_paths.add(expanded)
                    ext = expanded.suffix.lower()
                    is_voice = has_voice_directive and (ext in AUDIO_EXTENSIONS)
                    media_items.append({
                        "path": expanded,
                        "is_voice": is_voice,
                        "as_document": as_document_directive,
                    })
            else:
                logger.warning(f"MEDIA tag referenced nonexistent path: {raw_path_str}")
        except Exception as e:
            logger.debug(f"Failed to resolve MEDIA path '{raw_path_str}': {e}")

    # Clean directives and MEDIA: tags from the text
    cleaned = raw_text.replace("[[audio_as_voice]]", "").replace("[[as_document]]", "")
    cleaned = MEDIA_TAG_RE.sub("", cleaned)
    # Strip multiple consecutive blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    return cleaned, media_items


def find_session_generated_media(session_id: str) -> List[Dict[str, Any]]:
    """
    Inspects ~/.hermes/state.db for tool results in the specified session that
    produced media or audio files (e.g. text_to_speech, image_generate, or code runs).
    """
    if not session_id:
        return []

    state_db_path = Path.home() / ".hermes" / "state.db"
    if not state_db_path.exists():
        return []

    import json
    import sqlite3

    media_items: List[Dict[str, Any]] = []
    seen_paths = set()

    try:
        conn = sqlite3.connect(f"file:{state_db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM messages WHERE session_id = ? AND role = 'tool'",
            (session_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        for (content,) in rows:
            if not content:
                continue
            try:
                data = json.loads(content)
                if not isinstance(data, dict):
                    continue

                # 1. Check media_tag string (e.g. "[[audio_as_voice]]\nMEDIA:/path/...")
                media_tag = data.get("media_tag")
                if media_tag and isinstance(media_tag, str):
                    _, tag_items = extract_media_from_text(media_tag)
                    for item in tag_items:
                        p = item["path"]
                        if p not in seen_paths:
                            seen_paths.add(p)
                            media_items.append(item)

                # 2. Check file_path
                file_path = data.get("file_path")
                if file_path and isinstance(file_path, str):
                    p = Path(os.path.expanduser(file_path)).resolve()
                    if p.exists() and p.is_file() and p not in seen_paths:
                        seen_paths.add(p)
                        is_voice = bool(data.get("voice_compatible", False))
                        media_items.append({
                            "path": p,
                            "is_voice": is_voice,
                            "as_document": False,
                        })

                # 3. Check file_paths list
                file_paths = data.get("file_paths")
                if isinstance(file_paths, list):
                    for fp in file_paths:
                        if isinstance(fp, str):
                            p = Path(os.path.expanduser(fp)).resolve()
                            if p.exists() and p.is_file() and p not in seen_paths:
                                seen_paths.add(p)
                                media_items.append({
                                    "path": p,
                                    "is_voice": False,
                                    "as_document": False,
                                })
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"find_session_generated_media failed: {e}")

    return media_items


def find_deliverable_paths_in_text(text: str) -> List[Path]:
    """
    Fallback scanner: finds absolute local paths or markdown file links in text
    referencing deliverable media files that actually exist on disk and were recently touched.
    """
    if not text:
        return []

    found: List[Path] = []
    seen = set()
    path_pattern = re.compile(
        r"(?:file://)?((?:/[a-zA-Z0-9_\.\-]+)+|(?:~/[a-zA-Z0-9_\.\-]+)+)"
    )

    now = time.time()
    for match in path_pattern.finditer(text):
        raw_p = match.group(1).strip()
        try:
            p = Path(os.path.expanduser(raw_p)).resolve()
            if p.suffix.lower() in ALL_MEDIA_EXTENSIONS and p.exists() and p.is_file():
                mtime = p.stat().st_mtime
                if (now - mtime) < 1800 and p not in seen:
                    seen.add(p)
                    found.append(p)
        except Exception:
            pass

    return found


def clean_hermes_output(raw_output: str) -> Optional[str]:
    """Cleans terminal warnings, reasoning blocks, thread metrics, and session IDs from hermes chat output."""
    if not raw_output:
        return None
    lines = raw_output.splitlines()
    cleaned = []
    in_box = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Warning:") or stripped.startswith("session_id:"):
            continue
        if stripped.startswith("┌─ Reasoning") or stripped.startswith("┌─"):
            in_box = True
            continue
        if in_box:
            if stripped.endswith("┘") or stripped.startswith("└─"):
                in_box = False
            continue
        if stripped.startswith("**Thread Metrics:**"):
            continue
        cleaned.append(line)
    result = "\n".join(cleaned).strip()
    return result if result else None


def clean_agy_output(raw_output: str) -> Optional[str]:
    """Cleans thread.md artifacts, tool notifications, and divider lines from agy CLI output."""
    if not raw_output:
        return None
    lines = raw_output.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if re.search(r"\[thread\.md\]\(file://.*?\)", stripped):
            continue
        if stripped in ("***", "---", "___"):
            continue
        if stripped.lower().startswith("conversation artifact:"):
            continue
        cleaned.append(line)
    result = "\n".join(cleaned).strip()
    return result if result else None


def build_conversational_prompt(prompt: str, history: List[Dict[str, Any]]) -> str:
    """
    Constructs a contextual prompt including prior conversation turns,
    ensuring that references like 'Send that markdown again' or 'What about X?'
    have full context even across session restarts or long pauses.
    Enforces Telegram presentation rules (vertical cards, no tables) and native attachment delivery.
    """
    presentation_rule = (
        "[Formatting & Delivery Rules: You are chatting with Matt on mobile Telegram.\n"
        "1. Structure & Layout: Default all structured data to clean vertical cards/blocks with bold labels (e.g. • <b>Label:</b> Value) and bullet points. NEVER generate ASCII or Markdown tables.\n"
        "2. Native Attachments: You have full native Telegram file delivery capabilities! Whenever you generate, convert, locate, or refer to an audio recording, voice note, photo, image, video, PDF, document, or code export for Matt, attach it by outputting MEDIA:/absolute/path/to/file on its own line (e.g. MEDIA:/path/to/audio.mp3). Use [[audio_as_voice]] on the preceding line for voice bubble playback. The Telegram gateway will automatically extract the file, upload it as a native attachment, and deliver it directly to Matt in this chat.]\n\n"
    )

    if not history:
        return f"{presentation_rule}{prompt}"

    history_lines = []
    for msg in history:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "").strip()
        if len(content) > 2000:
            content = content[:2000] + "... [truncated for length]"
        history_lines.append(f"{role}: {content}")

    history_block = "\n\n".join(history_lines)
    return (
        f"{presentation_rule}"
        f"[Prior Conversation Context]\n"
        f"{history_block}\n"
        f"[End Prior Context]\n\n"
        f"User's Latest Message: {prompt}\n\n"
        f"Please respond directly to the user's latest message above, maintaining continuous context from the prior conversation history."
    )


class ActionDispatcher:
    def __init__(
        self,
        db: AssistantDB,
        fsrs_engine: FSRSEngine,
        habit_logger: HabitLogger,
        gateway: TelegramGateway,
        config: Optional[AssistantConfig] = None,
        habit_parser: Optional[HabitParser] = None,
        calendar_probe: Optional[CalendarProbe] = None,
    ):
        self.db = db
        self.fsrs_engine = fsrs_engine
        self.habit_logger = habit_logger
        self.gateway = gateway
        self.config = config or AssistantConfig()
        self.habit_parser = habit_parser
        self.calendar_probe = calendar_probe

    async def handle_callback_str(
        self, callback_data: str, chat_id: int, message_id: int
    ) -> bool:
        """
        Dispatches callback data directly (used both by Telegram event handlers and test harnesses).
        """
        parts = callback_data.split(":")
        action_type = parts[0]

        if action_type in ("fsrs", "fsrs_rate") and len(parts) >= 3:
            card_id = parts[1]
            rating_val = int(parts[2])
            return await self._handle_fsrs(card_id, rating_val, chat_id, message_id)

        elif action_type == "fsrs_pick" and len(parts) >= 3:
            card_id = parts[1]
            chosen_idx = int(parts[2])
            return await self._handle_fsrs_pick(card_id, chosen_idx, chat_id, message_id)

        elif action_type == "habit" and len(parts) >= 3:
            habit_name = parts[1]
            variant = parts[2]
            return await self._handle_habit(habit_name, variant, chat_id, message_id)

        elif action_type == "briefing" and len(parts) >= 2:
            sub = parts[1]
            if sub == "gratitude":
                await self.gateway.send_message(
                    chat_id,
                    "🙏 *Daily Gratitude Reflection*\n\n"
                    "What is one small, specific thing you appreciate having in your day?\n\n"
                    "Reply directly to this message, or type `/gratitude <thought>` to record it in your journal.",
                )
                return True
            elif sub == "meditate_done":
                await self.gateway.edit_prompt(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="🧘 *Morning Centering Complete*\n\n"
                    "Breath is grounded, posture is aligned, and awareness is reset. Wishing you a calm, focused day, Matt.",
                    remove_keyboard=True,
                )
                await self.db.resolve_signal(message_id, "RESPONDED")
                return True
            elif sub == "review":
                await self.cmd_quiz(chat_id)
                return True

        elif action_type == "cmd" and len(parts) >= 2:
            cmd_name = parts[1]
            if cmd_name == "quiz":
                return await self.cmd_quiz(chat_id)
            elif cmd_name == "habits":
                return await self.cmd_habits(chat_id)
            elif cmd_name == "status":
                return await self.cmd_status(chat_id)
            elif cmd_name == "morning":
                return await self.cmd_morning(chat_id)
            elif cmd_name == "engine":
                return await self.cmd_engine("", chat_id)

        elif action_type == "engine" and len(parts) >= 2:
            eng = parts[1]
            if eng == "agy":
                self.active_engine = "agy"
                await self.gateway.edit_prompt(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="⚡️ <b>Engine set to Agy (Gemini 3.8 Flash Low)</b>\n\nUsing free Antigravity quota.",
                    remove_keyboard=True,
                )
                return True
            elif eng == "codex":
                self.active_engine = "codex"
                await self.gateway.edit_prompt(
                    chat_id=chat_id,
                    message_id=message_id,
                    text="🧠 <b>Engine set to OpenAI Codex</b>\n\nUsing your Codex subscription.",
                    remove_keyboard=True,
                )
                return True

        logger.warning(f"Unknown callback query format: {callback_data}")
        return False

    async def _handle_fsrs_pick(
        self, card_id: str, chosen_idx: int, chat_id: int, message_id: int
    ) -> bool:
        card = await self.db.get_card(card_id)
        if not card:
            logger.warning(f"FSRS pick received for unknown card {card_id}")
            return False

        feedback_text, struggle_keyboard = format_feedback_prompt(card, chosen_idx)
        await self.gateway.edit_prompt(
            chat_id=chat_id,
            message_id=message_id,
            text=feedback_text,
            remove_keyboard=False,
            keyboard_rows=struggle_keyboard,
        )
        return True

    async def _handle_fsrs(
        self, card_id: str, rating_val: int, chat_id: int, message_id: int
    ) -> bool:
        card = await self.db.get_card(card_id)
        if not card:
            logger.warning(f"FSRS callback received for unknown card {card_id} (test card)")
            await self.gateway.edit_prompt(
                chat_id=chat_id,
                message_id=message_id,
                text=f"✅ *Test Recall Rating Recorded!*\n\nRating value `{rating_val}` received. Telegram button handler is fully connected.",
                remove_keyboard=True,
            )
            return True

        now = datetime.now(timezone.utc)
        updated_card, log_dict = self.fsrs_engine.review(card, rating_val, now)

        # Update card and log review
        await self.db.add_or_update_card(
            card_id=updated_card["card_id"],
            deck_type=updated_card["deck_type"],
            prompt=updated_card["prompt"],
            answer=updated_card["answer"],
            elaboration=updated_card["elaboration"],
            stability=updated_card["stability"],
            difficulty=updated_card["difficulty"],
            reps=updated_card["reps"],
            lapses=updated_card["lapses"],
            state=updated_card["state"],
            due_at=updated_card["due_at"],
            last_review=updated_card["last_review"],
        )
        await self.db.log_fsrs_review(
            log_id=log_dict["log_id"],
            card_id=log_dict["card_id"],
            rating=log_dict["rating"],
            review_time=log_dict["review_time"],
            scheduled_days=log_dict["scheduled_days"],
        )

        # Edit Telegram message in place
        completed_text = format_review_completed(card, rating_val, updated_card["due_at"])
        await self.gateway.edit_prompt(
            chat_id=chat_id, message_id=message_id, text=completed_text, remove_keyboard=True
        )

        # Mark outbound signal as responded
        await self.db.resolve_signal(message_id, "RESPONDED")
        logger.info(f"FSRS card {card_id} reviewed successfully with rating {rating_val}")
        return True

    async def _handle_habit(
        self, habit_name: str, variant: str, chat_id: int, message_id: int
    ) -> bool:
        now = datetime.now()
        time_str = now.strftime("%H:%M")

        if variant in ("full", "emergency"):
            self.habit_logger.log_completion(habit_name, variant=variant, timestamp=now)
            logger.info(f"Logged habit completion: {habit_name} ({variant})")

        completed_text = format_habit_completed(habit_name, variant, time_str)
        await self.gateway.edit_prompt(
            chat_id=chat_id, message_id=message_id, text=completed_text, remove_keyboard=True
        )

        await self.db.resolve_signal(message_id, "RESPONDED")
        return True

    # -------------------------------------------------------------------------
    # Executive Commands
    # -------------------------------------------------------------------------
    async def cmd_help(self, chat_id: int) -> bool:
        help_text = (
            "👋 *AI-OS Executive Assistant*\n\n"
            "I manage your morning briefings, spaced repetition reviews, habit tracking, and proactive check-ins.\n\n"
            "*Available Commands:*\n"
            "• `/morning` — Trigger your daily morning grounding and briefing\n"
            "• `/gratitude <thought>` — Log a gratitude entry directly into your vault\n"
            "• `/quiz` or `/review` — Start an immediate spaced repetition quiz\n"
            "• `/status` — View active triggers, due cards, and gate status\n"
            "• `/habits` — View today's habit check-ins\n"
            "• `/reset` or `/clear` — Reset conversation context and memory\n"
            "• `/note <text>` — Quick capture note directly to Obsidian Inbox\n"
            "• `/remind <text>` — Add timed reminder to Apple Reminders\n\n"
            "_Tip: You can reply directly to quizzes with A, B, C, D in text, or ask me any question!_"
        )
        keyboard = [
            [
                {"text": "🌅 Morning Briefing", "callback_data": "cmd:morning"},
                {"text": "📚 Quiz Me", "callback_data": "cmd:quiz"},
            ],
            [
                {"text": "📊 Status", "callback_data": "cmd:status"},
            ]
        ]
        await self.gateway.send_message(chat_id, help_text, keyboard_rows=keyboard)
        return True

    async def cmd_morning(self, chat_id: int) -> bool:
        now_utc = datetime.now(timezone.utc)
        due_cards = await self.db.get_due_cards(now_utc)
        events = []
        if self.calendar_probe:
            try:
                events = self.calendar_probe.fetch_events()
            except Exception as e:
                logger.warning(f"Error fetching calendar events for morning briefing: {e}")
        builder = MorningBriefingBuilder()
        text, keyboard = builder.build_prompt(
            due_cards_count=len(due_cards),
            calendar_events=events,
        )
        msg_id = await self.gateway.send_prompt(chat_id, text, keyboard)
        if msg_id:
            timeout_at = now_utc + timedelta(seconds=self.config.silence_timeout_seconds)
            await self.db.record_outbound_signal(
                message_id=msg_id,
                chat_id=chat_id,
                trigger_id="trig_morning_manual",
                sent_at=now_utc,
                timeout_at=timeout_at,
                status="AWAITING_INPUT",
            )
        return True

    async def cmd_gratitude(self, text: str, chat_id: int) -> bool:
        clean_text = text.strip()
        if not clean_text:
            await self.gateway.send_message(
                chat_id, "Usage: `/gratitude <what you are thankful for>`"
            )
            return False

        log_path = record_gratitude(self.config.obsidian_vault_path, clean_text)
        reply = (
            f"🙏 *Gratitude Logged!*\n\n"
            f"_{clean_text}_\n\n"
            f"Recorded to `{log_path.name}` in your Obsidian vault."
        )
        await self.gateway.send_message(chat_id, reply)
        return True

    async def cmd_status(self, chat_id: int) -> bool:
        now = datetime.now(timezone.utc)
        due_cards = await self.db.get_due_cards(now)
        pending = await self.db.get_pending_triggers(now)
        signals = await self.db.get_awaiting_signals()

        today_str = datetime.now().strftime("%Y-%m-%d")
        today_log_path = self.config.habits_logs_dir / f"{today_str}.md"
        completed_count = 0
        if today_log_path.exists():
            try:
                content = today_log_path.read_text(encoding="utf-8")
                completed_count = len([l for l in content.splitlines() if l.strip().startswith("- [x]")])
            except Exception:
                pass

        status_text = (
            "📊 *Executive Assistant Status*\n\n"
            f"• *Due FSRS Cards*: `{len(due_cards)}`\n"
            f"• *Pending Queue*: `{len(pending)} item(s)`\n"
            f"• *Active Prompts*: `{len(signals)}`\n"
            f"• *Habits Completed Today*: `{completed_count}`\n"
        )
        if pending:
            p0 = pending[0]
            status_text += f"\n_Next in Queue:_ `{p0['trigger_type']}` (`{p0['target_id']}`)"

        keyboard = [
            [
                {"text": "📚 Quiz Now", "callback_data": "cmd:quiz"},
                {"text": "📋 Check Habits", "callback_data": "cmd:habits"},
            ]
        ]
        await self.gateway.send_message(chat_id, status_text, keyboard_rows=keyboard)
        return True

    async def cmd_quiz(self, chat_id: int) -> bool:
        now = datetime.now(timezone.utc)
        due_cards = await self.db.get_due_cards(now)
        card = due_cards[0] if due_cards else await self.db.get_any_card()

        if not card:
            await self.gateway.send_message(
                chat_id,
                "ℹ️ *No flashcards in your deck yet.*\n\nUse the assistant CLI to add review cards:\n`python3 services/assistant/cli.py add-card --prompt ... --answer ...`",
            )
            return False

        text, keyboard = format_review_prompt(card)
        msg_id = await self.gateway.send_prompt(chat_id, text, keyboard)
        if msg_id:
            trigger_id = f"trig_fsrs_{card['card_id']}"
            await self.db.record_outbound_signal(
                message_id=msg_id,
                chat_id=chat_id,
                trigger_id=trigger_id,
                sent_at=now,
                timeout_at=now + timedelta(seconds=self.config.silence_timeout_seconds),
            )
            logger.info(f"Dispatched interactive quiz card '{card['card_id']}' as msg {msg_id}")
            return True
        return False

    async def cmd_habits(self, chat_id: int) -> bool:
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_log_path = self.config.habits_logs_dir / f"{today_str}.md"
        completed_habits = set()
        if today_log_path.exists():
            try:
                content = today_log_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    if line.strip().startswith("- [x]"):
                        for part in line.split("[["):
                            if "|" in part:
                                h_name = part.split("|")[1].split("]]")[0]
                                completed_habits.add(h_name)
            except Exception:
                pass

        all_habits = self.habit_parser.get_all_habits() if self.habit_parser else []
        if not all_habits:
            await self.gateway.send_message(
                chat_id,
                f"📋 *Habit Status ({today_str})*\n\nNo habit definitions found in `habits/definitions/`.",
            )
            return True

        keyboard = []
        msg_lines = [f"📋 *Habits for Today ({today_str})*\n"]
        for h in all_habits:
            is_done = h.name in completed_habits
            icon = "✅" if is_done else "⏳"
            msg_lines.append(f"{icon} *{h.name}* (`{h.frequency}`)")
            if not is_done:
                keyboard.append([
                    {"text": f"✅ {h.name} (Full)", "callback_data": f"habit:{h.name}:full"},
                    {"text": f"⚡️ 2-Min Emergency", "callback_data": f"habit:{h.name}:emergency"},
                ])

        text = "\n".join(msg_lines)
        if keyboard:
            await self.gateway.send_prompt(chat_id, text, keyboard)
        else:
            await self.gateway.send_message(chat_id, text + "\n\n🎉 *All habits completed for today!*")
        return True

    async def cmd_capture(self, text: str, chat_id: int) -> bool:
        if not text:
            await self.gateway.send_message(chat_id, "Usage: `/note <text>` or `/capture <text>`")
            return False

        try:
            inbox_dir = self.config.obsidian_vault_path / "Inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            capture_file = inbox_dir / "Quick Capture.md"

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            line = f"- [ ] {text} *(Captured via Telegram at {now_str})*\n"

            if not capture_file.exists():
                capture_file.write_text(f"# Quick Capture Inbox\n\n{line}", encoding="utf-8")
            else:
                with open(capture_file, "a", encoding="utf-8") as f:
                    f.write(line)

            await self.gateway.send_message(
                chat_id,
                f"📥 *Captured to Obsidian Inbox*\n\n> {text}\n\n_Location: `Inbox/Quick Capture.md`_",
            )
            logger.info(f"Captured note to Obsidian: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to capture note to Obsidian: {e}")
            await self.gateway.send_message(chat_id, f"❌ Failed to save note: {e}")
            return False

    async def cmd_remind(self, title: str, chat_id: int) -> bool:
        if not title:
            await self.gateway.send_message(chat_id, "Usage: `/remind <task title>`")
            return False

        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            res = subprocess.run(
                [
                    "apple-reminders",
                    "add",
                    "--title",
                    title,
                    "--notes",
                    f"Captured via AI-OS Assistant on {now_str}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                await self.gateway.send_message(
                    chat_id,
                    f"⏰ *Added to Apple Reminders*\n\n> {title}",
                )
                logger.info(f"Added Apple Reminder: {title}")
                return True
            else:
                logger.warning(f"apple-reminders command failed: {res.stderr}")
        except Exception as e:
            logger.error(f"Error executing apple-reminders: {e}")

        # Fallback to Obsidian inbox if apple-reminders fails
        return await self.cmd_capture(f"Reminder: {title}", chat_id)

    async def cmd_reset(self, chat_id: int) -> bool:
        await self.db.clear_chat_history(chat_id)
        engine = getattr(self, "active_engine", self.config.default_engine)
        engine_label = "Agy (Gemini 3.8 Flash Low - Free)" if engine == "agy" else "OpenAI Codex"
        await self.gateway.send_message(
            chat_id,
            f"🧹 *Conversation Context Cleared*\n\nStarted a fresh conversation session with {engine_label}.",
        )
        return True

    async def cmd_engine(self, engine_choice: str, chat_id: int) -> bool:
        """Inspects or switches the active AI engine between free Agy (3.8 Flash Low) and Codex."""
        choice = engine_choice.strip().lower()
        if choice in ("agy", "free", "gemini", "flash", "flash-low", "flash_low"):
            self.active_engine = "agy"
            await self.gateway.send_message(
                chat_id,
                "⚡️ <b>Engine Switched to Agy (Gemini 3.8 Flash Low)</b>\n\nAll queries and visual inspections will use free Antigravity quota.",
            )
            return True
        elif choice in ("codex", "openai"):
            self.active_engine = "codex"
            await self.gateway.send_message(
                chat_id,
                "🧠 <b>Engine Switched to OpenAI Codex</b>\n\nAll queries and visual inspections will route to your Codex subscription.",
            )
            return True

        current = getattr(self, "active_engine", self.config.default_engine)
        curr_label = "⚡️ Agy (Gemini 3.8 Flash Low - Free)" if current == "agy" else "🧠 OpenAI Codex (Subscription)"
        keyboard = [
            [
                {"text": "⚡️ Use Free Agy (3.8 Flash Low)", "callback_data": "engine:agy"},
                {"text": "🧠 Use Codex Subscription", "callback_data": "engine:codex"},
            ]
        ]
        text = (
            f"⚙️ <b>AI Engine Routing</b>\n\n"
            f"Current active engine: <b>{curr_label}</b>\n\n"
            f"Select which engine to route conversational queries and visual inspections to:"
        )
        await self.gateway.send_prompt(chat_id, text, keyboard)
        return True

    async def _query_agy(
        self,
        prompt: str,
        image_path: Optional[Path] = None,
        chat_id: Optional[int] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """Queries agy CLI non-interactively using free Antigravity quota with gemini-3.8-flash-low."""
        try:
            full_prompt = prompt
            if image_path and image_path.exists():
                full_prompt = (
                    f"Please view and inspect the local image file at `{image_path.resolve()}` "
                    f"using your file reading tools, and respond to the following:\n\n{prompt}"
                )

            target_model = model or getattr(self.config, "agy_model", "gemini-3.8-flash-low")
            cmd = [
                "agy",
                "-p", full_prompt,
                "--model", target_model,
                "--dangerously-skip-permissions",
                "--print-timeout", "120s",
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.config.media_tmp_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=130.0)
                output = stdout.decode("utf-8", errors="replace").strip()
                res = clean_agy_output(output)
                if not res:
                    logger.warning(f"Agy returned empty or unparseable output. Raw: {output[:300]}")
                return res
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning("Agy query timed out after 130s")
                return None
        except Exception as e:
            logger.error(f"Error querying agy: {e}")
            return None

    async def _query_codex(
        self,
        prompt: str,
        image_path: Optional[Path] = None,
        chat_id: Optional[int] = None,
    ) -> Optional[str]:
        """Queries OpenAI Codex via hermes chat CLI using user's Codex subscription."""
        try:
            cmd = [
                "hermes",
                "chat",
                "-q", prompt,
                "-Q",
                "--provider", "openai-codex",
                "--source", "tool",
                "--ignore-rules",
                "--reasoning", "none",
            ]
            if image_path and image_path.exists():
                cmd.extend(["--image", str(image_path)])

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=180.0)
                output = stdout.decode("utf-8", errors="replace")
                session_id_match = re.search(r"session_id:\s*([a-zA-Z0-9_-]+)", output)
                if session_id_match:
                    self._last_codex_session_id = session_id_match.group(1).strip()
                else:
                    self._last_codex_session_id = None
                res = clean_hermes_output(output)
                if not res:
                    logger.warning(f"Codex returned empty or filtered response. Raw: {output[:300]}")
                return res
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning("Codex query timed out after 180s")
                return None
        except Exception as e:
            logger.error(f"Error querying Codex from assistant: {e}")
            return None

    async def _query_model(
        self,
        prompt: str,
        image_path: Optional[Path] = None,
        chat_id: Optional[int] = None,
    ) -> Optional[str]:
        """Unified query dispatcher defaulting to free agy (3.8 Flash Low), falling back to Codex."""
        engine = getattr(self, "active_engine", self.config.default_engine)
        if engine == "agy":
            reply = await self._query_agy(prompt, image_path=image_path, chat_id=chat_id)
            if reply:
                return reply
            logger.warning("Agy query failed or exhausted; automatically falling back to Codex...")
            return await self._query_codex(prompt, image_path=image_path, chat_id=chat_id)
        else:
            reply = await self._query_codex(prompt, image_path=image_path, chat_id=chat_id)
            if reply:
                return reply
            logger.warning("Codex query failed; automatically falling back to Agy...")
            return await self._query_agy(prompt, image_path=image_path, chat_id=chat_id)

    async def _dispatch_agy_coding(self, prompt: str, chat_id: int) -> bool:
        """Dispatches an advanced coding task to agy via subagent.py."""
        status_msg_id = await self.gateway.send_message(
            chat_id, "⚡️ <i>Launching agy coding task...</i>"
        )
        try:
            cmd = [
                "python3",
                os.path.expanduser("~/projects/ai-os/scripts/subagent.py"),
                "-p", prompt,
                "--use-agy",
                "--no-tmux",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode("utf-8", errors="replace").strip()
            if not output:
                output = "✅ Agy completed the task."
            await self.gateway.edit_message(chat_id, status_msg_id, output)
            return True
        except Exception as e:
            logger.error(f"Failed to run agy coding task: {e}")
            await self.gateway.edit_message(chat_id, status_msg_id, f"❌ Failed to run agy: {e}")
            return False

    async def _deliver_model_response(
        self,
        chat_id: int,
        model_reply: str,
        status_msg_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Cleans the model's text response, saves it to history, updates status/sends message,
        and extracts and delivers any attached media natively to Telegram.
        """
        # 1. Extract MEDIA: tags and directives from the response text
        clean_text, media_items = extract_media_from_text(model_reply)

        # 2. Check if the session generated any media via tools (TTS, image generation, etc.)
        effective_session_id = session_id or getattr(self, "_last_codex_session_id", None)
        if effective_session_id:
            tool_media = find_session_generated_media(effective_session_id)
            for tm in tool_media:
                if not any(item["path"] == tm["path"] for item in media_items):
                    media_items.append(tm)

        # 3. Fallback: check for recently created local paths mentioned in text
        if not media_items:
            mentioned = find_deliverable_paths_in_text(clean_text)
            for p in mentioned:
                media_items.append({"path": p, "is_voice": False, "as_document": False})

        # 4. Save clean text to database
        if clean_text:
            await self.db.add_chat_message(chat_id, "assistant", clean_text)

        # 5. Deliver or edit text message
        if clean_text:
            if status_msg_id:
                await self.gateway.edit_message(chat_id, status_msg_id, clean_text)
            else:
                await self.gateway.send_message(chat_id, clean_text)
        elif status_msg_id and not media_items:
            await self.gateway.edit_message(chat_id, status_msg_id, "✅")

        # 6. Deliver all media attachments natively
        for item in media_items:
            path = item["path"]
            is_voice = item.get("is_voice", False)
            as_doc = item.get("as_document", False)
            logger.info(
                f"Delivering attachment to chat {chat_id}: {path.name} "
                f"(voice={is_voice}, as_doc={as_doc})"
            )
            await self.gateway.send_media(
                chat_id=chat_id,
                file_path=path,
                is_voice=is_voice,
                as_document=as_doc,
            )

        return True

    # -------------------------------------------------------------------------
    # Plain Text Handler (Prompt replies, natural keywords, capture, AI conversation)
    # -------------------------------------------------------------------------
    async def handle_text_message(
        self, text: str, chat_id: int, message_id: int
    ) -> bool:
        clean_text = text.strip()
        if not clean_text:
            return False

        lower_text = clean_text.lower()

        # 1. Check if user is replying to an active prompt awaiting response
        signals = await self.db.get_awaiting_signals()
        active_signal = next((s for s in signals if s["chat_id"] == chat_id), None)

        if active_signal:
            trigger_id = active_signal["trigger_id"]
            prompt_msg_id = active_signal["message_id"]

            # FSRS review active prompt
            if trigger_id.startswith("trig_fsrs_"):
                card_id = trigger_id.replace("trig_fsrs_", "")
                card = await self.db.get_card(card_id)
                if card:
                    option_map = {"a": 0, "1": 0, "b": 1, "2": 1, "c": 2, "3": 2, "d": 3, "4": 3}
                    if lower_text in option_map:
                        idx = option_map[lower_text]
                        await self._handle_fsrs_pick(card_id, idx, chat_id, prompt_msg_id)
                        return True

                    if card.get("options"):
                        try:
                            opts = json.loads(card["options"]) if isinstance(card["options"], str) else card["options"]
                            for idx, opt in enumerate(opts):
                                if lower_text == opt.strip().lower():
                                    await self._handle_fsrs_pick(card_id, idx, chat_id, prompt_msg_id)
                                    return True
                        except Exception:
                            pass

                    struggle_map = {
                        "again": 1, "lucky": 1, "guess": 1, "1": 1,
                        "hard": 2, "struggled": 2, "struggle": 2, "2": 2,
                        "good": 3, "confident": 3, "3": 3,
                        "easy": 4, "instant": 4, "4": 4,
                    }
                    for kw, r_val in struggle_map.items():
                        if kw in lower_text.split():
                            await self._handle_fsrs(card_id, r_val, chat_id, prompt_msg_id)
                            return True

            # Habit check active prompt
            elif trigger_id.startswith("trig_habit_"):
                parts = trigger_id.split("_")
                habit_name = parts[2] if len(parts) > 2 else "Habit"
                if any(w in lower_text for w in ("emergency", "2min", "quick")):
                    await self._handle_habit(habit_name, "emergency", chat_id, prompt_msg_id)
                    return True
                elif any(w in lower_text for w in ("full", "done", "yes", "completed")):
                    await self._handle_habit(habit_name, "full", chat_id, prompt_msg_id)
                    return True

            # Morning briefing active prompt (user replied to morning prompt)
            elif trigger_id.startswith("trig_morning_") or trigger_id == "trig_morning_manual":
                await self.cmd_gratitude(clean_text, chat_id)
                await self.db.resolve_signal(prompt_msg_id, "RESPONDED")
                return True

        # 2. Check for natural command keywords
        if lower_text in ("status", "info"):
            return await self.cmd_status(chat_id)
        elif lower_text in ("quiz", "review", "test"):
            return await self.cmd_quiz(chat_id)
        elif lower_text in ("habits", "habit"):
            return await self.cmd_habits(chat_id)
        elif lower_text in ("morning", "briefing", "good morning"):
            return await self.cmd_morning(chat_id)
        elif re.match(r"^(gratitude:\s*|grateful for\s*|i am grateful for\s*|i'm grateful for\s*)", lower_text):
            thought = re.sub(r"^(gratitude:\s*|grateful for\s*|i am grateful for\s*|i'm grateful for\s*)", "", clean_text, flags=re.IGNORECASE).strip()
            return await self.cmd_gratitude(thought, chat_id)
        elif lower_text in ("help", "start"):
            return await self.cmd_help(chat_id)
        elif lower_text in ("reset", "clear", "new chat", "forget"):
            return await self.cmd_reset(chat_id)
        elif lower_text in ("engine", "model"):
            return await self.cmd_engine("", chat_id)

        # 3. Check for reminders (Apple Reminders protocol)
        if re.match(r"^(remind me to |remind me |todo:\s*|remember to )", lower_text):
            title = re.sub(r"^(remind me to |remind me |todo:\s*|remember to )", "", clean_text, flags=re.IGNORECASE).strip()
            return await self.cmd_remind(title, chat_id)

        # 4. Check for quick note / capture prefix
        if re.match(r"^(note:\s*|capture:\s*|idea:\s*)", lower_text):
            note = re.sub(r"^(note:\s*|capture:\s*|idea:\s*)", "", clean_text, flags=re.IGNORECASE).strip()
            return await self.cmd_capture(note, chat_id)

        # 4.5. Check for explicit agy coding task
        if re.match(r"^(agy:\s*|code:\s*)", lower_text):
            coding_task = re.sub(r"^(agy:\s*|code:\s*)", "", clean_text, flags=re.IGNORECASE).strip()
            return await self._dispatch_agy_coding(coding_task, chat_id)

        # 5. Conversational Assistant (defaulting to free Agy 3.8 Flash Low, fallback to Codex)
        engine = getattr(self, "active_engine", self.config.default_engine)
        engine_label = "Gemini 3.8 Flash Low (Free)" if engine == "agy" else "Codex"
        status_msg_id = await self.gateway.send_message(
            chat_id, f"💬 <i>Thinking with {engine_label}...</i>"
        )

        stop_typing = asyncio.Event()

        async def _typing_heartbeat():
            while not stop_typing.is_set():
                await self.gateway.send_chat_action(chat_id, "typing")
                try:
                    await asyncio.wait_for(stop_typing.wait(), timeout=4.0)
                except asyncio.TimeoutError:
                    pass

        typing_task = asyncio.create_task(_typing_heartbeat())

        recent_history = await self.db.get_recent_chat_history(chat_id, limit=8)
        augmented_prompt = build_conversational_prompt(clean_text, recent_history)
        await self.db.add_chat_message(chat_id, "user", clean_text)

        try:
            model_reply = await self._query_model(augmented_prompt, chat_id=chat_id)
        finally:
            stop_typing.set()
            try:
                await typing_task
            except Exception:
                pass

        if model_reply:
            return await self._deliver_model_response(
                chat_id=chat_id,
                model_reply=model_reply,
                status_msg_id=status_msg_id,
                session_id=getattr(self, "_last_codex_session_id", None),
            )

        fail_msg = (
            "⚠️ <i>Unable to get a response from the AI assistant right now.</i>\n\n"
            "Please check network/credentials and try again."
        )
        if status_msg_id:
            await self.gateway.edit_message(chat_id, status_msg_id, fail_msg)
        else:
            await self.gateway.send_message(chat_id, fail_msg)
        return False

    # -------------------------------------------------------------------------
    # Multimodal Media Handlers (Photos, Voice/Audio STT, Videos, Documents)
    # -------------------------------------------------------------------------
    async def handle_photo_message(
        self, photo_path: Path, caption: Optional[str], chat_id: int, message_id: int
    ) -> bool:
        """Inspects and explains user-provided photos/screenshots using Agy Vision or Codex Vision."""
        user_prompt = caption.strip() if caption and caption.strip() else "Please inspect and explain what is shown in this image in detail:"
        engine = getattr(self, "active_engine", self.config.default_engine)
        engine_label = "Gemini 3.8 Flash Low (Free)" if engine == "agy" else "Codex Vision"
        status_msg_id = await self.gateway.send_message(
            chat_id, f"🖼️ <i>Analyzing image with {engine_label}...</i>"
        )

        stop_typing = asyncio.Event()

        async def _typing_heartbeat():
            while not stop_typing.is_set():
                await self.gateway.send_chat_action(chat_id, "typing")
                try:
                    await asyncio.wait_for(stop_typing.wait(), timeout=4.0)
                except asyncio.TimeoutError:
                    pass

        typing_task = asyncio.create_task(_typing_heartbeat())

        recent_history = await self.db.get_recent_chat_history(chat_id, limit=6)
        augmented_prompt = build_conversational_prompt(user_prompt, recent_history)
        await self.db.add_chat_message(chat_id, "user", f"[Photo attached: {photo_path.name}] {user_prompt}")

        try:
            reply = await self._query_model(augmented_prompt, image_path=photo_path, chat_id=chat_id)
        finally:
            stop_typing.set()
            try:
                await typing_task
            except Exception:
                pass

        if reply:
            return await self._deliver_model_response(
                chat_id=chat_id,
                model_reply=reply,
                status_msg_id=status_msg_id,
                session_id=getattr(self, "_last_codex_session_id", None),
            )

        fail_msg = "⚠️ <i>Unable to analyze image right now.</i>"
        if status_msg_id:
            await self.gateway.edit_message(chat_id, status_msg_id, fail_msg)
        else:
            await self.gateway.send_message(chat_id, fail_msg)
        return False

    async def handle_audio_message(
        self, audio_path: Path, chat_id: int, message_id: int, caption: Optional[str] = None
    ) -> bool:
        """Transcribes voice notes or audio files using Groq Whisper and processes as query."""
        status_msg_id = await self.gateway.send_message(
            chat_id, "🎙️ <i>Transcribing voice note with Groq Whisper...</i>"
        )
        try:
            transcript = await transcribe_audio_file(
                audio_path, api_key=self.config.groq_api_key
            )
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            transcript = None

        if not transcript:
            await self.gateway.edit_message(
                chat_id,
                status_msg_id,
                "⚠️ <i>Unable to transcribe audio message via Groq.</i>",
            )
            return False

        full_query = f"{caption.strip()} {transcript.strip()}" if caption and caption.strip() else transcript.strip()
        await self.gateway.edit_message(
            chat_id,
            status_msg_id,
            f"🎙️ <i>\"{full_query}\"</i>",
        )
        return await self.handle_text_message(full_query, chat_id, message_id)

    async def handle_video_message(
        self, video_path: Path, chat_id: int, message_id: int, caption: Optional[str] = None
    ) -> bool:
        """Extracts audio from video and transcribes with Groq Whisper."""
        status_msg_id = await self.gateway.send_message(
            chat_id, "🎬 <i>Processing video audio...</i>"
        )
        audio_path = extract_audio_from_video(video_path)
        transcript = None
        if audio_path and audio_path.exists():
            try:
                transcript = await transcribe_audio_file(
                    audio_path, api_key=self.config.groq_api_key
                )
            except Exception as e:
                logger.error(f"Error transcribing video audio: {e}")
            finally:
                if audio_path.exists():
                    try:
                        audio_path.unlink()
                    except Exception:
                        pass

        if transcript:
            full_query = f"{caption.strip()} {transcript.strip()}" if caption and caption.strip() else transcript.strip()
            await self.gateway.edit_message(
                chat_id,
                status_msg_id,
                f"🎬 <i>\"{full_query}\"</i>",
            )
            return await self.handle_text_message(full_query, chat_id, message_id)
        elif caption and caption.strip():
            await self.gateway.edit_message(chat_id, status_msg_id, f"🎬 <i>Received video: \"{caption.strip()}\"</i>")
            return await self.handle_text_message(caption.strip(), chat_id, message_id)
        else:
            await self.gateway.edit_message(chat_id, status_msg_id, "⚠️ <i>No speech or caption detected in video.</i>")
            return False

    async def handle_document_message(
        self,
        doc_path: Path,
        file_name: str,
        mime_type: Optional[str],
        caption: Optional[str],
        chat_id: int,
        message_id: int,
    ) -> bool:
        """Routes documents by file type (images to Vision, audio/video to STT, code/text to Codex)."""
        ext = doc_path.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"):
            return await self.handle_photo_message(doc_path, caption, chat_id, message_id)
        elif ext in (".ogg", ".oga", ".mp3", ".wav", ".m4a", ".webm", ".flac", ".aac"):
            return await self.handle_audio_message(doc_path, chat_id, message_id, caption=caption)
        elif ext in (".mp4", ".mov", ".mkv", ".avi"):
            return await self.handle_video_message(doc_path, chat_id, message_id, caption=caption)

        # Text and code files
        try:
            content = doc_path.read_text(encoding="utf-8", errors="replace")
            if len(content) > 50000:
                content = content[:50000] + "\n... [content truncated]"
            user_prompt = caption.strip() if caption and caption.strip() else f"Analyze and explain the contents of file `{file_name}`:"
            formatted_query = f"[Attached File: {file_name}]\n```\n{content}\n```\n\n{user_prompt}"
            return await self.handle_text_message(formatted_query, chat_id, message_id)
        except Exception as e:
            logger.error(f"Failed to read document {doc_path}: {e}")
            await self.gateway.send_message(
                chat_id, f"📁 Received file <code>{html.escape(file_name)}</code> ({ext})."
            )
            return True


def register_handlers(dispatcher: ActionDispatcher, gateway: TelegramGateway) -> None:
    """Registers callback queries, command handlers, and media/text message handlers with python-telegram-bot."""
    async def telegram_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query or not query.data:
            return

        chat_id = query.message.chat_id if query.message else 0
        message_id = query.message.message_id if query.message else 0

        try:
            await query.answer()
        except Exception as e:
            logger.debug(f"Callback query.answer warning (likely expired query): {e}")

        await dispatcher.handle_callback_str(query.data, chat_id, message_id)

    async def telegram_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_help(chat_id)

    async def telegram_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_status(chat_id)

    async def telegram_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_quiz(chat_id)

    async def telegram_habits_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_habits(chat_id)

    async def telegram_reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_reset(chat_id)

    async def telegram_capture_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        text = " ".join(context.args) if context.args else ""
        if text:
            await dispatcher.cmd_capture(text, chat_id)
        else:
            await gateway.send_message(chat_id, "Usage: `/capture <note text>` or `/note <note text>`")

    async def telegram_remind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        text = " ".join(context.args) if context.args else ""
        if text:
            await dispatcher.cmd_remind(text, chat_id)
        else:
            await gateway.send_message(chat_id, "Usage: `/remind <reminder title>`")

    async def telegram_morning_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        await dispatcher.cmd_morning(chat_id)

    async def telegram_gratitude_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        text = " ".join(context.args) if context.args else ""
        if text:
            await dispatcher.cmd_gratitude(text, chat_id)
        else:
            await gateway.send_message(chat_id, "Usage: `/gratitude <what you are thankful for>`")

    async def telegram_agy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        text = " ".join(context.args) if context.args else ""
        if text:
            await dispatcher._dispatch_agy_coding(text, chat_id)
        else:
            await gateway.send_message(chat_id, "Usage: `/agy <coding instruction>`")

    async def telegram_engine_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id if update.effective_chat else 0
        choice = " ".join(context.args) if context.args else ""
        await dispatcher.cmd_engine(choice, chat_id)

    async def telegram_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg or not msg.photo:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        photo = msg.photo[-1]
        try:
            file = await photo.get_file()
            target_dir = dispatcher.config.media_tmp_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{file.file_unique_id}.jpg"
            await file.download_to_drive(custom_path=str(target_path))
            await dispatcher.handle_photo_message(target_path, msg.caption, chat_id, message_id)
        except Exception as e:
            logger.error(f"Error handling photo message: {e}")
            await gateway.send_message(chat_id, f"❌ Failed to process photo: {e}")

    async def telegram_audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg:
            return
        audio_obj = msg.voice or msg.audio
        if not audio_obj:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        try:
            file = await audio_obj.get_file()
            target_dir = dispatcher.config.media_tmp_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            ext = ".ogg" if msg.voice else (Path(getattr(audio_obj, "file_name", "audio.mp3")).suffix or ".mp3")
            target_path = target_dir / f"{file.file_unique_id}{ext}"
            await file.download_to_drive(custom_path=str(target_path))
            await dispatcher.handle_audio_message(target_path, chat_id, message_id, caption=msg.caption)
        except Exception as e:
            logger.error(f"Error handling audio message: {e}")
            await gateway.send_message(chat_id, f"❌ Failed to process audio: {e}")

    async def telegram_video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg:
            return
        vid_obj = msg.video or msg.video_note
        if not vid_obj:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        try:
            file = await vid_obj.get_file()
            target_dir = dispatcher.config.media_tmp_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            ext = Path(getattr(vid_obj, "file_name", "video.mp4")).suffix or ".mp4"
            target_path = target_dir / f"{file.file_unique_id}{ext}"
            await file.download_to_drive(custom_path=str(target_path))
            await dispatcher.handle_video_message(target_path, chat_id, message_id, caption=msg.caption)
        except Exception as e:
            logger.error(f"Error handling video message: {e}")
            await gateway.send_message(chat_id, f"❌ Failed to process video: {e}")

    async def telegram_document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg or not msg.document:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        doc = msg.document
        try:
            file = await doc.get_file()
            target_dir = dispatcher.config.media_tmp_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            file_name = doc.file_name or f"{file.file_unique_id}.bin"
            target_path = target_dir / f"{file.file_unique_id}_{file_name}"
            await file.download_to_drive(custom_path=str(target_path))
            await dispatcher.handle_document_message(
                target_path, file_name, doc.mime_type, msg.caption, chat_id, message_id
            )
        except Exception as e:
            logger.error(f"Error handling document message: {e}")
            await gateway.send_message(chat_id, f"❌ Failed to process document: {e}")

    async def telegram_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg or not msg.text:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        await dispatcher.handle_text_message(msg.text, chat_id, message_id)

    gateway.add_callback_handler(telegram_callback_handler)
    gateway.add_handler(CommandHandler(["start", "help"], telegram_start_handler))
    gateway.add_handler(CommandHandler(["morning", "briefing"], telegram_morning_handler))
    gateway.add_handler(CommandHandler(["gratitude", "thankful"], telegram_gratitude_handler))
    gateway.add_handler(CommandHandler(["status", "info"], telegram_status_handler))
    gateway.add_handler(CommandHandler(["quiz", "review"], telegram_quiz_handler))
    gateway.add_handler(CommandHandler(["habits", "habit"], telegram_habits_handler))
    gateway.add_handler(CommandHandler(["reset", "clear", "new"], telegram_reset_handler))
    gateway.add_handler(CommandHandler(["capture", "note"], telegram_capture_handler))
    gateway.add_handler(CommandHandler(["remind", "todo"], telegram_remind_handler))
    gateway.add_handler(CommandHandler(["engine", "model"], telegram_engine_handler))
    gateway.add_handler(CommandHandler(["agy", "code"], telegram_agy_handler))
    gateway.add_handler(MessageHandler(filters.PHOTO, telegram_photo_handler))
    gateway.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, telegram_audio_handler))
    gateway.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, telegram_video_handler))
    gateway.add_handler(MessageHandler(filters.Document.ALL, telegram_document_handler))
    gateway.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_text_handler))

