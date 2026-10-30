# Readthrough publishes itself (2026-10-29)

## 14:00 Readthrough: automatic and free for agents

### What changed

Writing a details file now publishes its Readthrough through a hook. Agents no longer run the command.

### Voice only on play

Publishing makes no audio. Each paragraph is voiced the first time someone presses play, then cached on the VPS for everyone.

### Undo

Remove the readthrough_autopublish entry from PostToolUse in ~/.claude/settings.json.
