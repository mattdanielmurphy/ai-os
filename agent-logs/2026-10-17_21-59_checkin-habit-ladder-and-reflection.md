# Check-in: habit ladder + Sonnet reflection step

- New `services/checkin/` (page template copied in from `tmp/checkin/`, which stays as scratch).
- `ladder.py` + `ladder.json`: grows one thing per 7 kept days (alternating a level-up with adding a new step once the streak is 14+), undoes the latest growth on one missed day, drops everything to the floor after 2+ missed days, eases a habit after 2 days under dose. 7 unittest cases pass.
- Page reads doses from the ladder (breath count, gratitude count, card target), shows "New this week", renders unlocked steps, and ends with a "Now reflect with Claude" link to the thread.
- `reflection_prompt.md`: Sonnet seed prompt for the dictated, therapist-style morning reflection; it records reflection minutes back into the ladder.
- Not built: the daily job that chains record → thread → build → publish → iMessage.
