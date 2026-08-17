# Unified Single-Command Planner (`query_aios.js --plan`)

**Date:** 2026-08-16 21:20  
**Status:** Completed  

## Overview
Consolidated the previous multi-step planning workflow (`generate_planner_prompt.py` followed by `query_proxima.js`) into a unified, single command:
```bash
node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"
```

## Key Improvements
1. **Automatic Context Gathering & Prompt Generation**:
   - `query_aios.js` now natively inspects Git worktree & remote repository information, pulls private repository details for Perplexity's GitHub connector, scans recent `agent-logs/` for keyword matching, and incorporates `AG_CONTEXT.md` plus visual descriptions (`--image-desc`).
   - Automatically writes the prompt artifact to `./tmp/planner_prompt.txt`.
2. **Direct Dispatch**:
   - Sets defaults for planning: model `sonnet` (`claude50sonnetthinking`), timeout 600s, output `./tmp/planner_output.txt`.
   - Directly executes the query via native Tauri AI-OS server (`http://127.0.0.1:3031`) with fallback to Proxima Electron IPC.
3. **Workflow & Rules Synchronization**:
   - Updated `/proxima-planner` workflow at `~/.gemini/config/global_workflows/proxima-planner.md`.
   - Updated `.rules/core_safety.md`, `.rules/gemini_only.md`, and `scripts/compile_dynamic_prompt.py`.
   - Compiled rules into `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md` via `build_rules.py`.
