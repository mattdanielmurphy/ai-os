
## 22:15 Speechify end-to-end run (reel 004)
- Found: the build cache key ignored the TTS provider, so the first "Speechify" build silently reused old Deepgram audio. Key now starts `speechify-v2|`.
- Found: `...` inside a line was sent as text (0.1–0.18s token, barely a pause). `tts.ssml` now turns it into `<break time="400ms"/>`; beat joins stay 500ms.
- Checked on the new take: 100% of script heard, real gaps 0.40–0.51s, every clip starts/ends with ~0.3s silence (cuts at mid-gap), so no word edges clipped. `test.sh` passes (ducking works).
- Undo: revert the commit; old audio tags remain in git history.
