# Agent Work Log: Telegram Bot Codex Migration, Groq Cloud STT, and Multimodal Support

**Date:** 2026-09-19 13:06  
**Author:** Antigravity  
**Component:** `services/assistant/` (`telegram_gateway/`, `tests/`)

## Objective
1. Migrate the proactive Telegram assistant service from finicky `query_aios.js` to direct OpenAI Codex via `hermes chat -q ... --provider openai-codex` backed by Matt's active Codex subscription.
2. Provide full multimodal media support for incoming Telegram messages (photos/screenshots, voice notes, audio files, videos, documents).
3. Integrate free Groq Cloud STT using `whisper-large-v3-turbo` for sub-second audio/video transcription into queries, avoiding any local whisper model execution on macOS.
4. Enforce Telegram presentation rules: format all structured data as vertical cards/blocks with bold labels and bullet points, eliminating scrambled ASCII or markdown tables on mobile.
5. Provide on-demand coding task delegation via `/agy <prompt>` or `agy: <prompt>`.

## Changes Implemented

### 1. Groq Cloud STT Client (`services/assistant/telegram_gateway/stt.py`)
- Created `transcribe_audio_file` using `httpx.AsyncClient` targeting `https://api.groq.com/openai/v1/audio/transcriptions`.
- Pre-configured for model `whisper-large-v3-turbo` with multipart upload support for `.ogg`, `.oga`, `.mp3`, `.wav`, `.m4a`, `.webm`, `.flac`.
- Added `extract_audio_from_video` using macOS `ffmpeg` to extract audio streams from Telegram video and video-notes for Whisper transcription.

### 2. Telegram Vertical Card Table Formatter (`services/assistant/telegram_gateway/formatter.py`)
- Replaced `format_ascii_box_table` with `format_vertical_card_table`:
  - 2-column tables format as clean key-value bullet lists: `• <b>Key:</b> Value`.
  - 3+ column tables format as mobile vertical cards: card title `<b>Entity Name</b>` followed by attribute bullet items `• <b>Header:</b> Value`.
  - Escapes HTML entities safely.

### 3. OpenAI Codex Query & Multimodal Handlers (`services/assistant/telegram_gateway/handlers.py`)
- Replaced `_query_aios` with `_query_codex` calling `hermes chat -q ... -Q --provider openai-codex --source tool --ignore-rules --reasoning none`.
- Added `clean_hermes_output` to sanitize warnings, reasoning boxes, and session IDs.
- Injected strict Telegram mobile formatting rules into `build_conversational_prompt`.
- Implemented:
  - `handle_photo_message`: Downloads highest resolution image, queries Codex Vision via `--image`.
  - `handle_audio_message`: Transcribes voice note via Groq Whisper, displays transcript `🎙️ "..."`, routes as conversational query or executive command.
  - `handle_video_message`: Extracts audio with ffmpeg, transcribes via Groq Whisper, routes query.
  - `handle_document_message`: Auto-detects images, audio, video, or reads code/text documents and passes to Codex.
  - `_query_agy`: Supports `/agy <prompt>` and `agy: <prompt>` for coding delegation.
- Registered handlers for `PHOTO`, `VOICE | AUDIO`, `VIDEO | VIDEO_NOTE`, `Document.ALL`, `CommandHandler(["agy", "code"])`.

### 4. Assistant Configuration & Environment (`services/assistant/config.py`)
- Added `groq_api_key` (loaded from `~/.hermes/.env`) and `media_tmp_dir` (`./tmp/telegram_media/`).

### 5. Test Suite & Verification (`services/assistant/tests/test_assistant.py`)
- Added tests for `test_vertical_card_formatting`, `test_clean_hermes_output_utility`, and `test_multimodal_media_handlers_dispatch`.
- All 14 tests passing.
- Restarted `aios-assistant` launch agent and verified live Telegram polling.
