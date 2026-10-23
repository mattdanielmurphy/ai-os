# Live call transcript (Tyler call)

## 13:05 Built it

Asked (voice task): an always-current plain-text transcript of the call with Tyler, Matt on the left channel, Tyler on the right, via Deepgram live.

What I built:
- `scripts/call_transcript.ts` (bun, no deps): ffmpeg reads "BlackHole 16ch", keeps channels 1-2, 16 kHz PCM → Deepgram live (`nova-3`, multichannel, punctuate, smart_format, finals only). Each final line is appended to `~/calls/YYYY-MM-DD-<who>.md` as `[HH:MM:SS] Name: text` (file opened/closed per line, so always flushed). A WAV backup of the streamed audio goes to `~/calls/YYYY-MM-DD-<who>-HHMM.wav`. Reconnects on drops and marks the gap in the file.
- `scripts/call-transcript start [who] | stop | status | tail` wrapper, symlinked to `~/.local/bin/call-transcript`.

---

### Deepgram key needed

No key in env or keychain (an automatic safety check stopped me from searching further). The script reads `$DEEPGRAM_API_KEY` or keychain item `deepgram`. Add once: `security add-generic-password -U -s deepgram -a "$USER" -w` (prompts for the key, nothing printed).

---

### Audio Hijack setup

Audio Hijack 4.5.5 has a Channels block (kill left / kill right). Session: Input Device (mic) → Channels "kill right" → Output Device "BlackHole 16ch"; Application (FaceTime) → Channels "kill left" → same Output Device. Capturing FaceTime doesn't mute it for Matt. Rejected Loopback (works too, but the brief said Audio Hijack) and audiotee (no setup, but two unsynced streams to merge: riskier on a deadline).

---

### Headphones matter

Without headphones the mic hears Tyler from the speakers, so his words also land as "Matt".

---

### What is tested

Tested: capture from BlackHole, WAV backup, file writing, start/stop wrapper, and line parsing against a mock Deepgram server. Not tested: the real Deepgram connection (no key) and the Audio Hijack session (needs Matt's screen).

## 13:10 Review of Matt's Audio Hijack session

His session: FaceTime → Kill Right (Tyler on left), mic → Kill Left (Matt on right), → Recorder → Channels Mono → Default System Output.
- Channels are swapped versus my steps; no change needed, the script takes `--left Tyler --right Matt`.
- Problems: the Mono block merges both channels (kills the speaker split), and the output goes to speakers, not BlackHole, so the script gets no audio. It also plays his own mic out loud.
- Fix: Recorder → Output Device BlackHole 16ch (delete Mono). To still hear Tyler, add a second Output Device (his headphones/system output) wired straight from the FaceTime block, since Audio Hijack takes over the app's audio once it captures it (from memory, not checked on his Mac).
