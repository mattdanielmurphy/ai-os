---
title: "Implement Session Compaction Metrics"
date: "2026-08-17"
conversation_id: "06d3608b-7f84-49a9-80d0-150eb2caceb1"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 17, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">Please update `/Users/matt/projects/ai-os/scripts/postflight_lib.py` to calculate and render the Session Compaction / Handoff Delta in `format_metrics_table`:<br><br>1. Update `compute_thread_metrics` to compute compact token estimates:<br>```python<br>    # Estimate compaction savings (stripping tool calls, raw traces, intermediate turns)<br>    raw_history_tokens = max(0, token_count - t_sys)<br>    compact_history_tokens = int(raw_history_tokens * 0.18) if raw_history_tokens > 0 else 0<br>    compact_total = t_sys + compact_history_tokens<br>    savings_pct = int(((token_count - compact_total) / max(1, token_count)) * 100) if token_count > compact_total else 0<br>```<br>Include `compact_display`: `format_tokens(compact_total)`, `savings_pct`: `savings_pct`, `handoff_ready`: `token_count > 35000` in the returned dict.<br><br>2. In `format_metrics_table(metrics, conv_id=None)`:<br>If `conv_id` and metrics.get('savings_pct', 0) > 25:<br>Add a "Handoff Delta" column or a clickable compaction action link:<br>`headers.append("Handoff")`<br>`handoff_url = f"http://127.0.0.1:3031/handoff?session={conv_id}"`<br>`values.append(f"⚡ -{metrics['savings_pct']}% (~{metrics['compact_display']})")`<br><br>Make sure all changes in `postflight_lib.py` are robust, clean, and tested.</span>



<span title="Responded at 9:51am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Successfully updated `/Users/matt/projects/ai-os/scripts/postflight_lib.py` to include the requested Session Compaction / Handoff Delta metrics and rendering logic in the `format_metrics_table`.

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota |
| :--- | :--- | :--- | :--- |
| ~35k / ~450k 🟢 (optimal) | 4:50am | 🟡 Uncommitted (1) | 95 ❓, 30 📤 |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/06d3608b-7f84-49a9-80d0-150eb2caceb1/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>