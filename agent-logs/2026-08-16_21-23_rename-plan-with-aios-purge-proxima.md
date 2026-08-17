# Rename to `_plan-with-ai-os` & Purge Legacy Proxima References

**Date:** 2026-08-16 21:23  
**Status:** Completed  

## Overview
1. **Renamed Workflow**:
   - Replaced `/proxima-planner` with `/_plan-with-ai-os` at `~/.gemini/config/global_workflows/_plan-with-ai-os.md` using the standard leading underscore namespace (`_`).
2. **Purged Legacy Proxima Planner File**:
   - Moved `scripts/query_proxima.js` and `~/.gemini/config/global_workflows/proxima-planner.md` to `~/.Trash/`.
3. **Rule & Configuration Updates**:
   - Updated `.rules/core_safety.md` to mandate `/_plan-with-ai-os` using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`.
   - Updated `.rules/gemini_only.md` and `config/rules_config.json` to reference `AIOS_GUARDRAILS` / `ai-os & Perplexity Integration Guardrails`.
   - Updated `scripts/compile_dynamic_prompt.py` and `scripts/generate_planner_prompt.py`.
   - Compiled rules to `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md` via `build_rules.py`.
