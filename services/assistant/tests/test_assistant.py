"""Comprehensive unit and integration test suite for the Proactive Executive Assistant Service."""

import asyncio
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from services.assistant.config import AssistantConfig
from services.assistant.context_gate.calendar import CalendarEvent, CalendarProbe
from services.assistant.context_gate.evaluator import ContextGateEvaluator
from services.assistant.context_gate.focus_mode import FocusModeProbe
from services.assistant.habit_bridge.logger import HabitLogger, format_habit_completed, format_habit_prompt
from services.assistant.habit_bridge.parser import HabitDefinition, HabitParser
from services.assistant.spaced_repetition.cards import format_review_completed, format_review_prompt
from services.assistant.spaced_repetition.engine import FSRSEngine
from services.assistant.storage.db import AssistantDB
from services.assistant.telegram_gateway.bot import TelegramGateway
from services.assistant.telegram_gateway.handlers import ActionDispatcher
from services.assistant.telegram_gateway.silence import AwakeSilenceWatchdog


# -----------------------------------------------------------------------------
# Storage Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_storage_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_assistant.db"
        db = AssistantDB(db_path)
        await db.connect()

        now = datetime.now(timezone.utc)
        # Test Triggers
        await db.add_trigger(
            trigger_id="t1",
            trigger_type="fsrs_review",
            target_id="card1",
            scheduled_at=now - timedelta(minutes=10),
            expires_at=now + timedelta(hours=1),
            priority=2,
        )
        await db.add_trigger(
            trigger_id="t2",
            trigger_type="habit_check",
            target_id="habit1",
            scheduled_at=now - timedelta(minutes=5),
            expires_at=now + timedelta(hours=1),
            priority=1,  # Higher priority (lower number)
        )

        pending = await db.get_pending_triggers(now)
        assert len(pending) == 2
        # Priority 1 must come first
        assert pending[0]["id"] == "t2"
        assert pending[1]["id"] == "t1"

        # Test Reschedule
        future = now + timedelta(hours=2)
        await db.reschedule_trigger("t1", future)
        pending = await db.get_pending_triggers(now)
        assert len(pending) == 1
        assert pending[0]["id"] == "t2"

        # Test delay pending triggers except
        await db.reschedule_trigger("t1", now - timedelta(minutes=5))
        delayed = await db.delay_pending_triggers_except("t2", delay_minutes=30)
        assert delayed == 1
        pending_after_delay = await db.get_pending_triggers(now)
        assert len(pending_after_delay) == 1
        assert pending_after_delay[0]["id"] == "t2"

        # Test FSRS Cards
        await db.add_or_update_card(
            card_id="card1",
            deck_type="cold_storage",
            prompt="What is Bayes Theorem?",
            answer="P(A|B) = P(B|A)P(A)/P(B)",
            elaboration="Fundamental formula for probabilistic inference.",
            stability=2.5,
            difficulty=3.0,
            reps=1,
            lapses=0,
            state=1,
            due_at=now - timedelta(minutes=1),
        )
        card = await db.get_card("card1")
        assert card is not None
        assert card["prompt"] == "What is Bayes Theorem?"

        due_cards = await db.get_due_cards(now)
        assert len(due_cards) == 1

        # Test User Dynamics Key-Value
        await db.set_dynamic("test_key", "test_val")
        val = await db.get_dynamic("test_key")
        assert val == "test_val"

        await db.close()


# -----------------------------------------------------------------------------
# FSRS Engine Tests
# -----------------------------------------------------------------------------
def test_fsrs_engine():
    config = AssistantConfig(retention_cold_storage=0.90, retention_baby_facts=0.85)
    engine = FSRSEngine(config)

    now = datetime.now(timezone.utc)
    card_dict = engine.create_new_card(
        prompt="Explain attention mechanism",
        answer="Weighted sum of values based on query-key similarity",
        elaboration="Introduced in Vaswani et al. 2017 Transformer paper",
        deck_type="cold_storage",
    )

    # Initial rating: Good (3)
    updated, log = engine.review(card_dict, rating_val=3, review_time=now)
    assert updated["reps"] == 1
    assert updated["stability"] > 0
    assert updated["due_at"] > now
    assert log["rating"] == 3
    assert log["scheduled_days"] >= 0

    # Second rating: Easy (4)
    now_later = now + timedelta(days=1)
    updated2, log2 = engine.review(updated, rating_val=4, review_time=now_later)
    assert updated2["reps"] >= 1
    assert updated2["stability"] >= updated["stability"]


