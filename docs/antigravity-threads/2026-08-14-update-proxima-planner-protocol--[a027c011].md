---
title: "Update Proxima Planner Protocol"
date: "2026-08-14"
conversation_id: "a027c011-0975-4c7c-b46a-94f27749ae01"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`.

Incorporate the new retry and fallback protocol:
1. When calling `proxima:ask_perplexity`, inspect the response for GitHub connector / private repo content retrieval failures (e.g. phrases like "connector wouldn't surface raw text", "only returned file metadata/SHA", "blocked by fetch_url auth", "If you paste the actual...", "cannot quote actual lines").
2. **Automatic 1-Time Retry**: If Perplexity fails to read file contents via connector, the agent must retry ONCE on its own by passing the relevant local file path(s) directly into the `files` parameter of `proxima:ask_perplexity(message=..., files=[...])`.
3. **Critical Stop & Escalation Rule**: If the retry also fails or encounters errors, the agent MUST IMMEDIATELY STOP. Do NOT attempt to fall back to manual planning, guess the code, or proceed on your own. Output the exact message to the user:
`"I'm having trouble with the Ask Perplexity Tool."` followed by the specific details and wait for user instructions.

Use `replace_file_content` or `write_to_file` to update `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`.

</span>



<span title="Responded at 12:52am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The workflow file `/Users/matt/.gemini/config/global_workflows/proxima-planner.md` has been updated with the new retry and fallback protocol as requested. I have notified the parent agent.

</span>



</span>

</span>