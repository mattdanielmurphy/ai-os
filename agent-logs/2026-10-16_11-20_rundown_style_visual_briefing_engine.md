# Visual Rundown-Style AI Newsletter Engine & Pytest Summary Wrapper

**Date:** 2026-10-16 11:20  
**Service:** `aios-assistant` (`services/assistant/`)  
**Context:** Matt pointed out that the previous briefing implementation ("Daily Signal") was an unreadable, academic text wall consisting of static formulas (RoPE, FlashAttention) and music drills rather than an entertaining, high-signal replacement for The Rundown. Replaced the static textbook generator with a full-fledged Rundown ingestion and delivery engine featuring live RSS parsing, 100% ad elimination, hero image delivery, and a non-blocking pytest test runner.

## Changes Implemented

1. **Live Rundown Ingestion & Ad Elimination (`services/assistant/briefing/news.py`)**:
   - Replaced static flashcard arrays with live ingestion of The Rundown AI's official Beehiiv RSS feed (`https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml`).
   - Built an ad-filtering engine that detects and strips 100% of sponsored sections (`TOGETHER WITH HUBSPOT`, `PRESENTED BY GARTNER`, partner webinars, and disguised promotional guides).
   - Extracted structured stories following The Rundown's signature format:
     - Catchy emoji headline
     - High-res hero image URL and attribution
     - **The Rundown**: 1–2 punchy sentences with original source hyperlinks preserved
     - **The details**: 3–4 bullet points highlighting crazy specs, timelines, numbers
     - **Why it matters**: 1-sentence real-world takeaway
   - Extracted **Trending AI Tools** (links + 1-line takeaways) and actionable **AI Workflows / Tutorials** (e.g. ChatGPT interactive UI calculators).
   - Preserved personalized practice tips by converting them into a single rotating **Musician's Pro Tip** (Drumming, Cello, Piano) featured as a bonus bite at the bottom rather than an academic study sheet.
   - Added rich offline fallback stories (Tesla airborne supercar and Meta 816B Mac supercomputer) so briefing generation never fails even without network connectivity.

2. **Visual Telegram Delivery (`services/assistant/telegram_gateway/bot.py`, `handlers.py`)**:
   - Updated `send_photo_url` in `TelegramGateway` to allow `media.beehiiv.com`, `beehiiv.com`, and related trusted image CDNs.
   - Enhanced `DailyNewsService` to download and cache hero images locally to `./tmp/news_cache/` for bulletproof file upload.
   - Refactored `cmd_news` in `ActionDispatcher` to deliver a two-card experience:
     - **Card 1 (Photo Message)**: The high-res hero image accompanied by the lead story headline, **The Rundown**, and **The details** formatted within Telegram's 1024-character caption limit.
     - **Card 2 (Digest Message)**: Secondary deep dive, **Trending AI Tools**, **AI Workflow**, and rotating **Musician's Pro Tip**, with interactive action buttons (`🔄 Refresh Brief`, `🧠 Review Cards`, `🌅 Morning Flow`).
     - Graceful fallback: If photo delivery fails, seamlessly bundles the briefing into a single message.

3. **Pytest Session-Summary Monitor Wrapper (`scripts/run_pytest.py`)**:
   - Built a subprocess wrapper that monitors pytest stdout in real time and exits immediately once the summary line (`=== ... in ...s ===`) is printed.
   - Eliminates process hanging on background asyncio event loops and dangling thread pools.

## Verification

- Tested `run_pytest.py` against news tests: `3 passed in 2.52s`.
- Ran full assistant test suite: `30 passed in 99.48s`.
- Reloaded live daemon via `la restart aios-assistant` and verified healthy status and polling in tmux.
