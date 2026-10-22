# Banner polish, continued (2026-10-22)

## 14:15 Try-this command rule + Esc/Stop choice

Matt asked: until action buttons exist, whenever an agent says "try this now" / "look at this", give a terminal command that summons the behaviour.

---

### Rule saved globally

- Added to `.rules/core_safety.md` ("Every Word Costs Matt" section), recompiled with `build_rules.py` (CLAUDE.md, LEAF.md, GEMINI/Codex globals), and added a line to `~/.claude/CLAUDE.md`. The coordinator already saved it to project instructions.
- Undo: revert this commit and delete the line in `~/.claude/CLAUDE.md`.

---

### Esc Stop choice

Still open from the last thread: Matt asked for "Esc esc stop" → "Esc: stop". Collapsing it to one key would merge "not now" and "stop", so two options were offered:
- (a, recommended) Esc = not now; Stop only via the banner's Stop button. Snooze chips cover "later".
- (b) Shift-Esc = stop.
Nothing changed in code yet; waiting for his pick.

---

### Summon banner command

`~/.hammerspoon/bin/claude-control ask "demo banner" 3 --thread cmsg_01CUPXyY9oUwKVDFREVDpYDrUCSmGtvVpWokq7BSXKw8wz` shows the full banner for 3 s, with click-to-thread. Add `--light` for the pill. Matt running it himself is his own input, so no clearance needed. Click-to-thread is still untested.
