---
name: ai-os-audit
description: Run token waste audits on agent conversation transcripts using agy's audit_transcripts.py. Identifies inefficient tool usage patterns and delegation failures.
version: 1.0.0
metadata:
  hermes:
    tags: [ai-os, audit, token-efficiency, debugging]
---

# AI-OS Token Waste Audit

Run token waste audits on past agent conversation transcripts to identify inefficiencies, excessive direct file reads, and missed delegation opportunities.

## When to Use

- After a long or expensive agent session to learn what went wrong
- When investigating why a session blew through its token budget
- Periodically, to keep the system's rules and workflows sharp
- When the user asks "audit that last session"

## Basic Usage

### Audit the most recent transcript (auto-discovery)

```bash
cd ~/projects/ai-os
python3 scripts/audit_transcripts.py
```

This auto-discovers the most recent transcript from:
- `~/.gemini/antigravity-ide/brain/<conv_id>/.system_generated/logs/transcript.jsonl`
- `~/.gemini/antigravity-cli/brain/<conv_id>/.system_generated/logs/transcript.jsonl`

### Audit a specific transcript

```bash
cd ~/projects/ai-os
python3 scripts/audit_transcripts.py /path/to/transcript.jsonl
```

## What the Audit Reports

The script categorizes every step in the transcript:
1. **Direct reads** — Files read by the orchestrator (expensive)
2. **Direct writes** — Files written directly via heredocs/redirection
3. **Delegated calls** — Edits routed through mechanical_editor.py or Claude Code (cheap)
4. **Other calls** — shell commands, ripgrep searches, etc.

It also calculates **cumulative token waste** — the compounding cost of reading large files early in a long conversation.

## Follow-Up Actions

After an audit reveals issues:

1. **High direct-read count** → Add more aggressive rules to route file reading through subagents
2. **Low delegation rate** → Verify the `$AIOS_DELEGATE` toggle and mechanical_editor.py availability
3. **Token waste spikes** → The session was too long; branch earlier next time
4. **Grep without directory filters** → Add file-type or subdirectory constraints to search patterns

## Note

This script is agy's domain (it reads Antigravity/Gemini transcript formats), but Hermes can call it via terminal to get the report. The findings inform both systems' rule improvements.
