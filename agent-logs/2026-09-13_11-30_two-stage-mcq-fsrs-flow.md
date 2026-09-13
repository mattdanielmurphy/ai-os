# Agent Log: 2026-09-13 11:30 - Two-Stage MCQ & Struggle Rating Flow

## Overview
Restructured the Telegram interactive spaced repetition review mechanism in `services/assistant/` from an open-ended recall button prompt into an active-recall 2-stage interaction:
1. **Stage 1 (Multiple-Choice Question)**: Displays the prompt with multiple-choice candidate answers (options `A`, `B`, `C`, `D`) and inline buttons.
2. **Stage 2 (Struggle / Confidence Rating)**: When the user selects an answer button, the message is updated in place to reveal correctness feedback (`🎯 Correct!` or `❌ Incorrect`), the full answer explanation, and progressive elaboration. It presents 4 confidence/struggle rating buttons:
   - `⚡️ Instant` (Easy = 4)
   - `🟢 Confident` (Good = 3)
   - `🟠 Struggled` (Hard = 2)
   - `🎲 Lucky Guess / Again` (Again = 1)
3. **Stage 3 (Confirmation & FSRS Scheduling)**: When the struggle button is pressed, the FSRS algorithm updates the card metrics (`stability`, `difficulty`, `reps`, `lapses`, `due_at`), persists review logs in SQLite (`~/.hermes/assistant.db`), resolves the outbound signal, and mutates the message in place with next review due date (inline keyboard removed).

## Changes Made
- **`services/assistant/storage/db.py`**: Added `options TEXT` (JSON) and `correct_index INTEGER` columns with automated runtime database migration for existing SQLite databases.
- **`services/assistant/spaced_repetition/cards.py`**:
  - `format_review_prompt`: Formats MCQ options with `*A)* ...` markdown list and inline buttons `[A] [B] [C] [D]`.
  - `format_feedback_prompt`: Evaluates user selection, displays correct/incorrect feedback with answer and elaboration, and constructs struggle rating keyboard.
  - `format_review_completed`: Replaces keyboard with final confirmation and next scheduled review date.
- **`services/assistant/telegram_gateway/bot.py`**: Enhanced `edit_prompt` to support replacing existing inline keyboards with `keyboard_rows`.
- **`services/assistant/telegram_gateway/handlers.py`**: Added callback handlers for `fsrs_pick:<card_id>:<idx>` (routes to `_handle_fsrs_pick`) and `fsrs_rate:<card_id>:<rating>` (routes to `_handle_fsrs`).
- **`services/assistant/cli.py`**: Updated `add-card` to support `--options` (pipe-separated) and `--correct-index`.
- **`services/assistant/tests/test_assistant.py`**: Added and verified end-to-end multi-choice and struggle rating tests. All 7 test suites passing.
- **LaunchAgent**: Daemon reloaded via `la restart aios-assistant` (`com.matt.agent.aios-assistant`), confirmed running and live polling on Telegram. Live test MCQ card dispatched to Telegram bot `@mdm_assistor_bot`.
