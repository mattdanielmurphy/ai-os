"""Callback Query Handlers for FSRS and Habit button interactions."""

import logging
from datetime import datetime, timezone
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from ..habit_bridge.logger import HabitLogger, format_habit_completed
from ..spaced_repetition.cards import format_feedback_prompt, format_review_completed
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
    ):
        self.db = db
        self.fsrs_engine = fsrs_engine
        self.habit_logger = habit_logger
        self.gateway = gateway

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


def register_handlers(dispatcher: ActionDispatcher, gateway: TelegramGateway) -> None:
    """Registers callback query handlers with python-telegram-bot."""
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

    gateway.add_callback_handler(telegram_callback_handler)
