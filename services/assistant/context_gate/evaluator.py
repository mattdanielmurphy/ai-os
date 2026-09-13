"""Context Gate Evaluator combining Calendar, Focus Mode, and Silence Cooldowns."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from ..config import AssistantConfig
from ..storage.db import AssistantDB
from .calendar import CalendarProbe
from .focus_mode import FocusModeProbe

logger = logging.getLogger("assistant.context_gate.evaluator")


@dataclass
class GateEvaluation:
    allowed: bool
    reason: str
    retry_after_seconds: int = 0
    detail: Optional[str] = None


class ContextGateEvaluator:
    def __init__(
        self,
        config: AssistantConfig,
        db: AssistantDB,
        calendar_probe: Optional[CalendarProbe] = None,
        focus_probe: Optional[FocusModeProbe] = None,
    ):
        self.config = config
        self.db = db
        self.calendar_probe = calendar_probe or CalendarProbe()
        self.focus_probe = focus_probe or FocusModeProbe()

    async def evaluate(self, current_time: Optional[datetime] = None) -> GateEvaluation:
        now = current_time or datetime.now(timezone.utc)

        # 1. Check Silence Cooldown
        # If user ignored a prompt, silence watchdog sets a cooldown timestamp
        cooldown_until_str = await self.db.get_dynamic("silence_cooldown_until")
        if cooldown_until_str:
            try:
                cooldown_until = datetime.fromisoformat(cooldown_until_str)
                if cooldown_until.tzinfo is None:
                    cooldown_until = cooldown_until.replace(tzinfo=timezone.utc)
                if now < cooldown_until:
                    remaining = int((cooldown_until - now).total_seconds())
                    logger.info(f"Context Gate: Suppressed due to silence cooldown ({remaining}s remaining)")
                    return GateEvaluation(
                        allowed=False,
                        reason="SILENCE_COOLDOWN",
                        retry_after_seconds=max(60, remaining),
                        detail=f"Silence cooldown active until {cooldown_until.isoformat()}",
                    )
            except Exception as e:
                logger.error(f"Error parsing silence cooldown timestamp: {e}")

        # 2. Check Focus Mode
        is_focused, focus_name = self.focus_probe.check_focus_mode()
        if is_focused:
            logger.info(f"Context Gate: Suppressed due to active Focus Mode '{focus_name}'")
            return GateEvaluation(
                allowed=False,
                reason="FOCUS_MODE_ACTIVE",
                retry_after_seconds=1800,  # Re-check in 30 mins
                detail=f"Focus Mode active: {focus_name}",
            )

        # 3. Check Calendar & Routine Buffer (+45m)
        in_event, blocking_event, buffer_end = self.calendar_probe.is_in_event_or_buffer(
            now=now, buffer_minutes=self.config.event_routine_buffer_minutes
        )
        if in_event and blocking_event and buffer_end:
            remaining = int((buffer_end - now).total_seconds())
            logger.info(
                f"Context Gate: Suppressed due to calendar event '{blocking_event.title}' + buffer "
                f"(resume at {buffer_end.strftime('%H:%M')})"
            )
            return GateEvaluation(
                allowed=False,
                reason="CALENDAR_EVENT_OR_BUFFER",
                retry_after_seconds=max(60, remaining),
                detail=f"Blocked by '{blocking_event.title}' until {buffer_end.isoformat()}",
            )

        # All gates clear!
        return GateEvaluation(allowed=True, reason="AVAILABLE", retry_after_seconds=0)
