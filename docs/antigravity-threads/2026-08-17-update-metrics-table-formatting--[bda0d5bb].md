---
title: "Update Metrics Table Formatting"
date: "2026-08-17"
conversation_id: "bda0d5bb-2a32-447a-9b05-9f871a87dfaf"
source: "antigravity"
---

# Update Metrics Table Formatting

## User

Please update `/Users/matt/projects/ai-os/scripts/postflight_lib.py`:

In `format_metrics_table(metrics: dict, conv_id: str = None) -> str`:
Instead of raw numbers or removing cost, format the handoff column to convey the cost delta clearly and intuitively at a glance:

1. Look at `cost = metrics.get('cost_comp', {})`:
- `c_cost = cost.get('continuing', 0)`
- `h_cost = cost.get('handoff', 0)`
- Calculate delta ratio or dollar delta:
  - If `h_cost <= c_cost`:
    - `cost_badge = "T1: Cheaper"` or `cost_badge = f"-${c_cost - h_cost:.3f}"`
  - If `h_cost > c_cost`:
    - `cost_badge = f"+${h_cost - c_cost:.3f} T1"` (shows the minor cache-write premium on turn 1)

2. Display format:
`values.append(f"[\u26a1 -{metrics['savings_pct']}% (~{metrics['compact_display']}) \u00b7 {cost_badge}]({handoff_url})")`

This gives the user both the **Token Savings Delta** (`-84% (~12k)`) AND the **Instant Turn 1 Cost Delta** (`+$0.003 T1` or `-$0.005 T1`) in one clean, immediately understandable glance!

Ensure syntax and imports are 100% clean.

---

## Assistant

The updates to `/Users/matt/projects/ai-os/scripts/postflight_lib.py` have been completed successfully. The `format_metrics_table` function now calculates and displays the cost delta badge in the Handoff column, providing clear visibility into the cost impact alongside token savings.

---
