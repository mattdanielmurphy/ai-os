# User Personal To-Dos & Apple Reminders Protocol
- **Constraint**: Whenever Matt mentions personal to-dos, future follow-ups, calls to make (e.g., "I'll call them Monday"), reminders, or requests to track tasks for himself:
  - Agents MUST IMMEDIATELY execute the `apple-reminders` CLI in the same turn (`apple-reminders add --title "..." --due "YYYY-MM-DD HH:MM" --notes "..."`) with intelligent due dates, contact numbers, and relevant identifiers pre-populated in the notes.
  - Agents should proactively offer to break down overwhelming or multi-step tasks into small, low-friction subtasks in Apple Reminders.
  - Do NOT create orphaned markdown to-do files in random locations that won't be actively checked on mobile.
  - **Default to creating (2026-10-20)**: When it's unclear whether something deserves a reminder, create it anyway, then ask Matt whether he wants it deleted. A missed question must still leave a reminder behind.
  - **No sleep reminders (Matt, 2026-10-22)**: never create "go to bed" / "wake up" reminders, alarms or notifications (Reminders, Calendar, scripts like `hue.py`). The Hue lights already carry the bed/wake cues.
  - **Habits stay off the calendar (Matt, 2026-10-22)**: new habits start tiny and grow slowly, pull back after any missed day, and live in the check-in habit ladder (`services/checkin/ladder.json`), not in Calendar.
