# Hermes / agy Subagent Learning-Pass Architecture

## Status: Starred / High Priority Architectural Directive

## Context
When `agy` handles heavy execution subagent tasks, Hermes receives only a final text summary. The detailed tool output, intermediate reasoning, and failure modes are omitted, reducing long-term agent learning.

## Starred Architectural Pattern
1. **Delegate Execution to agy**: Heavy token-hungry execution burns Antigravity quota and keeps main context lean.
2. **Post-Handoff Targeted Learning Pass**: After `agy` returns, Hermes performs a cheap, targeted inspection pass over:
   - The `git diff`
   - The modified source files
   - Execution/error logs
3. **Memory & Skill Encoding**: Encodes durable lessons into local skills/memory without ingesting the full transcript.
