---
title: "Update Proxima Planner Configuration"
date: "2026-08-14"
conversation_id: "0e929150-e087-4b77-a7eb-0e3f7cd5042d"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/.gemini/config/global_workflows/proxima-planner.md:

```markdown

Run high-reasoning planning using the `planner` skill instructions.

1. **Sanity Check**: Analyze the user's request against the current active project directory.
2. **Pre-flight Git Check**: Ensure a GitHub remote is configured (`git config --get remote.origin.url`). If missing, STOP and ask the user if they want to create a remote repository.
3. **Run Prompt Script**: Run `python3 ~/projects/ai-os/scripts/generate_planner_prompt.py "<request>" --context="full"` — this generates `./tmp/planner_prompt.txt`.
4. **Invoke Perplexity (Fast MCP Tool with Async CLI Recovery)**:
   - **Primary Path**: Call `proxima:ask_perplexity` with the text of `./tmp/planner_prompt.txt`.
   - **Timeout Recovery**: If the MCP tool times out after 3 minutes (`context deadline exceeded`), Proxima is STILL running the query in the background. DO NOT retry from scratch. Immediately run:
     `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --recover --output ./tmp/planner_output.txt --timeout 300` via `run_command` to retrieve the completed plan as soon as Proxima finishes!
5. **Format Output**: Format the output into `implementation_plan.md`.

**Vision Provider & Image Attachment Protocol**: If the user attaches an image or screenshot, do NOT pass the raw image to Perplexity by default (preserving Perplexity file upload quota). The main orchestrator acts as the vision provider, inspecting and describing the visual elements, UI layout, diagrams, or error details in rich textual descriptions, and embeds that description into the prompt passed to Perplexity.

**CRITICAL FALLBACK RULE**: If Perplexity session is expired or permanently fails, fall back to `/planner 3.1 pro high` via `agymcp:agy_start` or `agymcp:agy` with the prompt from `./tmp/planner_prompt.txt`.
```

</span>



<span title="Responded at 1:42am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The update to `/Users/matt/.gemini/config/global_workflows/proxima-planner.md` has been completed. The workflow now incorporates the primary MCP path for Perplexity with the specified timeout recovery protocol and updated fallback rules.

</span>



</span>

</span>