"""CLI management utility for Proactive Assistant (cards, habits, triggers)."""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from services.assistant.config import AssistantConfig
from services.assistant.spaced_repetition.engine import FSRSEngine
from services.assistant.storage.db import AssistantDB


async def cmd_add_card(args, config: AssistantConfig):
    db = AssistantDB(config.db_path)
    await db.connect()
    engine = FSRSEngine(config)

    card = engine.create_new_card(
        prompt=args.prompt,
        answer=args.answer,
        elaboration=args.elaboration,
        deck_type=args.deck,
    )
    await db.add_or_update_card(
        card_id=card["card_id"],
        deck_type=card["deck_type"],
        prompt=card["prompt"],
        answer=card["answer"],
        elaboration=card["elaboration"],
        stability=card["stability"],
        difficulty=card["difficulty"],
        reps=card["reps"],
        lapses=card["lapses"],
        state=card["state"],
        due_at=card["due_at"],
        options=args.options,
        correct_index=args.correct_index,
    )
    print(f"Card created successfully: ID {card['card_id']} (Deck: {card['deck_type']})")

    if args.schedule_now:
        now = datetime.now(timezone.utc)
        trig_id = f"trig_fsrs_{card['card_id']}"
        await db.add_trigger(
            trigger_id=trig_id,
            trigger_type="fsrs_review",
            target_id=card["card_id"],
            scheduled_at=now,
            expires_at=now + timedelta(hours=4),
            priority=5,
        )
        print(f"Scheduled immediate review trigger: {trig_id}")

    await db.close()


async def cmd_add_habit_check(args, config: AssistantConfig):
    db = AssistantDB(config.db_path)
    await db.connect()

    now = datetime.now(timezone.utc)
    trig_id = f"trig_habit_{args.habit.replace(' ', '_')}_{int(now.timestamp())}"
    await db.add_trigger(
        trigger_id=trig_id,
        trigger_type="habit_check",
        target_id=args.habit,
        scheduled_at=now,
        expires_at=now + timedelta(hours=6),
        priority=3,
    )
    print(f"Scheduled habit check trigger: {trig_id} for '{args.habit}'")
    await db.close()


async def cmd_status(args, config: AssistantConfig):
    db = AssistantDB(config.db_path)
    await db.connect()
    now = datetime.now(timezone.utc)

    pending = await db.get_pending_triggers(now)
    print(f"\n--- Pending Triggers ({len(pending)}) ---")
    for p in pending:
        print(f"  [{p['priority']}] {p['trigger_type']} -> {p['target_id']} (Scheduled: {p['scheduled_at']})")

    due_cards = await db.get_due_cards(now)
    print(f"\n--- Due FSRS Cards ({len(due_cards)}) ---")
    for c in due_cards:
        print(f"  [{c['card_id']}] ({c['deck_type']}) {c['prompt'][:50]}... (Due: {c['due_at']})")

    await db.close()


def main():
    parser = argparse.ArgumentParser(description="Proactive Assistant CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add Card
    p_card = subparsers.add_parser("add-card", help="Add a new FSRS card")
    p_card.add_argument("--prompt", required=True, help="Question / prompt")
    p_card.add_argument("--answer", required=True, help="Answer")
    p_card.add_argument("--elaboration", default="", help="1-sentence progressive elaboration")
    p_card.add_argument("--options", default=None, help="Pipe-separated options, e.g. 'Option A|Option B|Option C|Option D'")
    p_card.add_argument("--correct-index", type=int, default=0, help="0-based index of correct option")
    p_card.add_argument("--deck", default="cold_storage", choices=["cold_storage", "baby_facts"])
    p_card.add_argument("--schedule-now", action="store_true", help="Queue immediate review trigger")

    # Add Habit Check
    p_habit = subparsers.add_parser("add-habit-check", help="Queue a habit check trigger")
    p_habit.add_argument("--habit", required=True, help="Exact name of habit definition")

    # Status
    subparsers.add_parser("status", help="Show pending triggers and due cards")

    args = parser.parse_args()
    config = AssistantConfig()

    if args.command == "add-card":
        asyncio.run(cmd_add_card(args, config))
    elif args.command == "add-habit-check":
        asyncio.run(cmd_add_habit_check(args, config))
    elif args.command == "status":
        asyncio.run(cmd_status(args, config))


if __name__ == "__main__":
    main()
