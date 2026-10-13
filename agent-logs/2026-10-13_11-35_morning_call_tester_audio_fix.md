# Morning Call Voice Agent Tester: Audio Pipeline & Live Interaction Fix

- **Date:** 2026-10-13
- **Focus:** Fixing silent audio playback, resolving Web Audio / Deepgram synchronization bugs, and completing features (persistent settings, mid-call live updates, silence watchdog, and starred voice catalog).

## Root Causes Isolated & Resolved
1. **Premature UI Status & Hidden Dialogue:**
   - In `public/app.js`, when `msg.status === "settings_sent"`, the UI displayed "Agent speaking... 🔊" immediately before audio chunks were decoded or confirmed.
   - The "Spoiler Shield" (`#hideUntilSpokenCheckbox`) was checked by default, suppressing greeting and agent dialogue in the transcript while audio was delayed.
   - **Fix:** Gated `#speakingPill` strictly on `AgentStartedSpeaking` or active PCM playback (`playPcmChunk`), unchecked the spoiler shield by default, and ensured transcript items display as received.

2. **Microphone Feedback Loop & Barge-In Interruption:**
   - `scriptProcessor = audioCtx.createScriptProcessor(4096, 1, 1)` was directly piped to `audioCtx.destination`, playing microphone input out through the speakers and triggering Deepgram's acoustic barge-in / cancellation immediately upon speech initiation.
   - **Fix:** Connected `scriptProcessor` through a zero-gain mute node (`muteGain.gain.value = 0`) to `audioCtx.destination`, satisfying Chrome's execution requirement without routing mic audio out of speakers.

3. **AudioContext Autoplay Suspension:**
   - WebKit/Chrome initializes Web Audio `AudioContext` in `suspended` state.
   - **Fix:** Added `await audioCtx.resume()` in `startCall()` and fallback resume inside `playPcmChunk` and `AgentStartedSpeaking`.

4. **Premature Binary Streaming to Deepgram:**
   - `server.ts` forwarded raw mic PCM frames to Deepgram before Deepgram acknowledged `SettingsApplied`.
   - **Fix:** Added `session.settingsApplied = false` gating in `server.ts`; mic frames are forwarded only after `SettingsApplied` is confirmed by Deepgram.

5. **Audio Buffer Clamping & Scheduling Drift:**
   - In `playPcmChunk`, odd byte lengths from binary frames could trigger a `RangeError` in `new Int16Array()`.
   - **Fix:** Clamped sample counts using `Math.floor(arrayBuffer.byteLength / 2)`, handled `Blob` and typed array instances cleanly, and protected `nextPlayTime` from drift with 20ms lookahead clamping.

## Verification
- HTTP and WebSocket endpoints verified active on `http://localhost:3344` (`http://morning-call.test`).
- Confirmed full 138-voice multi-lingual catalog `/api/voices` loads and pins starred favourites to `<optgroup label="⭐ Favourites (Pinned to Top)">`.
- Confirmed mid-call dynamic updates (`UpdateSpeak`, `UpdateListen`, `UpdateThink`) and silence watchdog (`5s` default, task auto-extension).
