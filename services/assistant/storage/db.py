"""SQLite storage layer for proactive assistant using aiosqlite."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiosqlite


class AssistantDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(str(self.db_path))
            self._conn.row_factory = aiosqlite.Row
            await self._create_tables()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _create_tables(self) -> None:
        assert self._conn is not None
        queries = [
            """
            CREATE TABLE IF NOT EXISTS trigger_queue (
                id TEXT PRIMARY KEY,
                trigger_type TEXT NOT NULL,          -- 'fsrs_review', 'habit_check', 'micro_step'
                target_id TEXT NOT NULL,             -- card_id, habit_id, or task_id
                scheduled_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                priority INTEGER DEFAULT 5,          -- 1 (highest) to 10 (lowest)
                status TEXT DEFAULT 'PENDING',       -- 'PENDING', 'FIRED', 'SUPPRESSED', 'EXPIRED'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS fsrs_cards (
                card_id TEXT PRIMARY KEY,
                deck_type TEXT NOT NULL,             -- 'cold_storage' (coursework), 'baby_facts' (trivia)
                prompt TEXT NOT NULL,
                answer TEXT NOT NULL,
                elaboration TEXT NOT NULL,           -- 1-sentence novel context / application
                options TEXT,                        -- JSON string array of multiple choice options
                correct_index INTEGER DEFAULT 0,     -- Index of the correct choice
                stability REAL NOT NULL,
                difficulty REAL NOT NULL,
                reps INTEGER NOT NULL,
                lapses INTEGER NOT NULL,
                state INTEGER NOT NULL,              -- 0=New, 1=Learning, 2=Review, 3=Relearning
                last_review TIMESTAMP,
                due_at TIMESTAMP NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS fsrs_logs (
                log_id TEXT PRIMARY KEY,
                card_id TEXT NOT NULL,
                rating INTEGER NOT NULL,             -- 1=Again, 2=Hard, 3=Good, 4=Easy
                review_time TIMESTAMP NOT NULL,
                scheduled_days REAL NOT NULL,
                FOREIGN KEY (card_id) REFERENCES fsrs_cards(card_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS outbound_signals (
                message_id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                trigger_id TEXT NOT NULL,
                sent_at TIMESTAMP NOT NULL,
                timeout_at TIMESTAMP NOT NULL,
                awake_seconds_accumulated REAL DEFAULT 0, -- Prevents sleep from triggering false timeouts
                status TEXT DEFAULT 'AWAITING_INPUT',    -- 'RESPONDED', 'SILENT_TIMEOUT', 'DISMISSED'
                FOREIGN KEY (trigger_id) REFERENCES trigger_queue(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS user_dynamics (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        for q in queries:
            await self._conn.execute(q)
        
        # Migrations for existing databases
        try:
            await self._conn.execute("ALTER TABLE fsrs_cards ADD COLUMN options TEXT")
        except Exception:
            pass
        try:
            await self._conn.execute("ALTER TABLE fsrs_cards ADD COLUMN correct_index INTEGER DEFAULT 0")
        except Exception:
            pass
        await self._conn.commit()

    # -------------------------------------------------------------------------
    # Triggers
    # -------------------------------------------------------------------------
    async def add_trigger(
        self,
        trigger_id: str,
        trigger_type: str,
        target_id: str,
        scheduled_at: datetime,
        expires_at: datetime,
        priority: int = 5,
        status: str = "PENDING",
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO trigger_queue (id, trigger_type, target_id, scheduled_at, expires_at, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                trigger_type=excluded.trigger_type,
                target_id=excluded.target_id,
                scheduled_at=excluded.scheduled_at,
                expires_at=excluded.expires_at,
                priority=excluded.priority,
                status=excluded.status
            """,
            (
                trigger_id,
                trigger_type,
                target_id,
                scheduled_at.isoformat(),
                expires_at.isoformat(),
                priority,
                status,
            ),
        )
        await self._conn.commit()

    async def get_pending_triggers(self, current_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        assert self._conn is not None
        now_str = (current_time or datetime.now(timezone.utc)).isoformat()
        cursor = await self._conn.execute(
            """
            SELECT * FROM trigger_queue
            WHERE status = 'PENDING' AND scheduled_at <= ? AND expires_at >= ?
            ORDER BY priority ASC, scheduled_at ASC
            """,
            (now_str, now_str),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def update_trigger_status(self, trigger_id: str, status: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "UPDATE trigger_queue SET status = ? WHERE id = ?",
            (status, trigger_id),
        )
        await self._conn.commit()

    async def reschedule_trigger(
        self, trigger_id: str, new_scheduled_at: datetime, new_expires_at: Optional[datetime] = None
    ) -> None:
        assert self._conn is not None
        if new_expires_at:
            await self._conn.execute(
                "UPDATE trigger_queue SET scheduled_at = ?, expires_at = ?, status = 'PENDING' WHERE id = ?",
                (new_scheduled_at.isoformat(), new_expires_at.isoformat(), trigger_id),
            )
        else:
            await self._conn.execute(
                "UPDATE trigger_queue SET scheduled_at = ?, status = 'PENDING' WHERE id = ?",
                (new_scheduled_at.isoformat(), trigger_id),
            )
        await self._conn.commit()

    async def expire_stale_triggers(self, current_time: Optional[datetime] = None) -> int:
        assert self._conn is not None
        now_str = (current_time or datetime.now(timezone.utc)).isoformat()
        cursor = await self._conn.execute(
            "UPDATE trigger_queue SET status = 'EXPIRED' WHERE status = 'PENDING' AND expires_at < ?",
            (now_str,),
        )
        await self._conn.commit()
        return cursor.rowcount

    async def delay_pending_triggers_except(
        self, exclude_trigger_id: str, delay_minutes: int = 30
    ) -> int:
        assert self._conn is not None
        cursor = await self._conn.execute(
            """
            UPDATE trigger_queue
            SET scheduled_at = datetime(scheduled_at, ? || ' minutes'),
                expires_at = datetime(expires_at, ? || ' minutes')
            WHERE status = 'PENDING' AND id != ?
            """,
            (f"+{delay_minutes}", f"+{delay_minutes}", exclude_trigger_id),
        )
        await self._conn.commit()
        return cursor.rowcount

    # -------------------------------------------------------------------------
    # FSRS Cards
    # -------------------------------------------------------------------------
    async def add_or_update_card(
        self,
        card_id: str,
        deck_type: str,
        prompt: str,
        answer: str,
        elaboration: str,
        stability: float,
        difficulty: float,
        reps: int,
        lapses: int,
        state: int,
        due_at: datetime,
        last_review: Optional[datetime] = None,
        options: Optional[str] = None,
        correct_index: int = 0,
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO fsrs_cards (
                card_id, deck_type, prompt, answer, elaboration, options, correct_index,
                stability, difficulty, reps, lapses, state, last_review, due_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(card_id) DO UPDATE SET
                deck_type=excluded.deck_type,
                prompt=excluded.prompt,
                answer=excluded.answer,
                elaboration=excluded.elaboration,
                options=excluded.options,
                correct_index=excluded.correct_index,
                stability=excluded.stability,
                difficulty=excluded.difficulty,
                reps=excluded.reps,
                lapses=excluded.lapses,
                state=excluded.state,
                last_review=excluded.last_review,
                due_at=excluded.due_at
            """,
            (
                card_id,
                deck_type,
                prompt,
                answer,
                elaboration,
                options,
                correct_index,
                stability,
                difficulty,
                reps,
                lapses,
                state,
                last_review.isoformat() if last_review else None,
                due_at.isoformat(),
            ),
        )
        await self._conn.commit()

    async def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        assert self._conn is not None
        cursor = await self._conn.execute("SELECT * FROM fsrs_cards WHERE card_id = ?", (card_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def get_due_cards(
        self, current_time: Optional[datetime] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        assert self._conn is not None
        now_str = (current_time or datetime.now(timezone.utc)).isoformat()
        cursor = await self._conn.execute(
            """
            SELECT * FROM fsrs_cards
            WHERE due_at <= ?
            ORDER BY due_at ASC
            LIMIT ?
            """,
            (now_str, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def log_fsrs_review(
        self,
        log_id: str,
        card_id: str,
        rating: int,
        review_time: datetime,
        scheduled_days: float,
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO fsrs_logs (log_id, card_id, rating, review_time, scheduled_days)
            VALUES (?, ?, ?, ?, ?)
            """,
            (log_id, card_id, rating, review_time.isoformat(), scheduled_days),
        )
        await self._conn.commit()

    # -------------------------------------------------------------------------
    # Outbound Signals & Silence Tracking
    # -------------------------------------------------------------------------
    async def record_outbound_signal(
        self,
        message_id: int,
        chat_id: int,
        trigger_id: str,
        sent_at: datetime,
        timeout_at: datetime,
        status: str = "AWAITING_INPUT",
    ) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO outbound_signals (
                message_id, chat_id, trigger_id, sent_at, timeout_at, awake_seconds_accumulated, status
            ) VALUES (?, ?, ?, ?, ?, 0, ?)
            ON CONFLICT(message_id) DO UPDATE SET
                chat_id=excluded.chat_id,
                trigger_id=excluded.trigger_id,
                sent_at=excluded.sent_at,
                timeout_at=excluded.timeout_at,
                status=excluded.status
            """,
            (message_id, chat_id, trigger_id, sent_at.isoformat(), timeout_at.isoformat(), status),
        )
        await self._conn.commit()

    async def get_awaiting_signals(self) -> List[Dict[str, Any]]:
        assert self._conn is not None
        cursor = await self._conn.execute(
            "SELECT * FROM outbound_signals WHERE status = 'AWAITING_INPUT'"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def update_signal_awake_time(
        self, message_id: int, delta_awake_seconds: float
    ) -> float:
        assert self._conn is not None
        await self._conn.execute(
            """
            UPDATE outbound_signals
            SET awake_seconds_accumulated = awake_seconds_accumulated + ?
            WHERE message_id = ?
            """,
            (delta_awake_seconds, message_id),
        )
        await self._conn.commit()
        cursor = await self._conn.execute(
            "SELECT awake_seconds_accumulated FROM outbound_signals WHERE message_id = ?",
            (message_id,),
        )
        row = await cursor.fetchone()
        return float(row[0]) if row else 0.0

    async def resolve_signal(self, message_id: int, status: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            "UPDATE outbound_signals SET status = ? WHERE message_id = ?",
            (status, message_id),
        )
        await self._conn.commit()

    # -------------------------------------------------------------------------
    # User Dynamics (Key-Value Store for silence cooldowns, state, etc.)
    # -------------------------------------------------------------------------
    async def get_dynamic(self, key: str) -> Optional[str]:
        assert self._conn is not None
        cursor = await self._conn.execute("SELECT value FROM user_dynamics WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None

    async def set_dynamic(self, key: str, value: str) -> None:
        assert self._conn is not None
        await self._conn.execute(
            """
            INSERT INTO user_dynamics (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=CURRENT_TIMESTAMP
            """,
            (key, value),
        )
        await self._conn.commit()
