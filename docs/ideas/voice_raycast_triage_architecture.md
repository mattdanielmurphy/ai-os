# Voice & Raycast Triage Architecture (`ai-os`)

## 1. Overview & Vision
Transform `ai-os` into a seamless, voice-enabled macOS command triage hub that routes natural language and spoken queries through an optimal execution tier:
- **Tier 1: Fast System Control (< 50ms):** Direct AppleScript / Hammerspoon triggers for device state (lights, media, volume).
- **Tier 2: Fast Intent & Search (~300ms):** High-speed LLM (Gemini 2.5 Flash / Groq / LiteLLM) parsing for macOS Spotlight file/app lookups (`mdfind`, `open`).
- **Tier 3: Full Agentic Tasks:** Complex, multi-step tasks routed directly to `agy` or `hermes` CLI with rule enforcement.

## 2. Speech-to-Text (STT): Microsoft Transcribe (`microsoft/mai-transcribe-1.5`)
For speech recognition, we align with the `microsoft/mai-transcribe-1.5` architecture (Azure Cognitive Speech / MAI Transcribe):

### STT Pipeline Options
1. **Azure Speech SDK / Cognitive REST API (BYOK - Recommended):**
   - Transcribes microphone input directly using your Azure Speech resource key.
   - Low latency, multi-language support, high accuracy on domain terms.
   - Endpoint: `https://<region>.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1`
2. **Local Audio Capture & Transcribe (`scripts/listen_stt.py`):**
   - Micro-record audio stream via `sox` or macOS `rec` / `pyaudio`.
   - Send raw WAV stream to Microsoft MAI Transcribe endpoint.
   - Return clean string output directly into `scripts/triage_router.py`.

## 3. Text-to-Speech (TTS): Microsoft Neural TTS
- **Provider:** Microsoft Cognitive Services / `edge-tts` (wrapping Microsoft's high-quality Neural Speech voices like `en-US-AvaNeural` / `en-US-AndrewNeural`).
- **Integration Layer:** `scripts/speak_response.py`
  - Accepts output text from `triage_router.py`.
  - Generates audio stream asynchronously.
  - Plays back using macOS `afplay`.

## 4. End-to-End Voice Flow

```
[ Mic Audio Stream ]
       │
       ▼
[ Microsoft Transcribe (mai-transcribe-1.5 API / Azure STT) ]
       │ (Transcribed Text)
       ▼
[ ai-os Triage Router (scripts/triage_router.py) ]
       │
       ├─► Fast-Path Regex (Lights, System Audio, Spotify)
       ├─► Fast Intent Search (Spotlight lookups, mdfind, open file)
       └─► Agentic Escalation (agy / hermes tasks with AGENTS.md rules)
       │
       ▼
[ Microsoft Neural TTS Engine (Azure / edge-tts) ]
       │ (Spoken Audio Output)
       ▼
🔊 [ macOS Speakers (`afplay`) ]
```

## 5. Raycast Launcher Integration
- **Script Installed:** [`/Users/matt/Documents/raycast/ai-os-triage.sh`](file:///Users/matt/Documents/raycast/ai-os-triage.sh)
- **Workflow:** Hotkey in Raycast $\rightarrow$ launches script or activates voice listening $\rightarrow$ executes action & speaks result.
