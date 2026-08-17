# Set Default ai-os Model to Grok Thinking

**Date:** 2026-08-16 21:44  
**Status:** Completed  

## Overview
Configured xAI Grok Thinking (`grok46medium`) as the global default model for ai-os queries and planning.

## Key Changes
1. **[`scripts/query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js)**:
   - Added `grok-thinking` and `grok_thinking` alias mappings to `grok46medium`.
   - Defaulted `rawModel` parameter and fallback to `grok`.
2. **Companion Webview & Engine Backend**:
   - Updated `apps/gemini-companion/src-tauri/engines/perplexity-engine.js` default `modelPref` to `grok46medium`.
   - Updated `apps/gemini-companion/src-tauri/src/server.rs` default model string fallback to `grok46medium`.
3. **Configuration & Rules**:
   - Updated `config/rules_config.json` default high reasoning model to `grok`.
   - Updated `scripts/compile_dynamic_prompt.py` to use `grok` by default.
   - Updated `~/.gemini/config/global_workflows/_plan-with-ai-os.md` and `.rules/core_safety.md`.
   - Recompiled all rule targets (`GEMINI.md`, `CLAUDE.md`, `HERMES.md`, `LEAF.md`).
