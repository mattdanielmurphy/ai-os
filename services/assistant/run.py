"""Main event loop & launchd entrypoint for the Proactive Executive Assistant Service."""

import asyncio
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from .config import AssistantConfig
from .context_gate.calendar import CalendarProbe
from .context_gate.evaluator import ContextGateEvaluator
from .context_gate.focus_mode import FocusModeProbe
from .habit_bridge.logger import HabitLogger, format_habit_prompt
from .habit_bridge.parser import HabitParser
from .spaced_repetition.cards import format_review_prompt
from .spaced_repetition.engine import FSRSEngine
from .storage.db import AssistantDB
from .telegram_gateway.bot import TelegramGateway
from .telegram_gateway.handlers import ActionDispatcher, register_handlers
from .telegram_gateway.silence import AwakeSilenceWatchdog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
# Silence httpx URL requests so Telegram bot token in endpoint URL is never logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("assistant.daemon")


class AssistantDaemon:
    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        self.db = AssistantDB(self.config.db_path)
        self.calendar_probe = CalendarProbe()
        self.focus_probe = FocusModeProbe()
        self.evaluator = ContextGateEvaluator(
            self.config, self.db, self.calendar_probe, self.focus_probe
        )
        self.fsrs_engine = FSRSEngine(self.config)
        self.habit_parser = HabitParser(self.config.habits_definitions_dir)
        self.habit_logger = HabitLogger(self.config.habits_logs_dir)
        self.gateway = TelegramGateway(self.config)
        self.dispatcher = ActionDispatcher(
            self.db, self.fsrs_engine, self.habit_logger, self.gateway
        )
        self.silence_watchdog = AwakeSilenceWatchdog(self.config, self.db, self.gateway)
        self._running = False

    async def setup(self) -> None:
        """Initializes database, TCC permission checks, and Telegram handlers."""
        logger.info("Starting Proactive Assistant Daemon...")
        await self.db.connect()

        # Startup Calendar TCC health check
        tcc_ok = self.calendar_probe.check_tcc_permission()
        if tcc_ok:
            logger.info("Calendar TCC permission confirmed.")
        else:
            logger.warning(
                "Calendar access unconfirmed or restricted! Check System Settings -> Privacy & Security -> Calendars."
            )

        # Initialize Telegram
        await self.gateway.initialize()
        register_handlers(self.dispatcher, self.gateway)
        await self.gateway.start()

    async def teardown(self) -> None:
        """Shuts down gateway and database connections gracefully."""
        logger.info("Shutting down Proactive Assistant Daemon...")
        self._running = False
        await self.gateway.stop()
        await self.db.close()
        logger.info("Assistant Daemon stopped cleanly.")

    async def run(self) -> None:
        await self.setup()
        self._running = True

        last_wall_time = time.time()
        last_mono_time = time.monotonic()

        while self._running:
            try:
                now_wall = time.time()
                now_mono = time.monotonic()

                wall_elapsed = now_wall - last_wall_time
                mono_elapsed = now_mono - last_mono_time

                # Awake time delta is bounded by monotonic elapsed time
                awake_seconds_delta = min(wall_elapsed, mono_elapsed)

                # Detect sleep gap (lid closed / system suspend)
                if (wall_elapsed - mono_elapsed) > self.config.sleep_gap_threshold_seconds:
                    sleep_duration = wall_elapsed - mono_elapsed
                    logger.warning(
                        f"Detected sleep-wake event: Mac was suspended for ~{sleep_duration:.1f}s. "
                        "Entering SLEEP_RECOVERY_MODE."
                    )
                    await self._handle_sleep_recovery()
                    # After sleep, awake time delta for this tick is just the immediate wake duration
                    awake_seconds_delta = min(5.0, mono_elapsed)

                last_wall_time = now_wall
                last_mono_time = now_mono

                # 1. Advance silence watchdog using awake seconds only
                await self.silence_watchdog.tick(awake_seconds_delta)

                # 2. Expire any stale triggers whose TTL passed
                now_utc = datetime.now(timezone.utc)
                await self.db.expire_stale_triggers(now_utc)

                # 3. Evaluate and process next pending trigger
                await self._process_pending_triggers(now_utc)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in assistant daemon loop: {e}", exc_info=True)

            # Wait for next poll interval
            await asyncio.sleep(self.config.poll_interval_seconds)

    async def _handle_sleep_recovery(self) -> None:
        """
        Sleep recovery protocol:
        - Expire triggers whose TTL has already passed.
        - If multiple triggers are pending, pick ONLY the single highest-priority valid item.
        - Push all other pending triggers out by +30m to prevent alert avalanches upon waking.
        """
        now_utc = datetime.now(timezone.utc)
        expired = await self.db.expire_stale_triggers(now_utc)
        if expired > 0:
            logger.info(f"Sleep recovery: Silently expired {expired} stale trigger(s).")

        pending = await self.db.get_pending_triggers(now_utc)
        if len(pending) > 1:
            highest_priority_id = pending[0]["id"]
            delayed = await self.db.delay_pending_triggers_except(
                highest_priority_id, delay_minutes=30
            )
            logger.info(
                f"Sleep recovery: Kept highest priority trigger '{highest_priority_id}', "
                f"delayed {delayed} remaining trigger(s) by +30m to prevent alert avalanche."
            )

    async def _process_pending_triggers(self, now_utc: datetime) -> None:
        pending = await self.db.get_pending_triggers(now_utc)
        if not pending:
            return

        # Pick highest priority item
        trigger = pending[0]
        trigger_id = trigger["id"]
        trigger_type = trigger["trigger_type"]
        target_id = trigger["target_id"]

        # Evaluate Context Gate
        gate = await self.evaluator.evaluate(now_utc)
        if not gate.allowed:
            logger.info(
                f"Context Gate suppressed trigger '{trigger_id}' ({gate.reason}). "
                f"Rescheduling in {gate.retry_after_seconds}s."
            )
            retry_time = now_utc + timedelta(seconds=max(60, gate.retry_after_seconds))
            await self.db.reschedule_trigger(trigger_id, new_scheduled_at=retry_time)
            return

        # Gate cleared: Fire prompt
        chat_id = self.config.telegram_chat_id or 0
        message_id: Optional[int] = None

        if trigger_type == "fsrs_review":
            card = await self.db.get_card(target_id)
            if card:
                text, keyboard = format_review_prompt(card)
                message_id = await self.gateway.send_prompt(chat_id, text, keyboard)
            else:
                logger.error(f"FSRS review trigger for missing card '{target_id}'")
                await self.db.update_trigger_status(trigger_id, "EXPIRED")
                return

        elif trigger_type == "habit_check":
            habit = self.habit_parser.get_habit(target_id)
            if habit:
                text, keyboard = format_habit_prompt(habit)
                message_id = await self.gateway.send_prompt(chat_id, text, keyboard)
            else:
                logger.error(f"Habit check trigger for missing habit definition '{target_id}'")
                await self.db.update_trigger_status(trigger_id, "EXPIRED")
                return

        elif trigger_type == "micro_step":
            # Generic micro-step prompt
            text = f"🎯 *Micro-Step Action*\n\n{target_id}\n\n_Take 2 minutes to complete this step._"
            keyboard = [[{"text": "✅ Done", "callback_data": f"micro:{trigger_id}:done"}]]
            message_id = await self.gateway.send_prompt(chat_id, text, keyboard)

        if message_id:
            timeout_at = now_utc + timedelta(seconds=self.config.silence_timeout_seconds)
            await self.db.record_outbound_signal(
                message_id=message_id,
                chat_id=chat_id,
                trigger_id=trigger_id,
                sent_at=now_utc,
                timeout_at=timeout_at,
                status="AWAITING_INPUT",
            )
            await self.db.update_trigger_status(trigger_id, "FIRED")
            logger.info(f"Trigger '{trigger_id}' FIRED successfully as Telegram message {message_id}.")


async def main():
    daemon = AssistantDaemon()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Termination signal received.")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    runner_task = asyncio.create_task(daemon.run())
    await stop_event.wait()
    await daemon.teardown()
    runner_task.cancel()
    try:
        await runner_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
