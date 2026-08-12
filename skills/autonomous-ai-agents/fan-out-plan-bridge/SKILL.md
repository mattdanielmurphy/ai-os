---
name: fan-out-plan-bridge
description: Cheap main bridges between expensive and cheap workers.
version: 1.0.0
author: Matt + Hermes
---

# Fan-Out Plan Bridge Pattern

A multi-tier delegation architecture using only native Hermes tools.
The main agent stays cheap; complex reasoning is outsourced to an
expensive planner, then executed by cheap workers via plan-as-data.

## Architecture

```
User prompt
    │
    ▼
┌──────────────────┐
│ Main Agent       │  ← cheap model (handles trivial directly)
│ (agy flash)      │
└──────────────────┘
    │
    ├─ Trivial? → respond directly (fast path)
    │
    └─ Complex? → delegate_task(goal="plan this", role="orchestrator")
                        │
                        ▼
              ┌────────────────────┐
              │ Expensive Planner  │  ← smart subagent
              │ (deepseek pro)     │
              │ - analyzes req     │
              │ - returns plan     │
              │ (structured JSON)  │
              └────────────────────┘
                        │
                        ▼
              Plan file arrives as subagent summary
                        │
                        ▼
              Main agent reads plan → fans out work
                        │
                        ├─ delegate_task(tasks=[step1, step2, ...])
                        │   (all cheap workers via delegation.model)
                        │
                        └─ Optional: delegate review pass to planner
```

## Prerequisites

```yaml
# ~/.hermes/config.yaml
delegation:
  max_spawn_depth: 2        # enables depth-2 (orchestrator → worker)
  model: gemini-3.6-flash-low  # cheap model for all workers
  provider: agy
```

- Main agent model set to a cheap fast model (e.g. agy flash)
- `delegation.model` set to the same cheap model

## How It Works

### Depth Levels

| Depth | Agent | Model | Role |
|-------|-------|-------|------|
| 0 | Main | Cheap (e.g. agy flash) | Triage + executor |
| 1 | Planner | Expensive (via agy MCP tool) | Deliberation + plan output |
| 1..N | Workers | Cheap (`delegation.model`) | Mechanical execution |

### The Plan Bridge

The expensive planner does NOT spawn workers. Instead it returns a
structured plan as its output (the subagent summary). The main agent
receives this summary and fans out execution using `delegate_task(tasks=[...])`.

This avoids the `delegation.model` constraint — the planner's output is
data, not tool calls — so its "children" are actually main-thread workers
that inherit the cheap `delegation.model`.

### Plan Format

Planner returns a JSON array of tasks:

```json
[
  {"id": "step-1", "goal": "Create file X with content Y", "depends_on": []},
  {"id": "step-2", "goal": "Run tests and report results", "depends_on": ["step-1"]}
]
```

The main agent reads this, optionally sorts by dependency, then calls:

```python
delegate_task(tasks=[
    {"goal": "Create file X with content Y"},
    {"goal": "Run tests and report results"}
])
```

## Variations

### With Review Pass
After workers finish, main agent optionally re-delegates to the
expensive planner for review:

```
Main → planner (review diffs) → main → planner (approve) → main → report to user
```

### With agy MCP for Expensive Calls
Instead of a separate subagent process, invoke the expensive model
via the agy MCP tool with model override:

```python
mcp__agymcp__agy(PROMPT="plan this: ...", model="gemini-3.1-pro-high")
```

This keeps everything in the main thread — no `delegate_task` overhead
for the planning step, just agy's model routing.

## Pitfalls

- **Main agent must faithfully execute the plan.** Cheap models may
  misinterpret complex plans. Keep plans as explicit action-oriented
  JSON, not prose.
- **No per-call model selection** on `delegate_task`. All children of
  a delegation use `delegation.model`. The planner can only communicate
  through its return text, not through tool calls that spawn workers.
- **Subagent summaries are self-reports.** Verify critical side-effects
  (file writes, API calls) from the main thread after workers finish.
- **Depth-2 agents are still `role='leaf'` by default.** The planner
  (depth 1) must be called with `role='orchestrator'` to receive the
  `delegation` toolset. Depth-2 agents (sub-sub-agents) don't need it —
  they're executors, not planners.