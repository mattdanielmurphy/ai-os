---
title: "Fix AI Agent Implementation Errors"
date: "2026-08-17"
conversation_id: "a90cfaa0-55b0-4b2b-bfc6-90e11840c87d"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 16, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">clearly our agents do NOT know how to use `_plan-with-ai-os`<br>@[conversation:"Metadata Parsing Improvement Plan"] <br>Look at the mistakes the agent makes RIGHT OFF THE BAT. Trying to run a separate generate_prompt script even though we've folded that into query_ai-os... and other issues.<br>Fully identify all the issues and fix them all.<span style="display: block; margin: 8px 0; border: none; border-top: 1px solid rgba(130, 115, 220, 0.35);"></span>continue</span>



<span title="Responded at 4:18am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Done. Here's the full diagnosis and what was fixed:

---

### Root Cause Analysis: [conversation://7facb558-e042-4073-a3a6-b65abdfaa270]

### Bugs Found

| # | What happened | What should have happened |
|---|---|---|
| **1** | `ECONNREFUSED 127.0.0.1:19241` → agent ran `pgrep`, `la status \| grep ...`, `la list`, `grep -rn "19241"` | Immediately run `--recover` with no diagnostic steps first |
| **2** | `la status \| grep "companion\|bridge\|perplexity"` → error ("name argument required") | `la status` requires a positional name arg — the agent wasted a turn on a broken command |
| **3** | After all the fumbling, the agent **never ran `--recover`** and produced **no plan** | `--recover` then `la start agy-proxy` if still failing |
| **4** | Matt mentioned a "separate `generate_prompt` script" — this stale mental model was leaking into the agent's reasoning | The script was folded into `query_aios.js` — no such step exists |
| **5** | Rules said "ensure ai-os companion is active" with no specifics on how | Now explicitly names `la start agy-proxy` as the exact restart command |

### Fixes Applied

**[`core_safety.md`](file:///Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/.rules/core_safety.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/.rules/core_safety.md)** — Replaced vague "Connection Recovery" with explicit numbered steps:
1. ECONNREFUSED → immediately run `--recover`, zero diagnostic commands
2. If recover also fails → `la start agy-proxy`, then retry
3. Explicitly banned: `pgrep`, `la status` (without name), `grep` for port numbers

**[`_plan-with-ai-os.md`](file:///Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/config/global_workflows/_plan-with-ai-os.md)** — Added:
- Top-level ⚠️ warning killing the stale `generate_prompt.py` mental model
- Explicit Step 4 with the same exact two-command recovery protocol
- ❌ NEVER list spelling out the forbidden diagnostic behaviors

**Rebuilt** → `GEMINI.md`, `CLAUDE.md`, `HERMES.md` all updated and pushed.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~80k / ~420k 🟢 (optimal) | 11:20pm | 🟢 Clean | 104 ❓, 29 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/a90cfaa0-55b0-4b2b-bfc6-90e11840c87d/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>