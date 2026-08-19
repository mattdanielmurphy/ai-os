---
title: "Logic Pro MIDI Documentation"
date: "2026-08-03"
conversation_id: "f5f475a1-141d-44ec-89ac-7be5dfffd176"
source: "antigravity"
---

# Logic Pro MIDI Documentation

## User

Create a new log file at `/Users/matt/projects/qwerty-midi-hammerspoon/agent-logs/2026-08-03_02-16_logic-pro-multichannel-voice-summing-notes.md` containing:

```markdown
# Agent Work Log: Logic Pro Multi-Channel Voice Summing Notes

## Summary
Documented DAW / Logic Pro behavior regarding multi-channel MIDI voice summing when routing multiple channels to a single instrument track.

## Findings & Documentation
- **Top Row**: Transmits on MIDI Channel 1 (`topRowChannel = 0`).
- **Bottom Row**: Transmits on MIDI Channel 2 (`bottomRowChannel = 1`).
- **Arpeggiator**: Transmits on MIDI Channel 3 (`arpChannel = 2`).
- **DAW Single-Track Behavior**: In Logic Pro, when a single software instrument track receives all MIDI channels, its internal synthesizer engine sums incoming MIDI note streams by pitch regardless of MIDI channel index. Sending a `Note-Off` for a specific pitch from one channel terminates the voice for that pitch on the synth.
- **Recommended Setup**: Create separate software instrument tracks in Logic Pro assigned to individual MIDI channels (Channel 1, Channel 2, Channel 3) to achieve full independent polyphony across rows.

## Updated Files
- `AG_CONTEXT.md`
- `DEVELOPMENT_JOURNAL.md`
```

Save the file using write_to_file.

---

## Assistant

Created At: 2026-08-03T02:17:04-06:00
Completed At: 2026-08-03T02:17:04-06:00
Created file file:///Users/matt/.gemini/antigravity/brain/f5f475a1-141d-44ec-89ac-7be5dfffd176/2026-08-03_02-16_logic-pro-multichannel-voice-summing-notes.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-03T02:17:05-06:00
Completed At: 2026-08-03T02:17:05-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-03T02:17:06-06:00
Completed At: 2026-08-03T02:17:06-06:00
Message sent to "0e4078ea-8b90-4d18-a813-e304e11b1f06".

The log file has been created at [`/Users/matt/projects/qwerty-midi-hammerspoon/agent-logs/2026-08-03_02-16_logic-pro-multichannel-voice-summing-notes.md`](file:///Users/matt/projects/qwerty-midi-hammerspoon/agent-logs/2026-08-03_02-16_logic-pro-multichannel-voice-summing-notes.md).

---
