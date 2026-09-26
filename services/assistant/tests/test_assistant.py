"""Comprehensive unit and integration test suite for the Proactive Executive Assistant Service."""

import asyncio
import json
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
        gateway._dry_run_messages[101] = {
            "chat_id": 12345,
            "text": "Take a moment to check in.",
            "keyboard": [[{"text": "Done", "callback_data": "done"}]],
            "status": "SENT",
        }
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
        assert gateway._dry_run_messages[101]["text"] == "Take a moment to check in."
        assert gateway._dry_run_messages[101]["keyboard"] == []

        # Verify cooldown was stored in user dynamics
        cooldown = await db.get_dynamic("silence_cooldown_until")
        assert cooldown is not None

        await db.close()


@pytest.mark.asyncio
async def test_awake_silence_watchdog_unlimited_checkin():
    """The default check-in policy keeps the Telegram action available indefinitely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = AssistantDB(Path(tmpdir) / "test_unlimited_silence.db")
        await db.connect()

        config = AssistantConfig(silence_timeout_seconds=0, dry_run=True)
        gateway = TelegramGateway(config)
        gateway._dry_run_messages[102] = {
            "chat_id": 12345,
            "text": "Take a moment to check in.",
            "keyboard": [[{"text": "Done", "callback_data": "done"}]],
            "status": "SENT",
        }
        watchdog = AwakeSilenceWatchdog(config, db, gateway)
        now = datetime.now(timezone.utc)
        await db.record_outbound_signal(
            message_id=102,
            chat_id=12345,
            trigger_id="trig_unlimited",
            sent_at=now,
            timeout_at=now,
            status="AWAITING_INPUT",
        )

        assert await watchdog.tick(awake_seconds_delta=24 * 60 * 60, current_time=now) == 0
        assert len(await db.get_awaiting_signals()) == 1
        assert gateway._dry_run_messages[102]["keyboard"]

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

        # 3. Test 2-Step MCQ Flow (Answer selection -> Struggle rating)
        mcq_options = ["Alpha", "Beta", "Gamma", "Delta"]
        await db.add_or_update_card(
            card_id="mcq1",
            deck_type="cold_storage",
            prompt="Which letter comes first in the Greek alphabet?",
            answer="Alpha",
            elaboration="Alpha is the first letter of the Greek alphabet.",
            stability=1.0,
            difficulty=2.0,
            reps=0,
            lapses=0,
            state=0,
            due_at=now,
            options=json.dumps(mcq_options),
            correct_index=0,
        )
        card_mcq = await db.get_card("mcq1")
        prompt_text, mcq_keyboard = format_review_prompt(card_mcq)
        assert "*A)* Alpha" in prompt_text
        assert mcq_keyboard[0][0]["callback_data"] == "fsrs_pick:mcq1:0"

        # Send prompt via gateway so message exists in gateway state
        msg_id = await gateway.send_prompt(999, prompt_text, mcq_keyboard)
        assert msg_id is not None

        await db.record_outbound_signal(
            message_id=msg_id,
            chat_id=999,
            trigger_id="trig_mcq",
            sent_at=now,
            timeout_at=now + timedelta(minutes=45),
        )

        # Step 1: User picks option A (correct)
        pick_ok = await dispatcher.handle_callback_str("fsrs_pick:mcq1:0", chat_id=999, message_id=msg_id)
        assert pick_ok is True
        # Verify message was updated with struggle buttons
        dry_msg = gateway._dry_run_messages[msg_id]
        assert "🎯 *Correct!*" in dry_msg["text"]
        assert dry_msg["keyboard"][0][0]["callback_data"] == "fsrs_rate:mcq1:4"

        # Step 2: User rates struggle (e.g. Confident / Good = 3)
        rate_ok = await dispatcher.handle_callback_str("fsrs_rate:mcq1:3", chat_id=999, message_id=msg_id)
        assert rate_ok is True
        updated_mcq = await db.get_card("mcq1")
        assert updated_mcq["reps"] == 1
        assert "✅ *Recall Logged*" in gateway._dry_run_messages[msg_id]["text"]
        assert gateway._dry_run_messages[msg_id]["keyboard"] == []

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

        await db.close()


# -----------------------------------------------------------------------------
# Text Messages, Active Prompt Replies & Commands Test
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_text_messages_and_commands():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        db_path = root / "assistant.db"
        vault_path = root / "vault"
        vault_path.mkdir(parents=True)
        (vault_path / "habits" / "definitions").mkdir(parents=True)
        (vault_path / "habits" / "logs").mkdir(parents=True)

        config = AssistantConfig(
            db_path=db_path,
            obsidian_vault_path=vault_path,
            telegram_bot_token="TEST_TOKEN",
            dry_run=True,
        )
        db = AssistantDB(db_path)
        await db.connect()
        fsrs = FSRSEngine(config)
        gateway = TelegramGateway(config)
        habit_logger = HabitLogger(vault_path / "habits" / "logs")
        dispatcher = ActionDispatcher(db, fsrs, habit_logger, gateway, config=config)

        # 1. Test /help and /status commands
        assert await dispatcher.cmd_help(chat_id=888) is True
        assert len(gateway._dry_run_messages) > 0

        assert await dispatcher.cmd_status(chat_id=888) is True

        # 2. Test /note and quick capture
        assert await dispatcher.cmd_capture("Buy green tea", chat_id=888) is True
        capture_file = vault_path / "Inbox" / "Quick Capture.md"
        assert capture_file.exists()
        assert "Buy green tea" in capture_file.read_text()

        # 3. Test Text Reply to Active MCQ Prompt
        mcq_options = ["London", "Paris", "Berlin", "Tokyo"]
        now = datetime.now(timezone.utc)
        await db.add_or_update_card(
            card_id="geo1",
            deck_type="cold_storage",
            prompt="What is the capital of France?",
            answer="Paris",
            elaboration="Paris is located on the river Seine.",
            stability=1.0,
            difficulty=2.0,
            reps=0,
            lapses=0,
            state=0,
            due_at=now,
            options=json.dumps(mcq_options),
            correct_index=1,
        )

        # Dispatch quiz card
        assert await dispatcher.cmd_quiz(chat_id=888) is True
        signals = await db.get_awaiting_signals()
        assert len(signals) == 1
        msg_id = signals[0]["message_id"]

        # Simulate user replying with text "B" (picking Paris)
        handled_pick = await dispatcher.handle_text_message("B", chat_id=888, message_id=999)
        assert handled_pick is True
        assert "🎯 *Correct!*" in gateway._dry_run_messages[msg_id]["text"]

        # Simulate user replying with text "Confident" (rating=3)
        handled_rate = await dispatcher.handle_text_message("Confident", chat_id=888, message_id=1000)
        assert handled_rate is True
        updated_card = await db.get_card("geo1")
        assert updated_card["reps"] == 1
        assert "✅ *Recall Logged*" in gateway._dry_run_messages[msg_id]["text"]

        # 4. Test natural keywords without active prompt
        assert await dispatcher.handle_text_message("quiz", chat_id=888, message_id=1001) is True

        await db.close()


# -----------------------------------------------------------------------------
# Telegram HTML Formatter Tests
# -----------------------------------------------------------------------------
def test_telegram_html_formatter():
    from services.assistant.telegram_gateway.formatter import (
        markdown_to_telegram_html,
        split_message_chunks,
    )

    # 1. Bold, Italic, Headers, Bullets, Blockquotes
    md = (
        "# Title Header\n\n"
        "**Double Bold** and *Single Bold*.\n"
        "_Italic note_ with `inline_code_variable`.\n\n"
        "> An insightful quote\n\n"
        "- Point A\n"
        "- Point B\n\n"
        "Check [Link](https://example.com) and ~~strike~~ and ||spoiler||."
    )
    res = markdown_to_telegram_html(md)
    assert "<b>Title Header</b>" in res
    assert "<b>Double Bold</b>" in res
    assert "<b>Single Bold</b>" in res
    assert "<i>Italic note</i>" in res
    assert "<code>inline_code_variable</code>" in res
    assert "<blockquote>An insightful quote</blockquote>" in res
    assert "• Point A" in res
    assert '<a href="https://example.com">Link</a>' in res
    assert "<s>strike</s>" in res
    assert "<tg-spoiler>spoiler</tg-spoiler>" in res

    # 2. Safety: special characters (<, >, &) outside formatting
    raw_math = "If x < 5 and y > 10 & z != 0: `test <code & tag>`"
    res_math = markdown_to_telegram_html(raw_math)
    assert "&lt;" in res_math
    assert "&gt;" in res_math
    assert "&amp;" in res_math
    assert "<code>test &lt;code &amp; tag&gt;</code>" in res_math

    # 3. Code block with language highlighting
    fenced = "```python\ndef test():\n    return 42\n```"
    res_fenced = markdown_to_telegram_html(fenced)
    assert '<pre><code class="language-python">def test():\n    return 42\n</code></pre>' in res_fenced

    # 4. snake_case should NOT be converted to italics
    snake = "variable_name_with_multiple_underscores"
    res_snake = markdown_to_telegram_html(snake)
    assert res_snake == "variable_name_with_multiple_underscores"
    assert "<i>" not in res_snake

    # 5. Italic wrapping inline code
    italic_code = "_Location: `Inbox/Quick Capture.md`_"
    res_ic = markdown_to_telegram_html(italic_code)
    assert res_ic == "<i>Location: <code>Inbox/Quick Capture.md</code></i>"

    # 6. Markdown Table conversion to Telegram Vertical Cards
    table_md = (
        "| Role | Officeholder | Function |\n"
        "| :--- | :--- | :--- |\n"
        "| Head of State | King Charles III | Sovereign and constitutional monarch |\n"
        "| Head of Government | Andrew Holness | Prime Minister |"
    )
    res_table = markdown_to_telegram_html(table_md)
    assert "<b>Head of State</b>" in res_table
    assert "• <b>Officeholder:</b> King Charles III" in res_table
    assert "• <b>Function:</b> Sovereign and constitutional monarch" in res_table
    assert "<b>Head of Government</b>" in res_table
    assert "• <b>Officeholder:</b> Andrew Holness" in res_table
    assert "• <b>Function:</b> Prime Minister" in res_table

    # 7. Message chunking
    long_text = ("This is a paragraph.\n\n" * 250)
    chunks = split_message_chunks(long_text, max_chars=4000)
    assert len(chunks) > 1
    assert all(len(c) <= 4000 for c in chunks)


@pytest.mark.asyncio
async def test_morning_briefing_builder_and_gratitude():
    from services.assistant.briefing.engine import MorningBriefingBuilder
    from services.assistant.briefing.gratitude import record_gratitude
    from services.assistant.context_gate.calendar import CalendarEvent

    # 1. Builder formatting test
    test_date = datetime(2026, 9, 18, 8, 30)
    builder = MorningBriefingBuilder(date=test_date)
    ev = CalendarEvent(
        title="MUSIC 102 Lecture",
        start=datetime(2026, 9, 18, 14, 0),
        end=datetime(2026, 9, 18, 15, 20),
        is_all_day=False,
    )
    text, keyboard = builder.build_prompt(due_cards_count=4, calendar_events=[ev])

    assert "Morning Grounding & Briefing" in text
    assert "Friday, September 18" in text
    assert "60-Second Mindful Centering" in text
    assert "Daily Gratitude" not in text
    assert "4 cards" in text
    assert "MUSIC 102 Lecture" in text
    assert "2:00 PM – 3:20 PM" in text

    # Check keyboard rows
    assert len(keyboard) == 1
    assert keyboard[0][0]["callback_data"] == "briefing:meditate_done"

    # 2. Gratitude Logging to Vault test
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        log_path = record_gratitude(vault, "The morning sunlight through the window", timestamp=test_date)
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert "## Gratitude" in content
        assert "[08:30] The morning sunlight through the window" in content

        # Append second gratitude note
        record_gratitude(vault, "A hot cup of pour-over coffee", timestamp=datetime(2026, 9, 18, 8, 45))
        content2 = log_path.read_text(encoding="utf-8")
        assert "[08:30] The morning sunlight through the window" in content2
        assert "[08:45] A hot cup of pour-over coffee" in content2


@pytest.mark.asyncio
async def test_morning_briefing_dispatch_and_callbacks():
    from services.assistant.briefing.engine import MorningBriefingBuilder
    from services.assistant.run import AssistantDaemon

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir) / "vault"
        db_path = Path(tmpdir) / "test.db"
        cfg = AssistantConfig(
            db_path=db_path,
            obsidian_vault_path=vault,
            dry_run=True,
            telegram_chat_id=12345,
            telegram_bot_token="TEST_TOKEN",
        )
        daemon = AssistantDaemon(config=cfg)
        await daemon.db.connect()

        # 1. Test automatic daily briefing queueing
        now_utc = datetime(2026, 9, 18, 7, 0, tzinfo=timezone.utc)
        await daemon._ensure_daily_morning_briefing(now_utc)
        today_trig = await daemon.db.get_trigger("trig_morning_2026-09-18")
        assert today_trig is not None
        assert today_trig["trigger_type"] == "morning_briefing"
        assert today_trig["priority"] == 1

        # 2. Test manual command /morning
        await daemon.dispatcher.cmd_morning(chat_id=12345)
        signals = await daemon.db.get_awaiting_signals()
        assert len(signals) == 1
        assert signals[0]["trigger_id"] == "trig_morning_manual"

        # 3. Completion chatter cannot be saved as gratitude before centering is done.
        await daemon.dispatcher.handle_text_message("done centering, give me the cards", 12345, 999)
        today_log = vault / "habits" / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        assert not today_log.exists()

        # 4. Centering advances to gratitude without resolving the check-in.
        success = await daemon.dispatcher.handle_callback_str("briefing:meditate_done", 12345, signals[0]["message_id"])
        assert success is True
        active = await daemon.db.get_awaiting_signals()
        assert len(active) == 1
        assert "Daily Gratitude" in daemon.gateway._dry_run_messages[signals[0]["message_id"]]["text"]

        # 5. Only the gratitude stage journals a direct text reply, then exposes
        # the fresh review step instead of silently ending the morning flow.
        await daemon.dispatcher.handle_text_message("I am grateful for high-bandwidth thinking", 12345, 999)
        today_log = vault / "habits" / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        assert today_log.exists()
        assert "high-bandwidth thinking" in today_log.read_text(encoding="utf-8")
        prompt = daemon.gateway._dry_run_messages[signals[0]["message_id"]]
        assert "Spaced-Repetition Review" in prompt["text"]
        assert prompt["keyboard"][0][0]["callback_data"] == "briefing:review"

        await daemon.db.close()


# -----------------------------------------------------------------------------
# Telegram Vertical Card & Formatter Tests
# -----------------------------------------------------------------------------
def test_vertical_card_formatting():
    from services.assistant.telegram_gateway.formatter import format_vertical_card_table

    # 2-column key-value
    kv_rows = [
        ["Property", "Value"],
        ["CPU", "M4 Pro"],
        ["Memory", "48GB"],
    ]
    kv_res = format_vertical_card_table(kv_rows)
    assert "• <b>CPU:</b> M4 Pro" in kv_res
    assert "• <b>Memory:</b> 48GB" in kv_res

    # 3-column entity cards
    entity_rows = [
        ["Service", "Port", "Status"],
        ["aios-assistant", "None", "Active"],
        ["aios-server", "3031", "Active"],
    ]
    entity_res = format_vertical_card_table(entity_rows)
    assert "<b>aios-assistant</b>" in entity_res
    assert "• <b>Port:</b> None" in entity_res
    assert "• <b>Status:</b> Active" in entity_res
    assert "<b>aios-server</b>" in entity_res
    assert "• <b>Port:</b> 3031" in entity_res


def test_clean_hermes_output_utility():
    from services.assistant.telegram_gateway.handlers import clean_hermes_output

    sample_output = (
        "Warning: Unknown toolsets: moa\n"
        "Here is the answer to your question, Matt.\n\n"
        "**Thread Metrics:** ~180k tokens\n"
        "session_id: 20260919_130000_123456\n"
    )
    cleaned = clean_hermes_output(sample_output)
    assert cleaned == "Here is the answer to your question, Matt."

    # Test with reasoning block
    reasoning_output = (
        "Warning: Unknown toolsets: moa\n"
        "┌─ Reasoning ──────────────────────────────────────────────────────────────────┐\n"
        "Internal thought process...\n"
        "└──────────────────────────────────────────────────────────────────────────────┘\n"
        "Direct final answer.\n"
        "session_id: 20260919_130000_123456\n"
    )
    cleaned_reasoning = clean_hermes_output(reasoning_output)
    assert cleaned_reasoning == "Direct final answer."


@pytest.mark.asyncio
async def test_multimodal_media_handlers_dispatch():
    from unittest.mock import AsyncMock, patch
    from services.assistant.telegram_gateway.handlers import ActionDispatcher

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir) / "vault"
        db_path = Path(tmpdir) / "test.db"
        media_dir = Path(tmpdir) / "media"
        media_dir.mkdir(parents=True)

        cfg = AssistantConfig(
            db_path=db_path,
            obsidian_vault_path=vault,
            dry_run=True,
            telegram_chat_id=12345,
            telegram_bot_token="TEST_TOKEN",
            media_tmp_dir=media_dir,
            groq_api_key="gsk_test",
        )
        db = AssistantDB(db_path)
        assert cfg.codex_command.endswith("/codex")
        await db.connect()
        gateway = TelegramGateway(cfg)
        dispatcher = ActionDispatcher(db, FSRSEngine(cfg), HabitLogger(vault), gateway, config=cfg)

        # 1. Photo Message Handler
        test_photo = media_dir / "test_photo.jpg"
        test_photo.write_bytes(b"dummy image")
        with patch.object(dispatcher, "_query_model", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "This is a screenshot of the Telegram bot conversation."
            handled = await dispatcher.handle_photo_message(
                photo_path=test_photo,
                caption="What is this?",
                chat_id=12345,
                message_id=101,
            )
            assert handled is True
            mock_query.assert_awaited_once()

        # 2. Audio Message Handler (Transcribe -> Query)
        test_audio = media_dir / "voice.ogg"
        test_audio.write_bytes(b"dummy audio")
        with patch("services.assistant.telegram_gateway.handlers.transcribe_audio_file", new_callable=AsyncMock) as mock_transcribe:
            mock_transcribe.return_value = "What is the capital of Alberta?"
            with patch.object(dispatcher, "_query_model", new_callable=AsyncMock) as mock_query:
                mock_query.return_value = "The capital of Alberta is Edmonton."
                handled = await dispatcher.handle_audio_message(
                    audio_path=test_audio,
                    chat_id=12345,
                    message_id=102,
                )
                assert handled is True
                mock_transcribe.assert_awaited_once()
                mock_query.assert_awaited_once()

        # 3. Document Message Handler (Code text routing)
        test_code_doc = media_dir / "script.py"
        test_code_doc.write_text("print('hello world')", encoding="utf-8")
        with patch.object(dispatcher, "_query_model", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "This script prints hello world."
            handled = await dispatcher.handle_document_message(
                doc_path=test_code_doc,
                file_name="script.py",
                mime_type="text/x-python",
                caption="Explain this script",
                chat_id=12345,
                message_id=103,
            )
            assert handled is True
            mock_query.assert_awaited_once()

        # 4. Engine Command reports the fixed direct-Codex route.
        assert await dispatcher.cmd_engine("codex", chat_id=12345) is True
        assert await dispatcher.cmd_engine("agy", chat_id=12345) is True

        await db.close()


def test_clean_agy_output_utility():
    from services.assistant.telegram_gateway.handlers import clean_agy_output

    sample_agy = (
        "Here is the breakdown of your project, Matt.\n"
        "• Task A is complete.\n\n"
        "***\n\n"
        "Conversation artifact: [thread.md](file:///Users/matt/.gemini/antigravity-cli/brain/123/thread.md)"
    )
    cleaned = clean_agy_output(sample_agy)
    assert "Here is the breakdown of your project, Matt." in cleaned
    assert "• Task A is complete." in cleaned
    assert "thread.md" not in cleaned
    assert "***" not in cleaned


@pytest.mark.asyncio
async def test_telegram_attachment_methods():
    """Validates that TelegramGateway delivers audio, voice, photo, video, and documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cfg = AssistantConfig(
            dry_run=True,
            telegram_chat_id=12345,
            telegram_bot_token="TEST_TOKEN",
        )
        gateway = TelegramGateway(cfg)

        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"dummy mp3 data")
        voice_file = tmp_path / "voice.ogg"
        voice_file.write_bytes(b"dummy ogg voice data")
        photo_file = tmp_path / "photo.png"
        photo_file.write_bytes(b"dummy png data")
        video_file = tmp_path / "video.mp4"
        video_file.write_bytes(b"dummy mp4 data")
        doc_file = tmp_path / "notes.pdf"
        doc_file.write_bytes(b"dummy pdf data")

        # Test discrete send methods
        m1 = await gateway.send_audio(12345, audio_file, caption="Meditation audio", title="Morning Mindfulness")
        assert m1 is not None
        assert gateway._dry_run_messages[m1]["type"] == "audio"
        assert gateway._dry_run_messages[m1]["title"] == "Morning Mindfulness"

        m2 = await gateway.send_voice(12345, voice_file, caption="Voice memo")
        assert m2 is not None
        assert gateway._dry_run_messages[m2]["type"] == "voice"

        m3 = await gateway.send_photo(12345, photo_file, caption="Chart photo")
        assert m3 is not None
        assert gateway._dry_run_messages[m3]["type"] == "photo"

        m4 = await gateway.send_video(12345, video_file, caption="Video preview")
        assert m4 is not None
        assert gateway._dry_run_messages[m4]["type"] == "video"

        m5 = await gateway.send_document(12345, doc_file, caption="Exported document")
        assert m5 is not None
        assert gateway._dry_run_messages[m5]["type"] == "document"

        # Test unified send_media auto-classification
        m_audio = await gateway.send_media(12345, audio_file)
        assert gateway._dry_run_messages[m_audio]["type"] == "audio"

        m_voice = await gateway.send_media(12345, voice_file)
        assert gateway._dry_run_messages[m_voice]["type"] == "voice"

        m_photo = await gateway.send_media(12345, photo_file)
        assert gateway._dry_run_messages[m_photo]["type"] == "photo"

        m_video = await gateway.send_media(12345, video_file)
        assert gateway._dry_run_messages[m_video]["type"] == "video"

        m_doc = await gateway.send_media(12345, doc_file)
        assert gateway._dry_run_messages[m_doc]["type"] == "document"

        # Test forced document override
        m_photo_as_doc = await gateway.send_media(12345, photo_file, as_document=True)
        assert gateway._dry_run_messages[m_photo_as_doc]["type"] == "document"


