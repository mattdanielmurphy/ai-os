# Telegram HTML Formatting & Markdown Conversion

**Date:** 2026-09-13 11:48  
**Component:** `services/assistant/telegram_gateway/`

## Objective
Fix unformatted markdown and plain text rendering in Telegram bot messages by transitioning from Telegram's legacy `MARKDOWN` parse mode to native `ParseMode.HTML` with a robust Markdown-to-Telegram-HTML conversion pipeline and message chunking.

## Root Cause
1. `services/assistant/telegram_gateway/bot.py` previously configured `parse_mode = ParseMode.MARKDOWN` (Telegram legacy mode).
2. Telegram's legacy parser does not support CommonMark/GFM features like `**bold**`, Markdown headers (`#`), bullet lists, or underscores inside variable names (`snake_case_vars`).
3. Furthermore, when conversational queries were processed through AI-OS (`_query_aios`), the resulting LLM markdown triggered Telegram parsing exceptions (`can't parse entities`), causing the bot's exception fallback to send the raw unformatted plain text.

## Changes
1. **HTML Formatter Utility (`services/assistant/telegram_gateway/formatter.py`)**:
   - Implemented `markdown_to_telegram_html(text)`:
     - Extracts fenced code blocks (` ```lang ... ``` `) and inline code (`` `code` ``), HTML-escapes content, and wraps them in `<pre><code class="language-...">` and `<code>`.
     - Preserves any pre-existing valid Telegram HTML tags (`<b>`, `<i>`, `<code>`, `<pre>`, `<a>`, `<blockquote>`, `<tg-spoiler>`, `<s>`, `<u>`).
     - Safely escapes raw HTML entities (`&`, `<`, `>`).
     - Converts blockquotes (`> quote`) into Telegram `<blockquote>` containers.
     - Converts markdown headers (`# Header`) into bold labels (`<b>Header</b>`).
     - Converts markdown links (`[label](url)`) into `<a href="url">label</a>`.
     - Converts `**bold**` and `*bold*` into `<b>bold</b>`.
     - Converts `_italic_` into `<i>italic</i>` while preserving word boundaries (`snake_case` variables remain untouched).
     - Converts strikethrough (`~~text~~`) and spoilers (`||text||`) into `<s>` and `<tg-spoiler>`.
     - Converts markdown bullets (`- ` or `* `) into clean Unicode bullets (`• `).
   - Implemented `split_message_chunks(text, max_chars=4000)` to prevent Telegram `400 Bad Request: message is too long` errors by splitting long text at paragraph, newline, or word boundaries.
2. **Gateway Engine (`services/assistant/telegram_gateway/bot.py`)**:
   - Changed default `parse_mode` across `send_message`, `send_prompt`, and `edit_prompt` to `ParseMode.HTML`.
   - Wired outgoing text through `markdown_to_telegram_html` when `parse_mode == ParseMode.HTML`.
   - Added chunked sending for long conversational responses.
   - Retained plain text fallback recovery for resilient delivery.
3. **Tests (`services/assistant/tests/test_assistant.py`)**:
   - Added `test_telegram_html_formatter` covering bold/italic/headers/quotes, special HTML character escaping, fenced code highlighting, snake_case protection, and message splitting.
   - Verified 100% test pass rate across all 9 unit/integration test suites.
4. **Daemon Reload**:
   - Reloaded LaunchAgent `com.matt.agent.aios-assistant` via `la restart aios-assistant`. Verified live connection and polling in tmux session `agent-aios-assistant`.
