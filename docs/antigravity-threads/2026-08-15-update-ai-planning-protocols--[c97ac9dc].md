---
title: "Update AI Planning Protocols"
date: "2026-08-15"
conversation_id: "c97ac9dc-fca9-4e0d-a7b3-979f4751dc7f"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw + 2px); bottom: 0; padding: 2.5rem 2rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

You are a leaf file editor. Modify the following files according to the user directive:

1. In `/Users/matt/projects/ai-os/.rules/core_safety.md`:
Update lines 35-39 from:
```markdown

## Strict Planner / Workflow Immediate Dispatch
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/proxima-planner` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the prompt generation script, query the planner (Perplexity or Pro escalation), and present the resulting implementation plan without intermediate manual codebase rummaging.
- **Dispatch Restriction**: When `/proxima-planner` is invoked, the orchestrator MUST ONLY dispatch to `proxima:ask_perplexity`, and NEVER fallback to `agy`/`gemini` unless explicitly told to by Matt.
```

to:
```markdown

## Strict Planner / Workflow Immediate Dispatch
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/proxima-planner` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the prompt generation script, query the planner (Perplexity via `proxima:ask_perplexity`), and present the resulting implementation plan without intermediate manual codebase rummaging.
- **Strict Perplexity Dispatch & Fallback Policy**: When `/proxima-planner` is invoked, the orchestrator MUST ONLY dispatch to `proxima:ask_perplexity`. Never use Gemini 3.1 Pro for planning for any reason. Fall back to `agy` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to `agy`, ALWAYS use `Gemini 3.7 Flash (High)` for planning, NEVER 3.1 Pro.
- **Connection Recovery**: If `proxima:ask_perplexity` fails with `ECONNREFUSED` / port 19222 error, immediately launch/ensure Proxima is running (`cd ~/projects/external/Proxima && bun start &`) and retry `proxima:ask_perplexity`.
```

2. In `/Users/matt/projects/ai-os/.rules/gemini_only.md`:
Update line 26-28 from:
```markdown

## Pro Model Escalation for Recurring/Stuck Bugs
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST immediately escalate planning and root cause analysis to a Pro reasoning model (`Gemini 3.1 Pro (High)` / `pro` or `Claude Sonnet 5`).
- **How:** Invoke `/planner 3.1 pro high` via `agymcp:agy_start` or `agymcp:agy` with complete context, error logs, and prior failed attempt diffs. Do NOT attempt additional iterative Flash fixes without first obtaining a Pro model architecture plan.
```

to:
```markdown

## High-Reasoning Escalation for Recurring/Stuck Bugs
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to `proxima:ask_perplexity` or `Gemini 3.7 Flash (High)` (via `agymcp:agy` only if Perplexity quota is 0). Do NOT use 3.1 Pro.
```

3. In `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`:
Update line 20 from:
```markdown

**CRITICAL FALLBACK RULE**: If Perplexity session is expired or permanently fails, fall back to `/planner 3.1 pro high` via `agymcp:agy_start` or `agymcp:agy` with the prompt from `./tmp/planner_prompt.txt`.
```

to:
```markdown

**FALLBACK POLICY**: Fall back to `agy` ONLY if Perplexity quota is 0, or if the user specifically requests it. Never use Gemini 3.1 Pro for any reason; use `Gemini 3.7 Flash (High)` if falling back. If `proxima:ask_perplexity` fails due to connection/port 19222, launch Proxima (`cd ~/projects/external/Proxima && bun start &`) and retry.
```

</span>



<span title="Responded at 6:23am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested file modifications have been successfully completed:

1.  **[`core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md)**: Updated rules for strict Perplexity dispatch, explicit prohibition of Gemini 3.1 Pro, and a new `ECONNREFUSED` recovery policy.
2.  **[`gemini_only.md`](file:///Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/gemini_only.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/gemini_only.md)**: Refined the escalation policy to prioritize Perplexity or `Gemini 3.7 Flash (High)`, explicitly banning `3.1 Pro`.
3.  **[`proxima-planner.md`](file:///Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/proxima-planner.md)**: Updated the fallback policy to align with the new guidelines, prohibiting `3.1 Pro` and including specific instructions for launching the Proxima service upon connection failure.

The changes have been reported to the parent agent.

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~35k | 1:25am 🔴 (expired) | ~35k / ~403k 🟢 | 109, 20 🔬, 16 📤 |


| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~35k | 1:25am 🔴 (expired) | ~35k / ~403k 🟢 | 109, 20 🔬, 16 📤 |

</span>



</span>

</span>