# -----------------------------------------------------------------------------
# Habit Bridge Tests
# -----------------------------------------------------------------------------
def test_habit_bridge():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        def_dir = vault / "habits" / "definitions"
        log_dir = vault / "habits" / "logs"
        def_dir.mkdir(parents=True)

        # Write sample habit definition
        habit_file = def_dir / "Read 30 Mins.md"
        habit_file.write_text(
            "---\n"
            "type: habit\n"
            "category: Mind\n"
            "frequency: daily\n"
            "target_days: 5\n"
            "emergency_version: Read 2 pages\n"
            "---\n"
            "# Read 30 Mins\n\n"
            "Daily non-fiction reading habit.\n",
            encoding="utf-8",
        )

        parser = HabitParser(def_dir)
        habits = parser.get_all_habits()
        assert len(habits) == 1
        assert habits[0].name == "Read 30 Mins"
        assert habits[0].category == "Mind"
        assert habits[0].emergency_version == "Read 2 pages"

        logger = HabitLogger(log_dir)
        test_time = datetime(2026, 9, 13, 14, 15)
        log_file = logger.log_completion("Read 30 Mins", variant="emergency", timestamp=test_time)

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "[[Read 30 Mins]]" in content
        assert "[[habits/definitions/Read 30 Mins|Read 30 Mins]] (emergency) @ 14:15" in content


# -----------------------------------------------------------------------------
# Context Gate Evaluator Tests
# -----------------------------------------------------------------------------
class MockCalendarProbe(CalendarProbe):
    def __init__(self, in_event=False, event_title="Class"):
        super().__init__()
        self.in_event = in_event
        self.event_title = event_title

    def is_in_event_or_buffer(self, now=None, buffer_minutes=45):
        if self.in_event:
            now_dt = now or datetime.now(timezone.utc)
            ev = CalendarEvent(
                title=self.event_title,
                start=now_dt - timedelta(minutes=30),
                end=now_dt + timedelta(minutes=30),
                is_all_day=False,
            )
            buffer_end = ev.end + timedelta(minutes=buffer_minutes)
            return True, ev, buffer_end
        return False, None, None


class MockFocusProbe(FocusModeProbe):
    def __init__(self, is_focused=False, focus_name=None):
        super().__init__()
        self.is_focused = is_focused
        self.focus_name = focus_name

    def check_focus_mode(self):
        return self.is_focused, self.focus_name


@pytest.mark.asyncio
async def test_context_gate_evaluator():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_gate.db"
        db = AssistantDB(db_path)
        await db.connect()

        config = AssistantConfig()
        now = datetime.now(timezone.utc)

        # 1. Gate is clear
        evaluator = ContextGateEvaluator(
            config, db, MockCalendarProbe(in_event=False), MockFocusProbe(is_focused=False)
        )
        gate = await evaluator.evaluate(now)
        assert gate.allowed is True

        # 2. Blocked by Focus Mode
        evaluator_focus = ContextGateEvaluator(
            config, db, MockCalendarProbe(in_event=False), MockFocusProbe(is_focused=True, focus_name="Do Not Disturb")
        )
        gate_focus = await evaluator_focus.evaluate(now)
        assert gate_focus.allowed is False
        assert gate_focus.reason == "FOCUS_MODE_ACTIVE"

        # 3. Blocked by Calendar + Routine Buffer
        evaluator_cal = ContextGateEvaluator(
            config, db, MockCalendarProbe(in_event=True, event_title="CMPUT 466"), MockFocusProbe(is_focused=False)
        )
        gate_cal = await evaluator_cal.evaluate(now)
        assert gate_cal.allowed is False
        assert gate_cal.reason == "CALENDAR_EVENT_OR_BUFFER"

        # 4. Blocked by Silence Cooldown
        await db.set_dynamic(
            "silence_cooldown_until", (now + timedelta(hours=1)).isoformat()
        )
        evaluator_silence = ContextGateEvaluator(
            config, db, MockCalendarProbe(in_event=False), MockFocusProbe(is_focused=False)
        )
        gate_silence = await evaluator_silence.evaluate(now)
        assert gate_silence.allowed is False
        assert gate_silence.reason == "SILENCE_COOLDOWN"

        await db.close()


# -----------------------------------------------------------------------------
# Silence Watchdog & Sleep Recovery Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_awake_silence_watchdog():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_silence.db"
        db = AssistantDB(db_path)
        await db.connect()

        config = AssistantConfig(silence_timeout_seconds=2700, silence_cooldown_seconds=7200, dry_run=True)
        gateway = TelegramGateway(config)
        watchdog = AwakeSilenceWatchdog(config, db, gateway)

        now = datetime.now(timezone.utc)
        await db.record_outbound_signal(
            message_id=101,
            chat_id=12345,
            trigger_id="trig1",
            sent_at=now,
            timeout_at=now + timedelta(seconds=2700),
            status="AWAITING_INPUT",
        )

        # Tick with small awake duration (10s): should not expire
        expired = await watchdog.tick(awake_seconds_delta=10.0, current_time=now)
        assert expired == 0
        signals = await db.get_awaiting_signals()
        assert len(signals) == 1
        assert signals[0]["awake_seconds_accumulated"] == 10.0

        # Tick with remaining duration reaching 2700s: should expire and mute
        expired = await watchdog.tick(awake_seconds_delta=2695.0, current_time=now)
        assert expired == 1
        signals = await db.get_awaiting_signals()
        assert len(signals) == 0

        # Verify cooldown was stored in user dynamics
        cooldown = await db.get_dynamic("silence_cooldown_until")
        assert cooldown is not None

        await db.close()


