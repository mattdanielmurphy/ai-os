# Agent Log: Hal Wake Word Listener & Headless Triage Router

**Date:** 2026-08-30  
**Status:** Completed & Verified  

## Summary of Changes

1. **Wake Word Listener (`services/wake-hal/hal_listener.py`)**:
   - Built on-device wake-word detection using Whisper (`tiny.en` int8) and PyAudio on the default microphone.
   - Configured robust phonetic wake-phrase recognition supporting `"Hal"`, `"Hey Hal"`, `"How"`, `"Howl"`, `"Hi Hal"`, etc.
   - Supported both:
     - **Two-stage activation**: Saying `"Hal"` arms a 10-second active listening window (with audible `"Tink"` chime), then captures the follow-up command.
     - **Single-utterance activation**: Saying `"Hal, open google"` immediately strips the wake word and dispatches `"open google"`.
   - Added audible feedback chimes for activation (`Tink`), dispatch (`Pop`), and timeout (`Purr`).

2. **Headless Triage Dispatcher (`scripts/triage_router.py`)**:
   - Eliminated brittle GUI AppleScript / `osascript` keystroke automation and mouse click simulations that were failing due to background macOS TCC / accessibility permission barriers.
   - Refactored prompt routing to use headless non-interactive CLI execution (`dispatch_headless_prompt()` via `agy -p "<prompt>"`).
   - Expanded direct execution patterns in `try_direct_execution()` to support:
     - Clean conversational prefix stripping (`"I'll "`, `"please "`, `"can you "`, `"let's "`).
     - Sentence punctuation stripping (`.`, `?`, `!`, `,`).
     - Application launches across standard macOS applications (`APP_ALIASES`).
     - Direct web search queries (`"google <query>"`, `"search for <query>"`).

3. **Background Daemon Supervision (`~/Library/LaunchAgents/com.aios.wake-hal.plist`)**:
   - Configured LaunchAgent to keep `hal_listener.py` running persistently in the background across macOS reboots.
   - Linked logging to `~/.hermes/logs/wake-hal-err.log` and `wake-hal.log`.

4. **Live Background Service Monitor (`services/wake-hal/monitor.py`)**:
   - Built a real-time monitor tool that taps into the background service logs and visualizes live speech transcription, wake word detections, and triage dispatches.
