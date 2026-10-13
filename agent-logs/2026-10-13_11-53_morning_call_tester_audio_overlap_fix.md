# Morning Call Tester: Eliminate Audio Overlap & Queue Wraparound Bug

- **Date:** 2026-10-13
- **Focus:** Isolating and eliminating overlapping speech chunks during agent utterances and greetings in `tools/voice-agent-tester`.

## Root Cause
- In `playPcmChunk()` in `public/app.js`:
  ```javascript
  if (startTime < now || startTime > now + 1.0) {
    startTime = now + 0.02;
  }
  ```
- Because Deepgram synthesizes greetings and conversational turns faster than real-time, dozens of audio chunks (~80ms each) are pushed over the WebSocket within the first 50ms of a turn.
- As soon as the queued audio timeline reached >1.0s ahead of `audioCtx.currentTime` (typically by chunk 13), the condition `startTime > now + 1.0` evaluated to `true`.
- This erroneously reset `startTime` back to `now + 0.02`, forcing all subsequent chunks in the sentence to play simultaneously on top of the opening chunks.

## Fix
1. **Removed Erroneous Lookahead Reset:**
   - Changed scheduling to:
     ```javascript
     if (startTime < now) {
       startTime = now + 0.02;
     }
     ```
   - Chunks now queue strictly in chronological sequence (`nextPlayTime = startTime + duration`), enabling seamless playback of any length without overlapping.

2. **Immediate Barge-In & Interruption Handling:**
   - Implemented `stopAllAgentAudio()` tracking `activeAudioSources`.
   - Wired `stopAllAgentAudio()` into `UserStartedSpeaking`, `startCall()`, and `endCall()`. When the user begins speaking, in-flight agent audio cuts off immediately.