# -----------------------------------------------------------------------------
# End-to-End Action Dispatcher Test
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_end_to_end_action_dispatcher():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        db = AssistantDB(root / "assistant.db")
        await db.connect()

        def_dir = root / "habits" / "definitions"
        log_dir = root / "habits" / "logs"
        def_dir.mkdir(parents=True)
        (def_dir / "Workout.md").write_text(
            "---\ntype: habit\ncategory: Health\nfrequency: daily\ntarget_days: 4\nemergency_version: 10 pushups\n---\n# Workout\n",
            encoding="utf-8",
        )

        config = AssistantConfig(obsidian_vault_path=root, dry_run=True)
        engine = FSRSEngine(config)
        logger = HabitLogger(log_dir)
        gateway = TelegramGateway(config)
        dispatcher = ActionDispatcher(db, engine, logger, gateway)

        now = datetime.now(timezone.utc)

        # 1. Test FSRS Dispatch
        await db.add_or_update_card(
            card_id="c99",
            deck_type="cold_storage",
            prompt="What is gradient descent?",
            answer="Optimization algorithm iteratively moving towards the minimum of the loss function.",
            elaboration="Step size governed by learning rate.",
            stability=1.0,
            difficulty=2.0,
            reps=0,
            lapses=0,
            state=0,
            due_at=now,
        )
        await db.record_outbound_signal(
            message_id=201,
            chat_id=999,
            trigger_id="trig_fsrs",
            sent_at=now,
            timeout_at=now + timedelta(minutes=45),
        )

        # Simulate user tapping "Good" button (rating=3)
        ok = await dispatcher.handle_callback_str("fsrs:c99:3", chat_id=999, message_id=201)
        assert ok is True
        card = await db.get_card("c99")
        assert card["reps"] == 1
        assert card["stability"] > 1.0

        # Outbound signal resolved
        signals = await db.get_awaiting_signals()
        assert len(signals) == 0

        # 2. Test Habit Dispatch
        await db.record_outbound_signal(
            message_id=202,
            chat_id=999,
            trigger_id="trig_habit",
            sent_at=now,
            timeout_at=now + timedelta(minutes=45),
        )
        ok_habit = await dispatcher.handle_callback_str("habit:Workout:emergency", chat_id=999, message_id=202)
        assert ok_habit is True

        today_log = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        assert today_log.exists()
        await db.close()


# -----------------------------------------------------------------------------
# Sleep Recovery Mode Test
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sleep_recovery_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        db = AssistantDB(root / "assistant.db")
        await db.connect()

        # Simulate sleep: Mac was asleep for 6 hours
        # During this time:
        # Trigger 1 had TTL 1 hour -> expired during sleep
        # Trigger 2 (priority 1) is valid and pending
        # Trigger 3 (priority 5) is valid and pending
        sleep_time = datetime(2026, 9, 13, 10, 0, tzinfo=timezone.utc)
        wake_time = sleep_time + timedelta(hours=6)

        await db.add_trigger(
            trigger_id="trig_expired",
            trigger_type="fsrs_review",
            target_id="card_old",
            scheduled_at=sleep_time + timedelta(minutes=30),
            expires_at=sleep_time + timedelta(hours=1),
            priority=5,
        )
        await db.add_trigger(
            trigger_id="trig_urgent",
            trigger_type="habit_check",
            target_id="HabitUrgent",
            scheduled_at=sleep_time + timedelta(hours=2),
            expires_at=wake_time + timedelta(hours=2),
            priority=1,
        )
        await db.add_trigger(
            trigger_id="trig_low_pri",
            trigger_type="fsrs_review",
            target_id="card_low",
            scheduled_at=sleep_time + timedelta(hours=3),
            expires_at=wake_time + timedelta(hours=2),
            priority=5,
        )

        # 1. Expire stale triggers on wake
        expired_count = await db.expire_stale_triggers(wake_time)
        assert expired_count == 1

        # 2. Inspect pending triggers on wake
        pending = await db.get_pending_triggers(wake_time)
        assert len(pending) == 2
        assert pending[0]["id"] == "trig_urgent"

        # 3. Anti-avalanche: delay all except highest priority item by +30m
        delayed_count = await db.delay_pending_triggers_except(pending[0]["id"], delay_minutes=30)
        assert delayed_count == 1

        # After anti-avalanche delay, only the single highest priority item is immediately pending
        pending_immediately = await db.get_pending_triggers(wake_time)
        assert len(pending_immediately) == 1
        assert pending_immediately[0]["id"] == "trig_urgent"

        await db.close()
