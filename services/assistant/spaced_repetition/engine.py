"""FSRS scheduling engine and deck partitioner."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
import uuid

import fsrs
from ..config import AssistantConfig


class FSRSEngine:
    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        # Schedulers tailored to retention goals
        self.schedulers = {
            "cold_storage": fsrs.Scheduler(desired_retention=self.config.retention_cold_storage),
            "baby_facts": fsrs.Scheduler(desired_retention=self.config.retention_baby_facts),
        }

    def _get_scheduler(self, deck_type: str) -> fsrs.Scheduler:
        return self.schedulers.get(deck_type, self.schedulers["cold_storage"])

    def create_new_card(
        self,
        prompt: str,
        answer: str,
        elaboration: str,
        deck_type: str = "cold_storage",
        card_id: Optional[str] = None,
        due_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Creates a new card record dictionary."""
        cid = card_id or str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)
        due = due_at or now

        return {
            "card_id": cid,
            "deck_type": deck_type,
            "prompt": prompt,
            "answer": answer,
            "elaboration": elaboration,
            "stability": 0.0,
            "difficulty": 0.0,
            "reps": 0,
            "lapses": 0,
            "state": 0,  # 0=New, 1=Learning, 2=Review, 3=Relearning
            "last_review": None,
            "due_at": due,
        }

    def review(
        self,
        card_dict: Dict[str, Any],
        rating_val: int,
        review_time: Optional[datetime] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Reviews a card using the appropriate FSRS scheduler.
        Args:
            card_dict: Existing card data from database
            rating_val: 1=Again, 2=Hard, 3=Good, 4=Easy
            review_time: UTC datetime of review
        Returns:
            (updated_card_dict, log_dict)
        """
        now = review_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        scheduler = self._get_scheduler(card_dict.get("deck_type", "cold_storage"))
        rating = fsrs.Rating(rating_val)

        # Build fsrs.Card instance
        fsrs_card = fsrs.Card()
        state_int = card_dict.get("state", 0)
        # Map state integer to State enum: 0=New (Learning in fsrs), 1=Learning, 2=Review, 3=Relearning
        if state_int == 2:
            fsrs_card.state = fsrs.State.Review
        elif state_int == 3:
            fsrs_card.state = fsrs.State.Relearning
        else:
            fsrs_card.state = fsrs.State.Learning

        st = card_dict.get("stability")
        fsrs_card.stability = float(st) if st and float(st) > 0 else None

        diff = card_dict.get("difficulty")
        fsrs_card.difficulty = float(diff) if diff and float(diff) > 0 else None

        reps = card_dict.get("reps", 0)
        fsrs_card.step = int(reps)

        due_val = card_dict.get("due_at")
        if isinstance(due_val, str):
            due_dt = datetime.fromisoformat(due_val)
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            fsrs_card.due = due_dt
        elif isinstance(due_val, datetime):
            if due_val.tzinfo is None:
                due_val = due_val.replace(tzinfo=timezone.utc)
            fsrs_card.due = due_val

        updated_card, review_log = scheduler.review_card(fsrs_card, rating, now)

        # Map state back to int
        new_state_int = 1
        if updated_card.state == fsrs.State.Review:
            new_state_int = 2
        elif updated_card.state == fsrs.State.Relearning:
            new_state_int = 3

        lapses = card_dict.get("lapses", 0)
        if rating_val == 1:
            lapses += 1

        total_reps = int(card_dict.get("reps", 0)) + 1

        updated_dict = dict(card_dict)
        updated_dict.update({
            "stability": updated_card.stability or 0.0,
            "difficulty": updated_card.difficulty or 0.0,
            "reps": total_reps,
            "lapses": lapses,
            "state": new_state_int,
            "last_review": now,
            "due_at": updated_card.due,
        })

        # Scheduled days delta
        scheduled_days = max(0.0, (updated_card.due - now).total_seconds() / 86400.0)

        log_dict = {
            "log_id": str(uuid.uuid4())[:8],
            "card_id": card_dict["card_id"],
            "rating": rating_val,
            "review_time": now,
            "scheduled_days": scheduled_days,
        }

        return updated_dict, log_dict
