# Call transcript drop: 2026-10-24

## 16:20 Why it stopped, and the fix

Matt's call with Tyler stopped transcribing at 15:10:35 and stayed off until 16:13:45 (restarted by hand). The coordinator asked to get it running, find the cause, and make it restart itself and alert him.

---

### FaceTime Settings misread as a call

Hammerspoon's console showed:

```
15:10:23 call_transcript: start General -> 0 already running (pid 52535)
15:10:38 call_transcript: stop General -> 0
```

The FaceTime auto start/stop watcher (~/.hammerspoon/modules/call_transcript.lua, built Oct 24, never tested on a real call) treats any FaceTime window not titled "FaceTime" as a call. The FaceTime Settings window is titled after its pane ("General"), so it was taken as a call with "General". The tool answered "already running" with exit 0, so the watcher believed it owned the transcript. When Settings closed, 12 s later it ran `call-transcript stop` and killed the hand-started transcript.

---

### Watcher fixes

- Ignores Settings-type window titles: General, Calls, Settings, Preferences (plus FaceTime variants). Tests added; all pass.
- If `start` says "already running", the watcher doesn't take ownership, so it never stops a transcript it didn't start.
- Hot-swapped into running Hammerspoon (no reload, nothing on screen).
- Still untested on a real FaceTime call: the live call window's title is assumed, not seen.

---

### Auto-restart and alert

`call-transcript start` now runs the transcriber under a small zsh supervisor. If it exits for any reason other than `call-transcript stop` (crash, audio device lost, killed), Matt gets a toast with sound and it restarts in 2 s. Five quick deaths in a row (each under 15 s) -> a FAILED toast and it stops retrying (e.g. no Deepgram key, no BlackHole device).

The transcriber also toasts if Deepgram disconnects and isn't back within 10 s (quick reconnects stay silent).

Tested with a stub transcriber in a scratch HOME: kill -> restart + alert; crash loop -> gives up after 5; stop -> child gets SIGINT, supervisor exits.

---

### Live swap and lost audio

At 16:17:39 the live transcript was restarted under the supervisor (gap ~3 s). (Corrected below: the hour was not lost; Audio Hijack had it.)

Undo: revert the commits in ai-os (scripts/call-transcript, scripts/call_transcript.ts) and ~/.hammerspoon, then copy the scripts back into ~/.local/share/call-transcript/.

## 16:35 Lost hour recovered from Audio Hijack

Matt pointed out Audio Hijack was recording the whole call (`~/Music/Audio Hijack/20261024 1303 Recording.mp3`, started 13:03:58). I was wrong that the hour was lost.

---

### Transcribing the gap

Cut 15:09:30-16:14:15 from the recording (`~/calls/recovery/seg.mp3`) and sent it to Deepgram prerecorded (nova-3, multichannel, utterances) with the new `scripts/call_recover.ts`. Left channel = Tyler, right = Matt, confirmed against the overlapping live lines. 1006 lines for 15:10:36-16:13:45.

Clock alignment: matching phrases in the overlap ("incentivize community members", "cross compatible") showed the recording's utterance starts ~15 s earlier than the live stamps (live stamps when a phrase is finalised, near its end). Shifted by +15 s; good to about ±5 s, noted in the inserted marker.

---

### Merge when the call ends

Splicing now would race the live transcriber appending to the same file, so a detached waiter (`~/calls/recovery/splice.sh`, log `splice.log`) polls every 30 s. When the transcript stops it inserts `gap.md` just before the `session started 16:13:45` marker (backup at `.md.bak`), refreshes the Obsidian copy, and sends a toast. Tested the insert on a copy.

Risk: if the transcript is never stopped (e.g. Mac sleeps with it running), the merge waits up to 12 h then runs anyway.
