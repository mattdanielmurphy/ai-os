---
title: "Update Model Default Settings"
date: "2026-08-17"
conversation_id: "c4de88bf-3b9b-45a7-b3f7-6d0e37358b4a"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please make the following edits:<br><br>File 1: `/Users/matt/projects/ai-os/scripts/query_aios.js`<br>Replace line 266:<br>`        const requestedModel = (rawModel || 'grok').toLowerCase();`<br>with:<br>`        const requestedModel = (rawModel || 'gemini').toLowerCase();`<br><br>And replace line 272:<br>`    const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'grok' : 'default');`<br>with:<br>`    const modelDisplay = rawModel || (baseProvider === 'perplexity' ? 'gemini' : 'default');`<br><br>File 2: `/Users/matt/projects/ai-os/.rules/core_safety.md`<br>Replace line 55:<br>`- **Workflow**: Immediately run the single planner command via \`run_command\` (using \`node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"\`) with \`WaitMsBeforeAsync: 500\`. This is a **unified single-step command** that automatically: inspects Git context, reads agent logs, generates \`./tmp/planner_prompt.txt\`, dispatches to Perplexity (Grok Thinking), and writes the completed plan to \`./tmp/planner_output.txt\`. There is NO separate \`generate_prompt.py\` step — do NOT run any such script.`<br>with:<br>`- **Workflow**: Immediately run the single planner command via \`run_command\` (using \`node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"\`) with \`WaitMsBeforeAsync: 500\`. This is a **unified single-step command** that automatically: inspects Git context, reads agent logs, generates \`./tmp/planner_prompt.txt\`, dispatches to Perplexity (Gemini 3.7 Flash Thinking), and writes the completed plan to \`./tmp/planner_output.txt\`. There is NO separate \`generate_prompt.py\` step — do NOT run any such script.`<br><br>And replace line 56:<br>`- **Strict Perplexity Dispatch & Fallback Policy**: When \`/_plan-with-ai-os\` is invoked, the orchestrator MUST ONLY dispatch via \`run_command\` (using \`node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"\`). Never use Gemini 3.1 Pro for planning for any reason. Fall back to \`agy\` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to \`agy\`, ALWAYS use \`Gemini 3.7 Flash (High)\` for planning, NEVER 3.1 Pro.`<br>with:<br>`- **Strict Perplexity Dispatch & Fallback Policy**: When \`/_plan-with-ai-os\` is invoked, the orchestrator MUST ONLY dispatch via \`run_command\` (using \`node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"\`). Defaults to Gemini 3.7 Flash Thinking on Perplexity. Never use Gemini 3.1 Pro for planning for any reason. Fall back to \`agy\` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to \`agy\`, ALWAYS use \`Gemini 3.7 Flash (High)\` for planning, NEVER 3.1 Pro.`<br><br>And line 80:<br>`- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using \`flash_lite\` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to \`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model grok\` (ai-os Grok Thinking) by default, with \`Gemini 3.7 Flash (High)\` as a fallback (via \`agymcp:agy\` only if primary quota is 0). Do NOT use 3.1 Pro.`<br>with:<br>`- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using \`flash_lite\` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to \`node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model gemini\` (ai-os Gemini Flash Thinking) by default, with \`Gemini 3.7 Flash (High)\` as a fallback (via \`agymcp:agy\` only if primary quota is 0). Do NOT use 3.1 Pro.`</span>



<span title="Responded at 9:48am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested changes have been successfully applied:

*   **File:** [`/Users/matt/projects/ai-os/scripts/query_aios.js`](file:///Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/query_aios.js) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/query_aios.js)
    *   Updated default model to `gemini` on lines 266 and 272.
*   **File:** [`/Users/matt/projects/ai-os/.rules/core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md)
    *   Updated workflow and policy documentation to reflect `gemini` as the default model and updated the related planning/fallback rules as specified in your request.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~40k / ~440k 🟢 (optimal) | 4:50am | 🟡 Uncommitted (3) | 95 ❓, 30 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/c4de88bf-3b9b-45a7-b3f7-6d0e37358b4a/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>