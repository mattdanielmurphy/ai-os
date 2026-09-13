"""Card prompt formatting and progressive elaboration for Telegram."""

from datetime import datetime
from typing import Any, Dict, List, Tuple


def format_review_prompt(card: Dict[str, Any]) -> Tuple[str, List[List[Dict[str, str]]]]:
    """
    Formats the micro-dosing review prompt with inline rating buttons.
    Returns:
        (message_text, inline_keyboard_markup)
    """
    deck_type = card.get("deck_type", "cold_storage")
    deck_label = "📚 Coursework" if deck_type == "cold_storage" else "💡 Baby Facts"
    prompt = card.get("prompt", "")

    text = (
        f"🧠 *Spaced Repetition Review* · _{deck_label}_\n\n"
        f"*Question:*\n{prompt}\n\n"
        f"_Take 10–30s. Rate your recall below:_"
    )

    card_id = card["card_id"]
    keyboard = [
        [
            {"text": "🔴 Again", "callback_data": f"fsrs:{card_id}:1"},
            {"text": "🟠 Hard", "callback_data": f"fsrs:{card_id}:2"},
        ],
        [
            {"text": "🟢 Good", "callback_data": f"fsrs:{card_id}:3"},
            {"text": "⚡️ Easy", "callback_data": f"fsrs:{card_id}:4"},
        ],
    ]

    return text, keyboard


def format_review_completed(
    card: Dict[str, Any],
    rating_val: int,
    next_due: datetime,
) -> str:
    """
    Formats the in-place edited message after user rates their recall.
    Shows the answer, next scheduled date, and progressive elaboration.
    """
    rating_names = {1: "🔴 Again", 2: "🟠 Hard", 3: "🟢 Good", 4: "⚡️ Easy"}
    rating_str = rating_names.get(rating_val, "Rated")

    prompt = card.get("prompt", "")
    answer = card.get("answer", "")
    elaboration = card.get("elaboration", "")
    due_str = next_due.strftime("%b %d, %Y at %H:%M UTC")

    text = (
        f"✅ *Review Completed* ({rating_str})\n\n"
        f"*Question:*\n{prompt}\n\n"
        f"*Answer:*\n{answer}\n\n"
        f"💡 *Progressive Elaboration:*\n{elaboration}\n\n"
        f"📅 *Next Review:* `{due_str}`"
    )
    return text
