# Agent Log: Instant Streaming Wake Word Feedback & Live HUD

## Context & Problem
Previously, `services/wake-hal/hal_listener.py` collected microphone audio and only performed Whisper transcription and wake-word evaluation after the user finished their complete spoken sentence and paused for ~1.1 seconds of silence (`silent_count > SILENCE_CHUNKS`). Consequently, the user received no visual confirmation or alert feedback while speaking.

## Changes Made
1. **Real-Time Interim Wake Detection (`services/wake-hal/hal_listener.py`):**
   - Added interim audio buffer evaluation (`INTERIM_MIN_CHUNKS = 6` ~384ms, `INTERIM_CHECK_INTERVAL = 5` ~320ms) while speech is actively occurring (`is_speaking == True`).
   - Transcribes partial audio chunks on-the-fly via Whisper (`tiny.en` int8).
   - As soon as "Hal" (or phonetic equivalents) is recognized (~400ms into speech), it immediately:
     - Sets `early_wake_detected = True`.
     - Displays the floating on-screen HUD badge (`show_gui_overlay("🎙️ Hal is listening...", 4.0)`).
     - Plays the activation chime (`afplay Tink.aiff`).
   - Ceases interim transcription overhead for the remainder of the utterance once detected, avoiding unnecessary CPU cycles while the user finishes speaking.

2. **Snappier Finalization & Dispatch:**
   - Reduced `SILENCE_CHUNKS` from 18 to 12 (~0.76s trailing silence) for faster post-sentence command execution.
   - Combined `early_wake_detected` state into the final utterance resolution to ensure instant dispatch even if trailing punctuation or noisy background obscures the wake prefix in the full audio buffer.

3. **Robust HUD Overlays & PATH Resolution:**
   - Enhanced `show_gui_overlay()` to use Hammerspoon AppleScript execution (`hs.alert.show`) for immediate centered on-screen alerts, falling back to Notification Center banners.
   - Fixed `agy` CLI binary resolution in `scripts/triage_router.py` via `shutil.which` and added `~/.local/bin` to `com.aios.wake-hal.plist` environment variables.

4. **Service Reload:**
   - Reloaded LaunchAgent `com.aios.wake-hal` in `launchd`.
