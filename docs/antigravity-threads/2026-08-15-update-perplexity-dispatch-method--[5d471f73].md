---
title: "Update Perplexity Dispatch Method"
date: "2026-08-15"
conversation_id: "5d471f73-80a2-434c-9980-02d63b3db190"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 80px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update the following files:

1. `/Users/matt/projects/ai-os/.rules/core_safety.md`:
In "Strict Planner / Workflow Immediate Dispatch":
Update lines 35-39:
- Instead of instructing to query Perplexity via `proxima:ask_perplexity`, instruct to query Perplexity via background script `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600`.
- Update the dispatch rule to emphasize that planning queries MUST be run via `query_proxima.js` in the background (using `run_command` with `WaitMsBeforeAsync: 500`) so the agent remains unblocked and avoids the 3-minute MCP tool deadline timeout.

2. `/Users/matt/projects/ai-os/.rules/gemini_only.md`:
In "Proxima & Perplexity Integration Guardrails":
Update the instructions so that Perplexity planner queries are always dispatched via `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600` instead of calling `proxima:ask_perplexity`.

3. `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`:
Update Step 4:
Replace the direct `proxima:ask_perplexity` MCP tool call instruction with running:
`node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600`
using `run_command` (with `WaitMsBeforeAsync: 500`). Antigravity will notify the agent when the task completes.

4. `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`:
Update lines 110-117 (the printed execution instructions):
Instruct to execute `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600` via `run_command`.

Make the edits directly and cleanly.

</span>



<span title="Responded at 7:09am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates have been successfully applied to the following files:

1.  [`core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md): Updated the "Strict Planner / Workflow Immediate Dispatch" rule to enforce usage of `query_proxima.js` via `run_command` and emphasize background execution.
2.  [`gemini_only.md`](file:///Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/gemini_only.md): Updated the "Proxima & Perplexity Integration Guardrails" to direct all planning queries to the `query_proxima.js` script.
3.  [`proxima-planner.md`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md): Updated Step 4 to instruct running the `query_proxima.js` script via `run_command` in the background.
4.  [`generate_planner_prompt.py`](file:///Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py): Updated the printed execution instructions to reflect the new command-line dispatch requirement.

</span>



</span>

</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">



**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~40k | 2:10am 🔴 (expired) | ~40k / ~403k 🟢 (optimal) | 108, 20 🔬, 16 📤 |

</span>