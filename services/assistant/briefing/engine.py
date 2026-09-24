"""Engine for composing the Morning Grounding & Executive Briefing prompt."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from services.assistant.context_gate.calendar import CalendarEvent


CENTERING_PROMPTS = [
    (
        "Take a slow, deep breath in through your nose... hold it gently... and exhale fully through your mouth. "
        "Notice your physical points of contact with your chair or the floor. "
        "Unclench your jaw, soften your shoulders, and allow this morning to begin without hurry."
    ),
    (
        "Pause for 60 seconds. Close your eyes or soften your gaze. "
        "Notice where you might be holding subtle tension—in the brow, neck, or hands. "
        "Breathe directly into those areas and let them release. Ground yourself in the present moment."
    ),
    (
        "Take three intentional, steady breaths. "
        "As you inhale, feel the clarity and space of the morning. "
        "As you exhale, let go of any residue or pressure from yesterday. You are completely in control of today's pace."
    ),
]


class MorningBriefingBuilder:
    def __init__(self, date: Optional[datetime] = None):
        self.date = date or datetime.now()

    def _get_centering_prompt(self) -> str:
        # Stable day-of-year rotation
        day_of_year = self.date.timetuple().tm_yday
        return CENTERING_PROMPTS[day_of_year % len(CENTERING_PROMPTS)]

    def build_prompt(
        self,
        due_cards_count: int = 0,
        calendar_events: Optional[List[CalendarEvent]] = None,
    ) -> Tuple[str, List[List[Dict[str, str]]]]:
        """
        Builds the formatted markdown message and interactive inline keyboard.
        """
        date_str = self.date.strftime("%A, %B %d")
        centering = self._get_centering_prompt()

        lines = [
            f"🌅 *Morning Grounding & Briefing* — {date_str}\n",
            "*Step 1 of 3 · 60-Second Mindful Centering*",
            f"_{centering}_\n",
            "When you are finished, tap the button below. The next part of the morning flow will appear then.\n",
        ]

        # Spaced Repetition Summary
        if due_cards_count > 0:
            lines.append(f"📚 *Spaced Repetition (FSRS)*\nYou have *{due_cards_count} card{'s' if due_cards_count != 1 else ''}* ready for active recall review today.\n")
        else:
            lines.append("📚 *Spaced Repetition (FSRS)*\nAll caught up! Zero cards due right now.\n")

        # Calendar Schedule Summary
        lines.append("📅 *Today's Schedule*")
        events = calendar_events or []
        today_events = [
            e for e in events
            if e.start.date() == self.date.date()
        ]

        if not today_events:
            lines.append("• No scheduled events today. Clear calendar for deep work.\n")
        else:
            for ev in today_events:
                if ev.is_all_day:
                    lines.append(f"• [All Day] *{ev.title}*")
                else:
                    start_str = ev.start.strftime("%-I:%M %p")
                    end_str = ev.end.strftime("%-I:%M %p")
                    lines.append(f"• {start_str} – {end_str}: *{ev.title}*")
            lines.append("")

        message_text = "\n".join(lines).strip()

        # Build inline keyboard
        keyboard: List[List[Dict[str, str]]] = [
            [{"text": "🧘 Done Centering", "callback_data": "briefing:meditate_done"}]
        ]

        return message_text, keyboard
