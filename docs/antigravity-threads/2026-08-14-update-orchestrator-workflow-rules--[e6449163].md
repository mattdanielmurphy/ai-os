---
title: "Update Orchestrator Workflow Rules"
date: "2026-08-14"
conversation_id: "e6449163-18e0-4a3e-947a-737bda519a6e"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw + 2px); bottom: 0; padding: 2.5rem 2rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 14, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please inspect and update `/Users/matt/projects/ai-os/.rules/` to add the rule approved by the user:

Rule Addition:
```markdown

## Strict Planner / Workflow Immediate Dispatch
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/proxima-planner` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the prompt generation script, query the planner (Perplexity or Pro escalation), and present the resulting implementation plan without intermediate manual codebase rummaging.
```

Find the most appropriate rule file under `/Users/matt/projects/ai-os/.rules/` (for example `proxima.md`, `orchestrator.md`, or the relevant rules file), add this section cleanly, and then run `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` to compile the single-source rules across GEMINI.md, CLAUDE.md, and HERMES.md. Verify that the build succeeds.

</span>



<span title="Responded at 6:39pm" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The "Strict Planner / Workflow Immediate Dispatch" rule has been successfully added to `core_safety.md` and compiled into the global agent rules.

### Summary of Actions
1.  **File Update**: Added the following rule to [`core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md):
    ```markdown
    ## Strict Planner / Workflow Immediate Dispatch
    - **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/proxima-planner` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
    - **Workflow**: Immediately run the prompt generation script, query the planner (Perplexity or Pro escalation), and present the resulting implementation plan without intermediate manual codebase rummaging.
    ```
2.  **Compilation**: Executed `python3 /Users/matt/projects/ai-os/scripts/build_rules.py`. The build completed successfully and updated all relevant rule files (`CLAUDE.md`, `GEMINI.md`, `HERMES.md`, `LEAF.md`).

</span>



</span>

</span>