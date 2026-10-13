# Morning Call Voice Tester & Persona Playground

Interactive testing workbench for morning wake-up call personas powered by Deepgram Voice Agent API (`wss://agent.deepgram.com/agent`).

## Local Dev URL
- Puma-dev: **[http://morning-call.test](http://morning-call.test)** (mapped to port `3344`)
- Direct: **[http://localhost:3344](http://localhost:3344)**

## Key Deepgram Voice Agent Parameters

### 1. Speaking Speed / Rate
- **Parameter**: `agent.speak.provider.speed`
- **Range**: `0.5` to `1.5` (default: `1.0`, steps of `0.05`).
- **Pacing Sweet Spot**: `1.25` – `1.35` provides rapid-fire, high-energy military cadence without clipping or sounding distorted.

### 2. Pauses & Turn-Taking Responsiveness
- **End-Of-Turn Detection (`agent.listen.provider.eot_threshold`)**:
  - Range: `0.5` – `1.0` (default: `0.7`).
  - Set to `0.55` – `0.60` to make the drill instructor interrupt hesitation and respond immediately when you stop speaking.
- **Eager Turn Detection (`agent.listen.provider.eager_eot_threshold`)**:
  - Range: `0.3` – `0.9` (default: disabled).
  - Set to `0.40` – `0.45` to start the LLM think cycle while you are finishing your words, saving 300–500ms of audio turn latency.
- **Text-Level Pause Suppression (Prompt Engineering)**:
  - Deepgram Flux TTS pauses at punctuation (commas, semicolons, ellipses `...`).
  - Instruct the persona to avoid commas and ellipses, keeping lines short, punchy, and punctuated with exclamation marks and dashes.

---

## Telegram Phone Call Feasibility & Morning Call Architecture

1. **Can Telegram Bots Call You?**
   - **No**: The official Telegram Bot API has no support for VoIP voice calls.
   - **UserBot Workaround**: Automating a personal Telegram account via MTProto + `PyTgCalls` can initiate calls, but is brittle and violates Telegram's automated account policies.
   - **Telegram Voice Notes**: If keeping within the Telegram Bot API, the bot can send voice notes (`sendVoice`) via TTS and accept user voice notes with STT.

2. **The Production Solution for Real Morning Phone Calls**:
   - **Twilio Voice / SIP Trunking**: Calls Matt's actual phone number `[REDACTED-PHONE]` over standard cellular. Twilio Media Streams connects live audio directly to Deepgram Voice Agent WebSocket over bidirectional PCM audio.
   - **Web / Companion Alarm**: A single-tap WebRTC call link sent via Telegram morning notification that opens the call in Safari/PWA.
