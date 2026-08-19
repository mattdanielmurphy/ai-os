---
title: "Update Python Metrics Formatting"
date: "2026-08-17"
conversation_id: "0dff2d8e-ecc6-43b2-8ead-df6edd9a6888"
source: "antigravity"
---

# Update Python Metrics Formatting

## User

Please update `/Users/matt/projects/ai-os/scripts/postflight_lib.py`:

In `format_metrics_table`:
Fix the token multiplier calculation so that it outputs realistic per-token pricing (e.g. assuming $1.25 per 1M tokens for Flash, which is $0.00000125/token instead of interpreting token counts as raw dollars!).
Currently `continuing_cost` is in tokens, not dollars, which gave `-$2970.870`!
Instead:
- Convert token cost to dollars assuming $1.25/1M tokens for write, $0.15/1M tokens for read.
- Even simpler: compare the effective token cost delta:
  - `c_tok = cost.get('continuing', 0)`
  - `h_tok = cost.get('handoff', 0)`
  - Convert to cents: `delta_cents = (c_tok - h_tok) * 0.000125`
  - If `c_tok >= h_tok`:
    - `cost_badge = f"-{int(((c_tok - h_tok)/max(1, c_tok))*100)}% cost T1"`
  - If `c_tok < h_tok`:
    - `cost_badge = f"+{int(((h_tok - c_tok)/max(1, c_tok))*100)}% cost T1"`
- Display clean and compact:
  `values.append(f"[\u26a1 -{metrics['savings_pct']}% context \u00b7 {cost_badge}]({handoff_url})")`

Ensure syntax and imports are 100% clean.

---

## Assistant

The `format_metrics_table` function in `/Users/matt/projects/ai-os/scripts/postflight_lib.py` has been updated to correctly calculate and display the token cost difference as a percentage-based badge instead of raw dollar amounts.

The updated logic now:
1. Retrieves `continuing` and `handoff` token counts.
2. Calculates the percentage difference between these counts.
3. Formats the badge cleanly as, for example, `-X% cost T1`.
4. Updates the final display string in the table to show a clean `context` metrics section.

---
