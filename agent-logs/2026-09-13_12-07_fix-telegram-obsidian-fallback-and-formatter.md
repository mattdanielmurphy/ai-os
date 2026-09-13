# Agent Work Log: Fix Telegram Obsidian Fallback & HTML Formatter Regressions

- **Date:** 2026-09-13 12:07
- **Task:** Fix Telegram "Try again" message being captured to Obsidian Inbox instead of executing AI query, fix prompt rejection with leading dashes in `query_aios.js`, and fix italic regex skipping inline code placeholders in `formatter.py`.

## 1. Root Cause Analysis
1. **Accidental Obsidian Capture**: In `services/assistant/telegram_gateway/handlers.py`, `handle_text_message` had a fallback: `if not aios_reply: return await self.cmd_capture(clean_text, chat_id)`. When an AI-OS query failed or timed out, any ordinary conversational message (such as "Try again") was erroneously saved to `Obsidian/Inbox/Quick Capture.md`.
2. **CLI Argument Rejection in `query_aios.js`**: `query_aios.js` discarded positional arguments starting with `-` (`if (!message && !arg.startsWith('-'))`). The contextual prompt built by `build_conversational_prompt()` began with `--- Prior Conversation Context ---`, so `query_aios.js` ignored it, printed the usage error, and exited with code 1.
3. **Italic Regex Failure with Placeholders**: In `formatter.py`, placeholders were generated as `\x00TGH_{idx}\x00`. Because `PAT_ITALIC` matches `[^_\n]+?`, encountering the underscore in `TGH_` aborted the match. As a result, constructs like `_Location: `Inbox/Quick Capture.md`_` remained unformatted with raw underscores.

## 2. Changes Made
1. **`scripts/query_aios.js`**:
   - Added `--prompt` and `--message` explicit CLI flags.
   - Added standard POSIX `--` delimiter handling (all trailing arguments belong to `message`).
   - Relaxed positional prompt assignment to accept multi-line strings with leading dashes or markdown lists.
2. **`services/assistant/telegram_gateway/handlers.py`**:
   - Updated `build_conversational_prompt()` to use `[Prior Conversation Context]` and `[End Prior Context]`.
   - Updated `_query_aios()` to explicitly pass `--prompt`, enforce `--timeout 300`, and set `asyncio.wait_for` to 310s.
   - Removed the Obsidian Inbox fallback for failed queries; replaced with an informative error notification.
3. **`services/assistant/telegram_gateway/formatter.py`**:
   - Switched placeholder token format from `\x00TGH_{idx}\x00` to `\x00TGHX{idx}X\x00`, preventing italic regex interference.
4. **`services/assistant/tests/test_assistant.py`**:
   - Added automated unit test assertion verifying italic wrapping around inline code blocks (`_Location: `path`_` -> `<i>Location: <code>path</code></i>`).
5. **Obsidian Inbox & DB Cleanup**:
   - Removed accidental `"Try again"` entry from `Inbox/Quick Capture.md`.
   - Removed orphaned uncompleted record from SQLite `chat_history`.
6. **Service Reload**:
   - Restarted `aios-assistant` via `la restart aios-assistant`.
