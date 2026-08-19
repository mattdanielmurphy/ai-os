---
title: "Refining Agent Response Logic"
date: "2026-08-17"
conversation_id: "0e440883-8499-4205-bcb7-b43c5e25e4a2"
source: "antigravity"
---

# Refining Agent Response Logic

## User

Please make two critical fixes:

File 1: `/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`
In `parse_exchanges`:
Look at lines 574-585:
When a `PLANNER_RESPONSE` has no tool calls, it is the agent final response for that exchange.
Currently:
```python
                content = obj.get('content', '') or obj.get('text', '')
                if content and isinstance(content, str) and content.strip():
                    cleaned = clean_agent_content(content.strip())
                    if cleaned:
                        if is_transient_status_line(cleaned):
                            latest_transient_status = cleaned
                        elif has_tool_calls:
                            pass
                        else:
                            accumulated_text = [cleaned]
```
Fix this so that when `not has_tool_calls` and `content` is present, `accumulated_text = [cleaned]` is ALWAYS set, and it overwrites any stale `latest_tool_action` or `latest_transient_status`!
Also, when flushing in `flush_current_turn()`:
If `accumulated_text` is present, use it directly as `agent_text` and do NOT fall back to `latest_tool_action`!
```python
        if pending_users:
            history_turn_text = load_agent_response(history_dir, len([i for i in active_items if i['type'] == 'exchange']) + 1) if history_dir else ''
            if accumulated_text:
                agent_text = '\n\n'.join(t for t in accumulated_text if t.strip()).strip()
            elif history_turn_text:
                agent_text = history_turn_text
            elif latest_tool_action:
                agent_text = f"✅ *Action completed: {latest_tool_action}*"
            else:
                agent_text = latest_transient_status or ''
```

File 2: `/Users/matt/projects/ai-os/scripts/postflight_lib.py`
In `format_metrics_table`:
Make sure the Handoff column cleanly shows the cost delta + token delta:
```python
    if conv_id and metrics.get('savings_pct', 0) > 25:
        headers.append("Handoff")
        handoff_url = f"http://127.0.0.1:3031/handoff?session={conv_id}"
        cost = metrics.get('cost_comp', {})
        c_cost = cost.get('continuing', 0)
        h_cost = cost.get('handoff', 0)
        if h_cost <= c_cost:
            cost_badge = f"-${c_cost - h_cost:.3f} T1"
        else:
            cost_badge = f"+${h_cost - c_cost:.3f} T1"
        values.append(f"[\u26a1 -{metrics['savings_pct']}% (~{metrics['compact_display']}) \u00b7 {cost_badge}]({handoff_url})")
```

Ensure both files run cleanly without errors.

---

## Assistant

The requested fixes have been applied:

1.  **`/Users/matt/projects/ai-os/scripts/gen_conversation_md.py`**: Updated to ensure `accumulated_text` is set and prioritizes explicit agent content over tool actions during turn flushing. Stale `latest_tool_action` and `latest_transient_status` are now explicitly cleared when `accumulated_text` is populated.
2.  **`/Users/matt/projects/ai-os/scripts/postflight_lib.py`**: Updated the `format_metrics_table` function to use the requested `-$X.XXX T1` or `+$X.XXX T1` cost badge format in the Handoff column.

---
