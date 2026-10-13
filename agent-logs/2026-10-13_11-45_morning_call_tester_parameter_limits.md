# Morning Call Tester: Deepgram Voice Agent Parameter Bounds & Error Isolation

- **Date:** 2026-10-13
- **Focus:** Isolating and eliminating silent Voice Agent startup failures caused by out-of-bounds TTS and STT parameters (`speed`, `eot_threshold`, `eager_eot_threshold`).

## Root Cause Analysis
1. **TTS Speed Limit Exceeded (`SPEAK_REQUEST_FAILED` -> `FAILED_TO_SPEAK`):**
   - Deepgram Flux TTS strictly enforces a maximum speed limit of `1.50` (range: `0.50`–`1.50` in `0.05` increments). Aura/Aura-2 models enforce `0.70`–`1.50`.
   - The UI slider previously permitted speeds up to `2.50`. When dragged above `1.50` (e.g. `1.75`), Deepgram rejected all speak synthesis requests with `SPEAK_REQUEST_FAILED`, escalated to `FAILED_TO_SPEAK`, and terminated the WebSocket connection.

2. **STT EOT Threshold Out of Bounds (`INVALID_SETTINGS`):**
   - Deepgram strictly enforces `eot_threshold` between `0.50` and `1.00`.
   - Deepgram strictly enforces `eager_eot_threshold` between `0.30` and `0.90` (and `≤ eot_threshold`).
   - The UI previously allowed `eot_threshold` down to `0.10`. In the normal Chrome window, `localStorage` had rehydrated an EOT value below `0.50` (e.g. `0.48`), causing Deepgram to immediately reject settings on handshake with `INVALID_SETTINGS: eot_threshold must be between 0.5 and 1, inclusive`. In private/incognito windows, `localStorage` was absent, defaulting to `0.58` which passed validation.

3. **Silent Error Swallowing:**
   - When Deepgram returned `{ type: "Error" }` or closed the WebSocket with `status: "deepgram_closed"`, `handleServerJson()` did not catch or alert on these events, leaving the UI hanging silently on `CONNECTING`.

## Fixes Implemented
1. **Slider & Input Constraints (`public/index.html`):**
   - Clamped `speedSlider` and `speedNum` to `min="0.50"`, `max="1.50"`, `step="0.05"`.
   - Clamped `eotSlider` and `eotNum` to `min="0.50"`, `max="1.00"`, `step="0.01"`.
   - Clamped `eagerEotSlider` and `eagerEotNum` to `min="0.30"`, `max="0.90"`, `step="0.01"`.

2. **Server-Side Sanitization & Clamping (`server.ts`):**
   - Sanitized and clamped `speed` (0.50–1.50, rounded to 0.05 step), `expressivity` (-2 to 2), `eot_threshold` (0.50–1.00), and `eager_eot_threshold` (0.30–min(0.90, eot)) in both initial `buildDeepgramSettings` and mid-call `UpdateSpeak`/`UpdateListen` payloads.

3. **Client-Side Storage & Object Sanitization (`public/app.js`):**
   - Clamped all loaded values in `loadSettingsFromStorage()` so corrupted or legacy `localStorage` entries cannot send invalid values to Deepgram.
   - Clamped values in `getSettingsObject()`.

4. **Transparent Error Surfacing (`public/app.js`):**
   - Added explicit handlers for `data.type === "Error"` and `msg.status === "deepgram_closed"`, surfacing alerts and transcript warning badges with the exact upstream error message and code.

## Verification
- Verified live end-to-end WebSocket connection to Deepgram from the active browser tab.
- Confirmed `SettingsApplied`, proactive initial greeting dialogue, and continuous binary Linear16 PCM audio chunk streaming.
