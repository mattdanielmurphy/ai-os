# 2026-10-24 four small tasks (coordinator relay)

## 07:40 Chips cap, publish, call transcripts, QWERTY step 3

### Chip cap
- Premise was wrong: hud_slots.json reserved 3 chips (276px), not 4. A 4th chip (ends y=440) overlaps piano_card (top y=417 on the 939px laptop screen). Tried 4; the hud_layout test failed, so reverted to 3.
- `claude_notify.lua`: laptop-only (1 screen) caps stacked chips at the knob `chips.maxLaptop` (default 3, ⌃⌥⌘T "Claude notification chips"); extras wait in the queue. Two or more screens: up to 6 as before.
- hud_layout_test passes. Hammerspoon reloaded fine. Real stacking untested.
- Undo: revert commits in ~/.hammerspoon.

### Auto-publish
- Only uncommitted work in ~/.hammerspoon was bin/ship-public (adds modules/claude_pill.lua to the export list); committed.
- Public copy was already caught up: the pre-push hook ran ship-public for each of my pushes (publishes "Update from 28966de" etc.). Exact original failure not reproduced (old log overwritten); likely the missing claude_pill.lua in the export list. Final push published "Nothing new" = in sync.

### FaceTime transcripts
- New `modules/call_transcript.lua`, registered in init.lua, listed MATT_ONLY, unit test `tests/call_transcript_test.lua`.
- Detects a call as a FaceTime window titled with a name (idle window is "FaceTime"). Starts after 2 polls, stops after 4 polls with no call (poll 3s). Knobs in ⌃⌥⌘T "Call transcripts". Only stops transcripts it started.
- Uses `--left <name> --right Matt` as asked (matches existing transcript file: left=Tyler, right=Matt). Shows an info chip when recording starts.
- Untested on a real call: the window-title guess is the risk. If it doesn't start, check `hs -c` FaceTime window titles during a call.
- 2-minute silence reminder untouched (in the tool).

### QWERTY step 3
- Installed VST3 (Oct 19 09:28) is byte-identical to the build from commit 1cb3a04 (worktree elastic-satoshi-e86373). Verified by checksum.
- Note: the AU component installed is old (Oct 16); Ableton should use the VST3.
- Local branch claude/project-thread-3er5op sits at 6c183ca; step 3 exists only on origin.
- Not touched Ableton.
