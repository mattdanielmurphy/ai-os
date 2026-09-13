"""Telegram handlers for callbacks, text messages, executive commands, and quick capture."""

import asyncio
import json
import logging
import os
import re
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ..config import AssistantConfig
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

logger = logging.getLogger("assistant.telegram_gateway.handlers")


class ActionDispatcher:
    def __init__(
        self,
        db: AssistantDB,
        fsrs_engine: FSRSEngine,
        habit_logger: HabitLogger,
        gateway: TelegramGateway,
        config: Optional[AssistantConfig] = None,
        habit_parser: Optional[HabitParser] = None,
    ):
        self.db = db
        self.fsrs_engine = fsrs_engine
        self.habit_logger = habit_logger
        self.gateway = gateway
        self.config = config or AssistantConfig()
        self.habit_parser = habit_parser

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

        elif action_type == "cmd" and len(parts) >= 2:
            cmd_name = parts[1]
            if cmd_name == "quiz":
                return await self.cmd_quiz(chat_id)
            elif cmd_name == "habits":
                return await self.cmd_habits(chat_id)
            elif cmd_name == "status":
                return await self.cmd_status(chat_id)

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
            "I manage your spaced repetition reviews, habit tracking, and proactive check-ins.\n\n"
            "*Available Commands:*\n"
            "• `/quiz` or `/review` — Start an immediate spaced repetition quiz\n"
            "• `/status` — View active triggers, due cards, and gate status\n"
            "• `/habits` — View today's habit check-ins\n"
            "• `/note <text>` — Quick capture note directly to Obsidian Inbox\n"
            "• `/remind <text>` — Add timed reminder to Apple Reminders\n\n"
            "_Tip: You can reply directly to quizzes with A, B, C, D in text, or ask me any question!_"
        )
        keyboard = [
            [
                {"text": "📚 Quiz Me", "callback_data": "cmd:quiz"},
                {"text": "📊 Status", "callback_data": "cmd:status"},
            ]
        ]
        await self.gateway.send_message(chat_id, help_text, keyboard_rows=keyboard)
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

    async def _query_aios(self, prompt: str) -> Optional[str]:
        try:
            cmd = [
                "node",
                os.path.expanduser("~/projects/ai-os/scripts/query_aios.js"),
                prompt,
                "--timeout", "25",
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
                output = stdout.decode("utf-8", errors="replace")

                if "--------------------------------------------------------------------------------" in output:
                    parts = output.split("--------------------------------------------------------------------------------")
                    if len(parts) >= 2:
                        ans = parts[1].split("================================================================================")[0]
                        return ans.strip()
                return output.strip() if output.strip() else None
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning("AI-OS query timed out after 30s")
                return None
        except Exception as e:
            logger.error(f"Error querying AI-OS from assistant: {e}")
            return None

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

        # 2. Check for natural command keywords
        if lower_text in ("status", "info"):
            return await self.cmd_status(chat_id)
        elif lower_text in ("quiz", "review", "test"):
            return await self.cmd_quiz(chat_id)
        elif lower_text in ("habits", "habit"):
            return await self.cmd_habits(chat_id)
        elif lower_text in ("help", "start"):
            return await self.cmd_help(chat_id)

        # 3. Check for reminders (Apple Reminders protocol)
        if re.match(r"^(remind me to |remind me |todo:\s*|remember to )", lower_text):
            title = re.sub(r"^(remind me to |remind me |todo:\s*|remember to )", "", clean_text, flags=re.IGNORECASE).strip()
            return await self.cmd_remind(title, chat_id)

        # 4. Check for quick note / capture prefix
        if re.match(r"^(note:\s*|capture:\s*|idea:\s*)", lower_text):
            note = re.sub(r"^(note:\s*|capture:\s*|idea:\s*)", "", clean_text, flags=re.IGNORECASE).strip()
            return await self.cmd_capture(note, chat_id)

        # 5. Conversational Assistant via AI-OS
        await self.gateway.send_chat_action(chat_id, "typing")
        aios_reply = await self._query_aios(clean_text)
        if aios_reply:
            await self.gateway.send_message(chat_id, aios_reply)
            return True

        # Fallback: Save to Obsidian Inbox
        return await self.cmd_capture(clean_text, chat_id)


def register_handlers(dispatcher: ActionDispatcher, gateway: TelegramGateway) -> None:
    """Registers callback queries, command handlers, and text message handlers with python-telegram-bot."""
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

    async def telegram_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.effective_message
        if not msg or not msg.text:
            return
        chat_id = update.effective_chat.id if update.effective_chat else 0
        message_id = msg.message_id
        await dispatcher.handle_text_message(msg.text, chat_id, message_id)

    gateway.add_callback_handler(telegram_callback_handler)
    gateway.add_handler(CommandHandler(["start", "help"], telegram_start_handler))
    gateway.add_handler(CommandHandler(["status", "info"], telegram_status_handler))
    gateway.add_handler(CommandHandler(["quiz", "review"], telegram_quiz_handler))
    gateway.add_handler(CommandHandler(["habits", "habit"], telegram_habits_handler))
    gateway.add_handler(CommandHandler(["capture", "note"], telegram_capture_handler))
    gateway.add_handler(CommandHandler(["remind", "todo"], telegram_remind_handler))
    gateway.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_text_handler))
