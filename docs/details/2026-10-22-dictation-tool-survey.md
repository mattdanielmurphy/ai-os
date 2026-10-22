# Dictation tool survey (2026-10-22)

## 10:20 Is TypeWhisper the best Mac dictation tool?

Matt asked (via coordinator) whether TypeWhisper is the best option. He loves live streaming text while still
speaking (Claude's dictation is his benchmark), dislikes TypeWhisper's "Thank you." hallucination on silent
triggers and its UX polish, and floated building his own as part of his mac-utilities suite.

What I did: web searches on streaming-capable Mac dictation apps; checked /Applications (TypeWhisper,
Spokenly and Whisper.app are installed). Nothing installed or tried yet.

---

### Superwhisper realtime pick

Superwhisper has a "Realtime" option for its Parakeet models (local) and Nova cloud models: text shows while
recording, then a final pass runs on the full recording. Source: Superwhisper feedback board
(https://superwhisper.userjot.com/board/p/live-text-functionality). Local Parakeet should avoid Whisper's
"Thank you." silence hallucination (that comes from Whisper's training on subtitled video; Parakeet is a
different model family). Unverified: which plan tier unlocks realtime, and how live text looks in practice.
Paid app with a trial.

---

### Aqua Voice cloud streaming

Aqua Voice has a Streaming Mode: text flows on screen as you speak (~850 ms per vendor). Cloud only;
some sources say realtime needs the top tier. Most polished streaming UX, but audio leaves the Mac.
Sources: https://aquavoice.com/blog/speech-to-text-mac-2026 and
https://www.promptquorum.com/power-local-llm/aquavoice-review

---

### Parrot free local

Parrot (https://github.com/banyudu/parrot): free menu bar app, local, real-time streaming with
Parakeet-TDT / Qwen3-ASR / Voxtral. Rougher UX; good base if Matt ever does build his own.
Also seen: sebsto/wispr (Parakeet Realtime 120M), moona3k/macparakeet (no streaming confirmed).

---

### Build-your-own rabbit hole

A dictation app means mic capture, streaming ASR, VAD, text injection into any app, hotkeys, HUD. Months of
polish to match Superwhisper. Smallest step: try Superwhisper realtime with Parakeet for a day. Recorded the
idea in IDEAS.md anyway.

Not listed: Wispr Flow (cloud, live text not confirmed), VoiceInk (Whisper-based, live preview unclear),
MacWhisper (file-transcription focus). Spokenly is installed but its streaming wasn't confirmed.

Undo: nothing changed on the Mac; the IDEAS.md entry can be deleted.
