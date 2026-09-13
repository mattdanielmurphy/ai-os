# Agent Log: 2026-09-13 11:42 - Telegram Text Messages, Executive Commands & AI-OS Integration

## Root Cause
Previously, `telegram_gateway/handlers.py` and `bot.py` only registered a `CallbackQueryHandler` to handle button presses. When the user sent plain text messages, commands (`/status`, `/quiz`, `/help`), or quick capture notes to `@mdm_assistor_bot`, python-telegram-bot dropped them silently because no `MessageHandler` or `CommandHandler` was registered.

## Solution & Architecture
1. **Added Full Message & Command Registration (`bot.py` & `handlers.py`)**:
   - Registered `CommandHandler` for `/start`, `/help`, `/status`, `/info`, `/quiz`, `/review`, `/habits`, `/habit`, `/note`, `/capture`, `/remind`, `/todo`.
   - Registered `MessageHandler(filters.TEXT & ~filters.COMMAND, ...)` for all incoming freeform text messages.
   - Added `send_chat_action(chat_id, "typing")` for visual feedback during processing.
   - Added fallback to unformatted text in `send_message` if Telegram Markdown parsing fails.

2. **Smart Active Prompt Text Routing**:
   - If an active FSRS quiz prompt is awaiting a response (`AWAITING_INPUT`), users can now answer via text (typing `A`, `B`, `C`, `D`, `1..4`, or option label text). It routes directly to `_handle_fsrs_pick`.
   - If awaiting struggle rating, typing `confident`, `good`, `struggled`, `hard`, `instant`, `again`, etc. routes directly to `_handle_fsrs`.
   - If an active habit check prompt is awaiting response, typing `done`, `full`, or `emergency` routes to `_handle_habit`.

3. **Natural Keyword Commands**:
   - Plain text keywords without slashes (`status`, `quiz`, `review`, `habits`, `help`) automatically trigger the respective command.

4. **Apple Reminders & Obsidian Quick Capture**:
   - If the user sends a reminder request (e.g. `remind me to call X`, `todo: Y`), the assistant triggers the `apple-reminders` CLI directly and confirms.
   - If the user sends a note (`note: Z`, `capture: Z`), it appends to `Obsidian/Personal/Inbox/Quick Capture.md`.

5. **Conversational Assistant via AI-OS**:
   - General conversation and freeform questions trigger an asynchronous query to `scripts/query_aios.js` connecting to the local AI-OS companion app (`http://127.0.0.1:3031`), responding to the user directly on Telegram with full intelligence.

6. **Testing & Verification**:
   - Added `test_text_messages_and_commands` in `test_assistant.py`.
   - All 8 test suites pass (`pytest services/assistant/tests/test_assistant.py -v`).
   - Reloaded LaunchAgent `com.matt.agent.aios-assistant` via `la restart aios-assistant`.
