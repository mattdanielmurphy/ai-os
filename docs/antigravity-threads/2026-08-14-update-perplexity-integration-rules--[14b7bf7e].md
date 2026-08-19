---
title: "Update Perplexity Integration Rules"
date: "2026-08-14"
conversation_id: "14b7bf7e-c1dd-4e83-af78-e894f1715357"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please refine the Perplexity file upload rules in:

1. `/Users/matt/projects/ai-os/.rules/gemini_only.md`:
Update `## Proxima & Perplexity Integration Guardrails`:
```markdown

## Proxima & Perplexity Integration Guardrails
- **Perplexity File Upload & Context Policy**:
  - **Codebase & Text Files**: NEVER pass codebase or text files in the `files` argument to `proxima:ask_perplexity`. ALWAYS rely on the authenticated GitHub connector or embedded text.
  - **Screenshots & Visual Assets**: Upload quota is 50/week on a rolling window. If remaining upload quota is > 25 AND a screenshot contains complex visual elements that cannot be easily/accurately transcribed into text, passing the image file to `proxima:ask_perplexity` is permitted. If quota is <= 25 or the visual content is easily describable, the orchestrator MUST act as the vision provider and describe it textually in the prompt instead of uploading.
- **Disabled Proxima Providers**: NEVER call `proxima:ask_claude` or `proxima:ask_chatgpt`.
- **Async Recovery on Timeout**: If `proxima:ask_perplexity` times out after 3 minutes, do NOT switch providers or abandon the query. Immediately run `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --recover --output ./tmp/planner_output.txt --timeout 300` to retrieve the finished output.
```

2. `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`:
Update the Vision Provider & File Upload section accordingly.

Make these updates now.

</span>



<span title="Responded at 3:26am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The Perplexity file upload rules have been updated in both locations as requested.
1.  **`/Users/matt/projects/ai-os/.rules/gemini_only.md`**: Updated the *Proxima & Perplexity Integration Guardrails* section.
2.  **`/Users/matt/.gemini/config/global_workflows/proxima-planner.md`**: Updated the *Vision Provider & File Upload* rules and the specific Perplexity policy within the workflow.
No further action is required.

</span>



</span>

</span>