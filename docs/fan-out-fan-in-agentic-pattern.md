# Fan-Out / Fan-In Agentic Pattern

A high-throughput orchestration architecture where a fast orchestrator decomposes goals into parallel subtasks for cheap execution units.

---

## Why It Works

### 1. Massive Latency Compression
4 sequential 10s steps = 40s total. Fan-out reduces this to ~10–12s (plus orchestrator overhead). You trade serial wait time for parallel API concurrency.

### 2. Asymmetric Cost-to-Intelligence Ratio
Use a top-tier model for structural planning, then push 90% of raw output generation to an ultra-cheap model (e.g., DeepSeek V4 Flash). Get top-tier *structure* at a fraction of the cost.

### 3. Context Window Isolation (Preventing Context Poisoning)
Subagents operate with **pristine, targeted context windows**. Long chats accumulate noise from errors, intermediate thoughts, and dead ends. Parallel subagents never see each other's mess — each only sees its specific prompt and inputs.

---

## Where It Breaks

### 1. Hidden State Dependencies (Race Condition Trap)
Parallelization only works for **decoupled micro-tasks**. If Task B secretly relies on an interface or architectural decision made by Task A, both models will invent their own assumptions.

- **Failure:** Subagent A writes a DB schema, Subagent B writes an API endpoint assuming different table names.
- **Fix:** The orchestrator must produce **strict interface contracts** (TypeScript types, JSON schemas, mock signatures) *before* fanning out.

### 2. The Merge Bottleneck (Reducer Problem)
Generating 5 parallel code blocks is easy; stitching them together cleanly is hard. Handing 5 disparate chunks to the orchestrator with "combine these" reintroduces the hallucination and context-length issues you tried to avoid.

- **Fix:** Assign subagents to **isolated files or decoupled modules** so the final step is a simple file-system write or git merge — not a complex logical synthesis pass.

### 3. Cascading Hallucinations
If the orchestrator's initial plan has a subtle logic flaw, you spawn N subagents all building beautifully formatted code on a broken foundation — at N× the speed.

- **Fix:** Validate the orchestrator's architecture contract before dispatching workers. A linter/compiler/test run on the plan itself catches this early.

---

## Reliable 3-Stage Pipeline

```
[ Orchestrator (e.g., Gemini Flash / GPT-4o) ]
              │
              ├── 1. Generate Architecture & Strict Contracts
              │
      ┌───────┼───────┐  (Fan-Out)
      ▼       ▼       ▼
   [Sub 1] [Sub 2] [Sub 3]  (Cheap Model - Parallel Execution)
      │       │       │
      └───────┼───────┘  (Deterministic Validation)
              ▼
   [ Local Linter / Compiler / Test Suite ]
              │
              ▼  (Fan-In)
[ Integrator / Final Polish Pass ]
```

### Stage 1: Contract Generation (Orchestrator)
The smart model outputs a structured plan with **explicit schemas/types** defining how pieces talk to each other. This is the most important stage — bad contracts cascade everywhere.

### Stage 2: Parallel Workers (Cheap Model)
Dispatch isolated prompts containing *only* the specific task + the relevant contract schemas. No shared context, no cross-contamination.

### Stage 3: Deterministic Verification Before Assembly
Run local tooling (linters, type checkers, unit tests) on individual outputs *before* returning them to the orchestrator. Filter broken work before the integration pass.

> If your harness enforces clean boundary contracts between parallel workers, this architecture delivers ~80% of the capability of high-tier reasoning models at a fraction of the cost and time.

---

## Key Principles Summary

| Principle | Rule |
|---|---|
| Decoupled tasks only | If outputs depend on each other's internals, serialize them |
| Contracts before fan-out | Types, schemas, and interfaces must exist before workers start |
| File-level isolation | One subagent = one file/module, not one subagent = one logical concern |
| Validate before merge | Never hand raw parallel outputs directly to the integrator |
| Orchestrator is the planner | Don't use the orchestrator for raw generation — use it for structure |
