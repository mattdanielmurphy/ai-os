"""CLI management utility for Proactive Assistant (cards, habits, triggers)."""

import argparse
import asyncio
import json
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


def load_deck(path: Path) -> tuple[dict, list[dict]]:
    """Read and validate an entire JSON deck before making any database changes."""
    deck = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(deck, dict) or not isinstance(deck.get("deck_id"), str):
        raise ValueError("Deck must be an object with a string deck_id.")
    if deck.get("deck_type", "cold_storage") not in ("cold_storage", "baby_facts"):
        raise ValueError("deck_type must be cold_storage or baby_facts.")
    cards = deck.get("cards")
    if not isinstance(cards, list) or not cards:
        raise ValueError("Deck must contain a non-empty cards array.")

    seen_ids = set()
    for position, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            raise ValueError(f"Card {position} must be an object.")
        card_id = card.get("card_id")
        if not isinstance(card_id, str) or not card_id.startswith(f"{deck['deck_id']}_"):
            raise ValueError(f"Card {position} ID must start with '{deck['deck_id']}_'.")
        if card_id in seen_ids:
            raise ValueError(f"Duplicate card ID: {card_id}")
        seen_ids.add(card_id)
        for field in ("prompt", "answer", "elaboration"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                raise ValueError(f"Card {card_id} needs a non-empty {field}.")
        options = card.get("options")
        if not isinstance(options, list) or len(options) != 4 or not all(
            isinstance(option, str) and option.strip() for option in options
        ):
            raise ValueError(f"Card {card_id} needs exactly four non-empty string options.")
        correct_index = card.get("correct_index")
        if not isinstance(correct_index, int) or isinstance(correct_index, bool) or not 0 <= correct_index < 4:
            raise ValueError(f"Card {card_id} has an invalid 0-based correct_index.")
    return deck, cards


async def cmd_import_deck(args, config: AssistantConfig):
    deck, cards = load_deck(args.path)
    if args.dry_run:
        print(f"Validated {len(cards)} cards for deck '{deck['deck_id']}' (dry run; no database changes).")
        return

    db = AssistantDB(config.db_path)
    await db.connect()
    engine = FSRSEngine(config)
    added = skipped = 0
    for item in cards:
        if await db.get_card(item["card_id"]):
            skipped += 1
            continue
        card = engine.create_new_card(
            prompt=item["prompt"],
            answer=item["answer"],
            elaboration=item["elaboration"],
            deck_type=deck.get("deck_type", "cold_storage"),
            card_id=item["card_id"],
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
            options=json.dumps(item["options"], ensure_ascii=False),
            correct_index=item["correct_index"],
        )
        added += 1
    await db.close()
    print(f"Imported {added} cards into '{deck['deck_id']}'; skipped {skipped} existing card(s) to preserve FSRS progress.")


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


async def cmd_morning_briefing(args, config: AssistantConfig):
    db = AssistantDB(config.db_path)
    await db.connect()
    now = datetime.now(timezone.utc)
    if args.now:
        scheduled_at = now
    elif args.time:
        parts = [int(p) for p in args.time.split(":")]
        now_local = datetime.now().replace(hour=parts[0], minute=parts[1], second=0, microsecond=0)
        scheduled_at = now_local.astimezone(timezone.utc)
    else:
        now_local = datetime.now().replace(
            hour=config.morning_briefing_hour,
            minute=config.morning_briefing_minute,
            second=0,
            microsecond=0,
        )
        scheduled_at = now_local.astimezone(timezone.utc)

    trig_id = f"trig_morning_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
    expires_at = scheduled_at + timedelta(hours=6)
    await db.add_trigger(
        trigger_id=trig_id,
        trigger_type="morning_briefing",
        target_id="daily_briefing",
        scheduled_at=scheduled_at,
        expires_at=expires_at,
        priority=1,
    )
    print(f"Scheduled morning briefing trigger: {trig_id} for {scheduled_at.isoformat()}")
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

    # Morning Briefing
    p_morning = subparsers.add_parser("morning-briefing", help="Queue a morning briefing trigger")
    p_morning.add_argument("--now", action="store_true", help="Queue immediate morning briefing")
    p_morning.add_argument("--time", default=None, help="Scheduled time in HH:MM")

    # Import a validated, idempotent multiple-choice deck
    p_import = subparsers.add_parser("import-deck", help="Import an FSRS deck from JSON")
    p_import.add_argument("--path", type=Path, required=True, help="Path to deck JSON")
    p_import.add_argument("--dry-run", action="store_true", help="Validate the deck without database changes")

    # Status
    subparsers.add_parser("status", help="Show pending triggers and due cards")

    args = parser.parse_args()
    config = AssistantConfig()

    if args.command == "add-card":
        asyncio.run(cmd_add_card(args, config))
    elif args.command == "add-habit-check":
        asyncio.run(cmd_add_habit_check(args, config))
    elif args.command == "morning-briefing":
        asyncio.run(cmd_morning_briefing(args, config))
    elif args.command == "status":
        asyncio.run(cmd_status(args, config))
    elif args.command == "import-deck":
        try:
            asyncio.run(cmd_import_deck(args, config))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"Deck import failed: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