@pytest.mark.asyncio
async def test_media_extraction_and_delivery():
    """Validates MEDIA: tag parsing, tool-generated session media detection, and end-to-end delivery."""
    from services.assistant.telegram_gateway.handlers import (
        extract_media_from_text,
        find_session_generated_media,
        ActionDispatcher,
    )
    from unittest.mock import AsyncMock, patch
    import sqlite3
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir).resolve()
        db_path = tmp_path / "test.db"
        media_file = tmp_path / "meditation.mp3"
        media_file.write_bytes(b"dummy mp3 data")

        # 1. Test extract_media_from_text
        raw_reply = (
            "Here is your meditation.\n\n"
            "[[audio_as_voice]]\n"
            f"MEDIA:{media_file}\n\n"
            "Enjoy the session!"
        )
        cleaned, items = extract_media_from_text(raw_reply)
        assert "Here is your meditation." in cleaned
        assert "Enjoy the session!" in cleaned
        assert "MEDIA:" not in cleaned
        assert "[[audio_as_voice]]" not in cleaned
        assert len(items) == 1
        assert items[0]["path"] == media_file
        assert items[0]["is_voice"] is True
        assert items[0]["as_document"] is False

        # 2. Test find_session_generated_media using a mock state.db
        hermes_dir = tmp_path / ".hermes"
        hermes_dir.mkdir(parents=True)
        fake_state_db = hermes_dir / "state.db"
        conn = sqlite3.connect(str(fake_state_db))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE messages (session_id TEXT, role TEXT, content TEXT)")
        tool_content = json.dumps({
            "success": True,
            "file_path": str(media_file),
            "media_tag": f"MEDIA:{media_file}",
            "voice_compatible": True,
        })
        cursor.execute(
            "INSERT INTO messages VALUES ('test_session_123', 'tool', ?)",
            (tool_content,),
        )
        conn.commit()
        conn.close()

        with patch("pathlib.Path.home", return_value=tmp_path):
            tool_items = find_session_generated_media("test_session_123")
            assert len(tool_items) >= 1
            assert any(item["path"] == media_file for item in tool_items)

        # 3. Test ActionDispatcher end-to-end model response delivery
        cfg = AssistantConfig(
            db_path=db_path,
            obsidian_vault_path=tmp_path / "vault",
            dry_run=True,
            telegram_chat_id=12345,
            telegram_bot_token="TEST_TOKEN",
        )
        db = AssistantDB(db_path)
        await db.connect()
        gateway = TelegramGateway(cfg)
        dispatcher = ActionDispatcher(db, FSRSEngine(cfg), HabitLogger(tmp_path / "vault"), gateway, config=cfg)

        with patch.object(gateway, "send_media", new_callable=AsyncMock) as mock_send_media:
            mock_send_media.return_value = 2001
            await dispatcher._deliver_model_response(
                chat_id=12345,
                model_reply=raw_reply,
                status_msg_id=1001,
            )
            mock_send_media.assert_awaited_once_with(
                chat_id=12345,
                file_path=media_file,
                is_voice=True,
                as_document=False,
            )

        # Verify clean text was saved to chat history without raw MEDIA tags
        history = await db.get_recent_chat_history(12345, limit=5)
        assert len(history) == 1
        assert history[0]["role"] == "assistant"
        assert "MEDIA:" not in history[0]["content"]
        assert "Here is your meditation." in history[0]["content"]

        await db.close()
