# Conversational Card Meta-Context & 1/4-4/4 Rating Hierarchy

## Context
When interacting with the Proactive Assistant's morning flow and FSRS spaced-repetition cards on Telegram:
1. Long multi-word user comments, questions, and meta-feedback regarding the cards or buttons (e.g. containing words like "hard", "struggle", or "1") were inadvertently intercepted by a loose `kw in lower_text.split()` check in `handle_text_message`. This treated conversational feedback as an FSRS rating callback, marked the card reviewed, completed the morning review threshold, and triggered the C&H reward comic prematurely.
2. The button options on iOS Telegram mobile were prone to truncation (e.g. `[Red] Slipped my mind (...` and `[Yellow] Almost had it (Hard)`), and lacked a clear, predictable hierarchy or indication of the 1/4 to 4/4 scale.
3. Conversational queries lacked active card context and morning routine state, or were blocked by canned messages during centering and review.

## Changes
1. **FSRS Rating Button Redesign & Hierarchy Legend (`services/assistant/spaced_repetition/cards.py`)**:
   - Replaced long truncated button labels with concise, numbered, un-truncated button labels:
     - Row 1: `1/4 · Again` (rating 1), `2/4 · Hard` (rating 2)
     - Row 2: `3/4 · Good` (rating 3), `4/4 · Easy` (rating 4)
   - Added an explicit legend to `format_feedback_prompt` and `format_answer_reveal_prompt` explaining the 1/4 to 4/4 scale:
     - `• *1/4 Again:* Missed, blanked, or lucky guess`
     - `• *2/4 Hard:* Recalled with struggle / effort`
     - `• *3/4 Good:* Recalled correctly with normal effort`
     - `• *4/4 Easy:* Instant, effortless recall`
   - Updated `format_review_completed` to log `1/4 · Again (Missed / Guess)`, `2/4 · Hard (Struggled)`, etc.

2. **Strict Rating Parsing & Non-Destructive Fallthrough (`services/assistant/telegram_gateway/handlers.py`)**:
   - Replaced loose `kw in lower_text.split()` with `RATING_EXACT_MAP` matching only explicit rating commands (`1`, `2`, `3`, `4`, `again`, `hard`, `good`, `easy`, `1/4`, `2/4`, `3/4`, `4/4`, etc.).
   - Multiple-choice option picks are only consumed when a card has options and is unanswered (`answered != "true"`).
   - Conversational comments, questions, and feedback fall through to the conversational assistant without resolving or destroying the active prompt, keeping the Telegram buttons active and clickable.
   - During centering and review, non-command user messages fall through to the conversational assistant rather than returning canned error messages.
   - During gratitude, questions and meta-inquiries fall through to the assistant rather than being saved into Obsidian as gratitude notes.

3. **Active Card & Morning Flow System Context Injection (`services/assistant/telegram_gateway/handlers.py`)**:
   - Added `_build_active_system_context(chat_id)` to assemble structured context including:
     - Active flashcard details: deck, prompt, answer, options, correct index, progressive elaboration, and UI state.
     - Active morning flow state: current step (Centering, Gratitude, Review), reviewed count vs threshold, remaining due cards, and routine architecture.
     - Assistant guidance to answer content questions directly, engage in meta-discussions about the system/habits, and remind user that buttons remain active.
   - Updated `build_conversational_prompt` to accept and inject `[Active System & Task Context]`.
   - Persisted `last_active_card_id`, `last_active_card_msg_id`, and `last_active_morning_trigger` across `cmd_quiz`, `cmd_morning`, `_handle_fsrs_pick`, and `_handle_fsrs`.

4. **Testing & Service Verification (`services/assistant/tests/test_assistant.py`)**:
   - Added `test_active_card_conversational_meta_comment_and_button_hierarchy`.
   - Verified that all 25 unit and integration tests pass cleanly.
   - Restarted `aios-assistant` service via `la restart aios-assistant`.
