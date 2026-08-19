---
title: "Optimizing Agent Prompt Workflow"
date: "2026-08-17"
conversation_id: "c887f39a-3f70-404e-b991-2e2b89fe984b"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">we want our default ai-os model to be grok thinking, make it so please</span>



<span title="Responded at 3:44am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The default model for **ai-os** has been switched to **Grok Thinking** (`grok46medium`):

### Summary of Changes

1. **CLI & Query Defaults ([`scripts/query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js))**:
   - Added aliases `'grok-thinking'` and `'grok_thinking'` mapped to `'grok46medium'`.
   - Defaulted `rawModel` and query fallback to `'grok'`.

2. **Webview Engine & Server Defaults**:
   - Updated default `modelPref` to `'grok46medium'` in [`apps/gemini-companion/src-tauri/engines/perplexity-engine.js`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js).
   - Updated default model in [`apps/gemini-companion/src-tauri/src/server.rs`](file:///Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/src/server.rs).

3. **System Directives & Rules Compiled**:
   - Set `high_reasoning_model_default` to `"grok"` in [`config/rules_config.json`](file:///Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/config/rules_config.json) and [`scripts/compile_dynamic_prompt.py`](file:///Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py).
   - Updated workflow instructions in [`_plan-with-ai-os.md`](file:///Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) and [`.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md).
   - Recompiled all system prompts (`GEMINI.md`, `CLAUDE.md`, `HERMES.md`, `LEAF.md`).
   - Staged, committed, and pushed all changes to remote repository.

---
Thread context reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) | [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">so proxima-planner was so named because we were using proxima; but now we're using ai-os. Rename it to: `_plan-with-ai-os`<br>And remoe anything we have mentioning proxima (query_proxima)</span>



<span title="Responded at 3:23am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

All requested updates and purges are complete:

### Summary of Changes

1. **Workflow Renamed to `_plan-with-ai-os`**:
   - Created [`_plan-with-ai-os.md`](file:///Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) with the standard leading underscore namespace (`_`).
   - Moved deprecated `proxima-planner.md` to `~/.Trash/`.

2. **Purged Legacy `query_proxima` & References**:
   - Moved [`scripts/query_proxima.js`](file:///Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_proxima.js) to `~/.Trash/`.
   - Updated [`scripts/generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) and [`scripts/compile_dynamic_prompt.py`](file:///Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/compile_dynamic_prompt.py) to point to [`scripts/query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js).

3. **System Directives & Rules Compiled**:
   - Updated [`.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md), [`.rules/gemini_only.md`](file:///Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/gemini_only.md), and [`config/rules_config.json`](file:///Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/config/rules_config.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/config/rules_config.json) to reference `/_plan-with-ai-os` and ai-os guardrails.
   - Compiled rules to `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md`.
   - Staged, committed, and pushed all updates.

---
Thread context reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) | [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 16, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">I can't believe this is only occurring to me now!<br>afaik we have our agents instructed to run a perplexity prompt generator and THEN they call a separate query_aios script with that prompt... let's just make it all the single query_aios command! We can generate the prompt and call the planner model all in one.</span>



<span title="Responded at 3:19am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The planner workflow has been unified into a single command with [`query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js):

### Summary of Changes

1. **Unified Planner in [`scripts/query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js)**:
   - Added `--plan "<request>"` (or `--planner`) mode.
   - Automatically gathers Git repository metadata, authenticated GitHub connector repository name, matching historical context from `agent-logs/`, and `AG_CONTEXT.md` (plus optional `--image-desc`).
   - Automatically persists the prompt artifact to `./tmp/planner_prompt.txt`.
   - Defaults to model `sonnet` (`claude50sonnetthinking`), 600s timeout, and output to `./tmp/planner_output.txt`.
   - Dispatches seamlessly via the native Tauri AI-OS server (`http://127.0.0.1:3031`) with fallback to Proxima Electron IPC.
   - Updated [`scripts/query_proxima.js`](file:///Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_proxima.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_proxima.js) to forward cleanly to `query_aios.js` for backward compatibility.

2. **Workflow & Rules Synchronization**:
   - Updated the global workflow [`/proxima-planner`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md) to use `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`.
   - Updated [`.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md), [`.rules/gemini_only.md`](file:///Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/gemini_only.md), and compiled them into `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md` via `build_rules.py`.

### How Agents Run Planning Now:
```bash
node ~/projects/ai-os/scripts/query_aios.js --plan "<user request>"
```
And if recovery is ever needed after a timeout:
```bash
node ~/projects/ai-os/scripts/query_aios.js --recover
```

---
Thread context reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/thread.md) | [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~100k / ~420k 🟡 (fatigue) | 10:45pm | 🟡 Uncommitted (1) | 103 ❓, 28 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/c887f39a-3f70-404e-b991-2e2b89fe984b/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>