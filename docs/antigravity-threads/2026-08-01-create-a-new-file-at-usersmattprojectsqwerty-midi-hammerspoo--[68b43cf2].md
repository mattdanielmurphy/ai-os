---
title: "Create a new file at `/Users/matt/projects/qwerty-midi-hammerspoon/TOOL_ISSUES.md` recording tool execution issues encountered during agent tasks:"
date: "2026-08-01"
conversation_id: "68b43cf2-c4a7-470d-81e0-0610849c6257"
source: "antigravity"
---

# Create a new file at `/Users/matt/projects/qwerty-midi-hammerspoon/TOOL_ISSUES.md` recording tool execution issues encountered during agent tasks:

## User

Create a new file at `/Users/matt/projects/qwerty-midi-hammerspoon/TOOL_ISSUES.md` recording tool execution issues encountered during agent tasks:

1. **agymcp JSON Schema Parameter Mismatch**:
   - `agymcp` tools (`agy`, `agy_start`) require uppercase `PROMPT` as a required parameter rather than standard camelCase or lowercase `prompt` or array `Arguments`. Passing nested array parameters causes a Pydantic `PROMPT` missing validation error.
2. **agymcp Default Model Fallback**:
   - Omitting `model` parameter defaults `agymcp` to `Gemini 3.5 Flash (Low)` instead of `gemini-3.6-flash-low` or `gemini-3.1-pro-high`. `gemini-3.5-flash-low` is strictly prohibited by policy and must be avoided.
3. **agymcp Detached Mode vs Execution**:
   - `agymcp:agy_start` launches an asynchronous background tmux job that does not directly edit files in the caller's active turn unless polled or synchronized.

Ensure the document is cleanly formatted in markdown as an ongoing tool issues log.

---
