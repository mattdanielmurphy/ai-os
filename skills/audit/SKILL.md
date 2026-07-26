---
name: audit
description: Perform a token waste audit on the previous conversation transcript.
---

Perform a token waste audit on the previous conversation transcript using the following steps:

1. **Locate the Transcript**: Identify the previous conversation ID from the agent log directory (`agent-logs/`) by looking at the most recent log file's transcript pointer, or find the second most recent directory in `~/.gemini/antigravity-ide/brain/` or `~/.gemini/antigravity-cli/brain/`. Locate the `transcript_full.jsonl` in that directory.
2. **Run Audit Script**: Execute `python3 scripts/audit_transcripts.py <path-to-transcript_full.jsonl>` to analyze the tool calls and calculate cumulative token waste.
3. **Analyze Findings**:
   - Identify the files that were read or edited directly by the orchestrator.
   - Describe which steps contributed most to cumulative token waste (e.g., files read early in a long thread).
4. **Propose Optimizations**: Identify specific ways we can modify the system of rules (e.g., in `.agents/AGENTS.md`) and helper functions (like `subagent.py` or shell wrappers) to minimize direct file reads/writes and enforce cheaper delegation to Deepseek or Claude Code.
