# Morning Call Tester & Voice Agent Persona Bench

- **Date:** 2026-10-13
- **Focus:** Deepgram Voice Agent settings optimization (speech speed, turn latency, pause elimination), prompt engineering for morning wake-up personas, and local test platform implementation.

## Accomplishments
1. **Identified Exact Deepgram Voice Agent Parameters:**
   - Speech speed parameter: `agent.speak.provider.speed` (range `0.5`–`1.5`, sweet spot `1.25`–`1.35`).
   - Turn-taking latency parameters: `agent.listen.provider.eot_threshold` (`0.55`–`0.60`) and `agent.listen.provider.eager_eot_threshold` (`0.40`–`0.45`).
   - Pause suppression strategy: Instructing the LLM to avoid commas and ellipses, using exclamation marks and dashes to keep TTS delivery rapid-fire.
2. **Clarified Telegram Voice Calling Feasibility:**
   - Standard Telegram Bot API cannot initiate voice phone calls.
   - Outlined viable paths: Twilio Media Streams calling Matt's direct phone number `(825) 977-5250`, Telegram UserBot (MTProto/PyTgCalls), or WebRTC/Web Audio call trigger.
3. **Engineered Upgraded & New Wake-Up Prompts:**
   - Upgraded Gunnery Sgt. Hartman with deadpan realism, non-repetition invariants, and physical verification challenges.
   - Added Archibald (The Devastatingly Disappointed Victorian Butler).
   - Added Rex Sterling (The Hyper-Caffeinated Startup Pit Boss).
   - Added Handler 8 (The Panicked Sci-Fi Temporal Dispatcher).
4. **Built Interactive Testing Platform:**
   - Created `tools/voice-agent-tester` with Bun HTTP + WebSocket server (`server.ts`).
   - Implemented real-time browser Web Audio microphone capture and playback with Deepgram WebSocket proxy.
   - Configured local dev domain via puma-dev: `http://morning-call.test` (port 3344).
