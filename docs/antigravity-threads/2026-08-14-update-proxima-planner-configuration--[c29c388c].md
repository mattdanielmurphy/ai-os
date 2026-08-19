---
title: "Update Proxima Planner Configuration"
date: "2026-08-14"
conversation_id: "c29c388c-1edf-464f-b652-ed244cbca5ab"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Update /Users/matt/.gemini/config/global_workflows/proxima-planner.md:
Replace the synchronous MCP tool step with running `node ~/projects/ai-os/scripts/query_proxima.js` via `run_command`:

```markdown

Run high-reasoning planning using the `planner` skill instructions.

1. **Sanity Check**: Analyze the user's request against the current active project directory.
2. **Pre-flight Git Check**: Ensure a GitHub remote is configured (`git config --get remote.origin.url`). If missing, STOP and ask the user if they want to create a remote repository.
3. **Run Prompt Script**: Run `python3 ~/projects/ai-os/scripts/generate_planner_prompt.py "<request>" --context="full"` — this generates `./tmp/planner_prompt.txt`.
4. **Invoke Perplexity via CLI (Immune to MCP 3-Minute Timeout)**:
   - Run `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600` via `run_command`.
   - If output contains an auth error, notify user to refresh the Proxima session.
   - Read the generated plan from `./tmp/planner_output.txt`.
5. **Format Output**: Format the output into `implementation_plan.md`.

**Vision Provider & Image Attachment Protocol**: If the user attaches an image or screenshot, do NOT pass the raw image to Perplexity by default (preserving Perplexity file upload quota). The main orchestrator acts as the vision provider, inspecting and describing the visual elements, UI layout, diagrams, or error details in rich textual descriptions, and embeds that description into the prompt passed to Perplexity.

**CRITICAL FALLBACK RULE**: If Perplexity is unreachable or session is expired, immediately fall back to `/planner 3.1 pro high` via `agymcp:agy_start` or `agymcp:agy` with the prompt from `./tmp/planner_prompt.txt`.
```

Ensure syntax and markdown are valid.

</span>



<span title="Responded at 1:40am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The workflow file `/Users/matt/.gemini/config/global_workflows/proxima-planner.md` has been updated as requested. The synchronous MCP tool step has been replaced with the specified `run_command` execution using `node ~/projects/ai-os/scripts/query_proxima.js`, and the fallback protocol has been updated.

</span>



</span>

</span>