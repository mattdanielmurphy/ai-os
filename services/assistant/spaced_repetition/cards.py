"""Card prompt formatting and progressive elaboration for Telegram (supporting Multiple Choice & Struggle Rating)."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _parse_options(options_field: Any) -> List[str]:
    if not options_field:
        return []
    if isinstance(options_field, list):
        return [str(x) for x in options_field]
    if isinstance(options_field, str):
        try:
            parsed = json.loads(options_field)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            # Fallback to pipe or newline separated
            if "|" in options_field:
                return [x.strip() for x in options_field.split("|") if x.strip()]
            if "\n" in options_field:
                return [x.strip() for x in options_field.splitlines() if x.strip()]
    return []


def format_review_prompt(card: Dict[str, Any]) -> Tuple[str, List[List[Dict[str, str]]]]:
    """
    Formats the review prompt. If the card contains multiple choice options,
    renders options A, B, C, D with 1-tap choice buttons.
    Otherwise falls back to the open recall format.
    """
    deck_type = card.get("deck_type", "cold_storage")
    deck_label = "📚 Coursework" if deck_type == "cold_storage" else "💡 Baby Facts"
    prompt = card.get("prompt", "")
    card_id = card["card_id"]

    options = _parse_options(card.get("options"))
    labels = ["A", "B", "C", "D", "E", "F"]

    if options:
        # Multiple Choice Format (Stage 1)
        options_text_lines = []
        keyboard_buttons = []
        for i, opt in enumerate(options):
            label = labels[i] if i < len(labels) else str(i + 1)
            options_text_lines.append(f"*{label})* {opt}")
            keyboard_buttons.append({"text": label, "callback_data": f"fsrs_pick:{card_id}:{i}"})

        options_block = "\n".join(options_text_lines)
        text = (
            f"🧠 *Spaced Repetition Review* · _{deck_label}_\n\n"
            f"*Question:*\n{prompt}\n\n"
            f"{options_block}\n\n"
            f"_Tap your answer below:_"
        )

        # Split buttons into rows of 2
        keyboard = [keyboard_buttons[i : i + 2] for i in range(0, len(keyboard_buttons), 2)]
        return text, keyboard

    # Fallback to open recall format
    text = (
        f"🧠 *Spaced Repetition Review* · _{deck_label}_\n\n"
        f"*Question:*\n{prompt}\n\n"
        f"_Take 10–30s. Rate your recall below:_"
    )
    keyboard = [
        [
            {"text": "🔴 Again", "callback_data": f"fsrs_rate:{card_id}:1"},
            {"text": "🟠 Hard", "callback_data": f"fsrs_rate:{card_id}:2"},
        ],
        [
            {"text": "🟢 Good", "callback_data": f"fsrs_rate:{card_id}:3"},
            {"text": "⚡️ Easy", "callback_data": f"fsrs_rate:{card_id}:4"},
        ],
    ]
    return text, keyboard


def format_feedback_prompt(
    card: Dict[str, Any], chosen_idx: int
) -> Tuple[str, List[List[Dict[str, str]]]]:
    """
    Stage 2: Shows correctness feedback, reveals the answer and elaboration,
    and prompts for the struggle/confidence calibration rating.
    """
    card_id = card["card_id"]
    prompt = card.get("prompt", "")
    answer = card.get("answer", "")
    elaboration = card.get("elaboration", "")
    correct_idx = int(card.get("correct_index", 0))

    options = _parse_options(card.get("options"))
    labels = ["A", "B", "C", "D", "E", "F"]

    is_correct = chosen_idx == correct_idx

    if is_correct:
        status_banner = "🎯 *Correct!*"
        # Struggle / confidence rating keyboard for correct answers
        keyboard = [
            [
                {"text": "⚡️ Instant / Easy", "callback_data": f"fsrs_rate:{card_id}:4"},
                {"text": "🟢 Confident / Good", "callback_data": f"fsrs_rate:{card_id}:3"},
            ],
            [
                {"text": "🟠 Struggled / Hard", "callback_data": f"fsrs_rate:{card_id}:2"},
                {"text": "🎲 Lucky Guess / Again", "callback_data": f"fsrs_rate:{card_id}:1"},
            ],
        ]
    else:
        chosen_str = (
            f"{labels[chosen_idx]}) {options[chosen_idx]}"
            if chosen_idx < len(options)
            else f"Option {chosen_idx + 1}"
        )
        status_banner = f"❌ *Incorrect.* _(You picked {chosen_str})_"
        # Struggle rating for incorrect answers
        keyboard = [
            [
                {"text": "🔴 Slipped my mind (Again)", "callback_data": f"fsrs_rate:{card_id}:1"},
                {"text": "🟠 Almost had it (Hard)", "callback_data": f"fsrs_rate:{card_id}:2"},
            ]
        ]

    text = (
        f"{status_banner}\n\n"
        f"*Question:*\n{prompt}\n\n"
        f"*Answer:*\n{answer}\n\n"
        f"💡 *Progressive Elaboration:*\n{elaboration}\n\n"
        f"_How was that recall? Rate your struggle / confidence:_"
    )
    return text, keyboard


def format_review_completed(
    card: Dict[str, Any],
    rating_val: int,
    next_due: datetime,
) -> str:
    """
    Stage 3: Formats the in-place edited message after user rates their recall struggle.
    Shows the final scheduled date and progressive elaboration.
    """
    rating_names = {
        1: "🔴 Again (Guess / Missed)",
        2: "🟠 Hard (Struggled)",
        3: "🟢 Good (Confident)",
        4: "⚡️ Easy (Instant Recall)",
    }
    rating_str = rating_names.get(rating_val, "Rated")

    prompt = card.get("prompt", "")
    answer = card.get("answer", "")
    elaboration = card.get("elaboration", "")
    due_str = next_due.strftime("%b %d, %Y at %H:%M UTC")

    text = (
        f"✅ *Recall Logged* ({rating_str})\n\n"
        f"*Question:*\n{prompt}\n\n"
        f"*Answer:*\n{answer}\n\n"
        f"💡 *Progressive Elaboration:*\n{elaboration}\n\n"
        f"📅 *Next Review:* `{due_str}`"
    )
    return text
