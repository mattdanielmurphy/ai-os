# Fix Telegram Morning Check-in Breath Callback Handling

**Date:** 2026-10-08 10:05  
**Author:** Antigravity  
**Component:** `services/assistant/telegram_gateway/`

## Problem
When tapping the "4 breaths" (or 1, 2, 3 breaths) buttons for morning check-in on Telegram, nothing happened. The user reported:
> "problem: I'm tapping "4 breaths" button for morning checkin on telegram and nothing is happening"

Inspecting the live service logs via `tmux capture-pane -pt agent-aios-assistant` revealed recurring warnings:
```
2026-10-08 09:50:44,640 [WARNING] assistant.telegram_gateway.handlers: Unknown callback query format: briefing:breath:4
2026-10-08 09:50:59,735 [WARNING] assistant.telegram_gateway.handlers: Unknown callback query format: briefing:breath:3
```

## Root Cause
In `services/assistant/telegram_gateway/handlers.py`:
1. `callback_data` was split unconditionally on colon: `parts = callback_data.split(":")`. For `"briefing:breath:4"`, `parts` evaluated to `["briefing", "breath", "4"]`.
2. `action_type = parts[0]` (`"briefing"`), and `sub = parts[1]` (`"breath"`).
3. The branch check evaluated `elif sub == "meditate_done" or sub.startswith("breath:"):`.
4. Because `sub` was `"breath"`, `sub.startswith("breath:")` evaluated to `False`. The handler dropped through to `Unknown callback query format: briefing:breath:4`, silently ignoring the button tap.

## Changes Made
1. **`services/assistant/telegram_gateway/handlers.py`**:
   - Updated condition to `elif sub in ("meditate_done", "breath") or sub.startswith("breath:"):`.
   - Extracted breath count from `parts[2]` when `sub == "breath" and len(parts) >= 3` (e.g. `count = int(parts[2])`), retaining fallback parsing for backward compatibility.
   - Deactivated repeat reminders on centering completion via `await self._set_morning_reminders_active(trigger_id, False)`.
   - Enhanced `_morning_trigger_for_message` with a direct fallback query to `outbound_signals` table in case signal status transitioned out of `AWAITING_INPUT`.
2. **`services/assistant/tests/test_assistant.py`**:
   - Added `test_morning_centering_breath_callbacks` testing both `briefing:breath:4` (bonus) and `briefing:breath:1` (micro) callbacks, verifying prompt in-place editing, keyboard removal, gratitude stage progression, reminder deactivation, and heuristic recording.
   - All 23 tests pass.
3. **Service Reload**:
   - Reloaded daemon via `la restart aios-assistant`. Confirmed live Telegram polling resumed with PID 64120. Active outbound signal for message 223 remains `AWAITING_INPUT`.
