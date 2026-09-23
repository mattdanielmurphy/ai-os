"""Awake-time silence watchdog preventing false timeouts during Mac sleep."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..config import AssistantConfig
from ..storage.db import AssistantDB
from .bot import TelegramGateway

logger = logging.getLogger("assistant.telegram_gateway.silence")


class AwakeSilenceWatchdog:
    def __init__(
        self,
        config: AssistantConfig,
        db: AssistantDB,
        gateway: TelegramGateway,
    ):
        self.config = config
        self.db = db
        self.gateway = gateway

    async def tick(self, awake_seconds_delta: float, current_time: Optional[datetime] = None) -> int:
        """
        Advances the awake timer on awaiting outbound signals by awake_seconds_delta.
        Mutes expired messages and enforces empathetic backoff cooldowns.
        Returns:
            Number of signals expired during this tick.
        """
        if awake_seconds_delta <= 0:
            return 0

        now = current_time or datetime.now(timezone.utc)
        signals = await self.db.get_awaiting_signals()
        expired_count = 0

        for sig in signals:
            msg_id = sig["message_id"]
            chat_id = sig["chat_id"]

            accumulated = await self.db.update_signal_awake_time(msg_id, awake_seconds_delta)
            # A non-positive timeout is the explicit "never expire" setting. The previous
            # 45-minute default made a check-in disappear while it was still useful, and a
            # plain `>= 0` comparison would make unlimited mode expire on the first tick.
            timeout_seconds = self.config.silence_timeout_seconds
            if timeout_seconds > 0 and accumulated >= timeout_seconds:
                logger.info(
                    f"Outbound signal {msg_id} reached {accumulated:.1f}s awake time without response. "
                    "Muting prompt and triggering silence cooldown."
                )

                # Remove interaction controls but preserve the original prompt text.
                # The user should not see a visible "Check-in expired" replacement.
                await self.gateway.remove_prompt_keyboard(
                    chat_id=chat_id,
                    message_id=msg_id,
                )

                # Mark signal as SILENT_TIMEOUT
                await self.db.resolve_signal(msg_id, "SILENT_TIMEOUT")

                # Set silence cooldown in user dynamics (e.g. back off for 2 hours)
                cooldown_until = now + timedelta(seconds=self.config.silence_cooldown_seconds)
                await self.db.set_dynamic("silence_cooldown_until", cooldown_until.isoformat())

                expired_count += 1

        return expired_count
