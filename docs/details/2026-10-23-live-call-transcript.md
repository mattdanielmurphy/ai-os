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

## 13:16 Every Claude knows about the call

Asked: any Claude he asks mid-call should know a transcript is live, weigh recent lines most, and the transcript should be saved after the call.

---

### Hook on every prompt

New UserPromptSubmit hook `scripts/hooks/live_call.py` (installed copy in `~/.local/share/call-transcript/`, registered first in `~/.claude/settings.json`). While `call-transcript` runs, every prompt in any Claude Code session or project thread on the Mac gets: "LIVE CALL IN PROGRESS", the transcript path, an instruction to assume the question is about the call, and the last 60 lines. For 3 h after a call it points at the saved copy. Tested by running it directly; not yet seen firing inside a live session (hooks may only load in sessions started after the change).

---

### Saved after the call

`call-transcript stop` copies the transcript to Obsidian `Calls/` (QMD indexes the vault, so later searches find it).

---

### Coordinator gap

The project coordinator runs in the cloud and can't read `~/calls`; it would need to hand the question to a thread on the Mac. Voice Claude can read the file through the Mac connector.

## 13:20 Hang-up reminder

Asked: eventually start/stop on its own with a FaceTime call to Tyler (just a small notification); for now, remind him to stop it when he hangs up.

---

### How the reminder works

While recording, every 10 s the script checks: is FaceTime still running, and has anyone spoken in the last 120 s (`--silence <sec>` to change)? If either fails, one amber toast via `claude-notify`: "Call over? Stop the transcript". It re-arms when someone speaks again. Tested with a 5 s threshold (one test toast appeared on his screen). The FaceTime-closed path is untested; FaceTime usually stays open after hanging up, so silence is the main trigger. A quiet stretch mid-call also triggers it.

---

### Auto start/stop next

Not built: detecting a FaceTime call to Tyler starting/ending (likely via FaceTime's window title or call-state logs) and starting/stopping on its own with a small toast.

## 13:30 Simpler setup + voice effects

Asked: simplify using the FaceTime block's "Include audio input + Split between channels" (input left, app right); and add effects to his voice that Tyler hears, while the transcriber still gets the dry mic.

---

### Why not the one-block setup

"Include audio input" records whatever FaceTime's microphone is. Once FaceTime's mic is the effects device, that channel would be wet, so the transcriber would get effected audio. Without effects, the one-block setup is fine (left = Matt, right = Tyler, matching the script's defaults, no flags needed).

---

### Effects routing

- Loopback: new device "Mic FX" (default Pass-Thru, nothing else).
- Audio Hijack FX session: Input Device (mic) → effects → Output Device "Mic FX".
- FaceTime: Video menu → Microphone → Mic FX. Tyler hears the effects.
- Transcription session: Input Device (dry mic) → left, FaceTime block (Include audio input OFF) → right → Output Device BlackHole 16ch (+ his Mono → speakers branch for listening). Then `call-transcript start` with no flags.
Untested; from Audio Hijack/Loopback knowledge, not run on his Mac. FaceTime's own voice processing may soften some effects.
