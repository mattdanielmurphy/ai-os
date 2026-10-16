# Daily Briefing, Comic Anti-Repetition, Morning Nudge Deletion, and Deck Diversification

**Date:** 2026-10-16 10:15  
**Service:** `aios-assistant` (`services/assistant/`)  
**Context:** Matt requested replacing external tech news blasts ("The Rundown") with an ad-free, personalized, pull-based daily brief in Telegram focusing on his core domains (AI, drumming, cello, piano & music theory). Additionally, addressed three Telegram pain points: 15-minute morning nudge message clutter, Cyanide & Happiness (C&H) comic repetition across days, and lack of spaced repetition flashcard variety (pruning FSRS meta-cards and adding new domain decks).

## Changes Implemented

1. **Morning Nudge Message Clutter Elimination (`run.py`, `bot.py`, `handlers.py`)**:
   - Added `delete_message` to `TelegramGateway` in `services/assistant/telegram_gateway/bot.py`.
   - Updated `run.py` to delete `previous_nudge_id` before sending a new 15-minute check-in nudge, with fallback to `edit_prompt` if deletion fails. At any time, exactly one active nudge exists in the chat instead of an escalating stack of edited zombie messages.
   - Updated `handlers.py` to delete stale check-in prompts when acknowledging via "I'm up".

2. **Cyanide & Happiness Anti-Repetition (`briefing/comic.py`, `handlers.py`)**:
   - Identified that Explosm's `/comics/latest` does not update every day (e.g. weekends or multi-day intervals), serving the exact same comic consecutively.
   - Refactored `_fetch_comic_details` to parse `slug` and Next.js navigation `randomSlug`.
   - Updated `fetch_daily_cyanide_and_happiness_comic` to accept `seen_slugs`. If today's latest comic was already seen in recent days, it automatically fetches the random archive comic, guaranteeing a fresh comic every morning.
   - Persisted `seen_comic_slugs` in `AssistantDB` dynamic state.

3. **Spaced Repetition Pruning & Multi-Deck Diversification (`spaced_repetition/decks/`, `handlers.py`, `assistant.db`)**:
   - Deleted the 3 unwanted FSRS meta-cards (`c094a73c`, `1725de8f`, `ce333b97`) from `~/.hermes/assistant.db`.
   - Authored and imported three high-yield JSON decks:
     - `drumming_essentials.json` (`drums` deck): Rudiments, Moeller technique, ghost note placement, polyrhythms (3:2), and linear coordination.
     - `music_theory_strings.json` (`music` deck): Cello tenor clef, open string tuning, bowing techniques (sul tasto, spiccato), tritone substitutions, rootless Bill Evans voicings, and modal interchange.
     - `ai_engineering_essentials.json` (`ai` deck): GQA vs MHA, KV cache linear scaling, FlashAttention tiling, RoPE, and speculative decoding.
   - Updated `cmd_quiz` in `handlers.py` to implement round-robin deck diversification across domains (`forallx`, `drums`, `music`, `ai`) using `last_reviewed_deck_prefix`.
   - Added command and callback routing for `/drums`, `/music`, and `/ai`.

4. **Personalized Daily Briefing ("Daily Signal") (`briefing/news.py`, `handlers.py`, `bot.py`)**:
   - Implemented `DailyNewsService` in `services/assistant/briefing/news.py` providing bounded, ad-free intake structured across AI & Applied Engineering, Drumming, Cello, and Piano & Music Theory.
   - Day-of-year rotation ensures distinct, high-yield practice takeaways every morning.
   - Daily caching in SQLite dynamic state (`daily_brief:YYYY-MM-DD`) eliminates redundant computation.
   - Wired `/news`, `/brief`, `/rundown`, and natural text triggers ("news", "show news") with interactive Telegram inline keyboards (`🔄 Refresh Brief`, `🧠 Review Cards`, `🌅 Morning Flow`).
   - Registered Telegram bot menu commands in `bot.py` via `set_my_commands` for 1-tap access via Telegram's native Menu button.

## Verification

- Ran automated unit and integration tests with pytest: `29 passed in 132.50s`.
- Reloaded `aios-assistant` daemon via `la restart aios-assistant`.
- Verified live process in tmux: `assistant.telegram_gateway.bot: Configured Telegram bot menu commands successfully` and `Telegram Bot polling started`.
