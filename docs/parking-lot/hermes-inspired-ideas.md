# Hermes-Inspired Architectural Ideas (Deferred)

> [!NOTE]
> **Status**: Parking Lot / Future Possibility Only.  
> Hermes Desktop and Hermes Agent are **not** active architectural dependencies, primary UIs, or mandatory backends. These ideas are captured here for reference and evaluation if future scaling warrants revisiting them.

---

## 1. Curated Reusable Skills or Procedural Playbooks

- **Potential Value**:
  Standardizes multi-step procedural sequences (e.g. specialized API audits, database migrations, specific framework release flows) into validated, modular execution playbooks with explicit steps and validation gates.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Skill rot, redundant overlapping instructions across platforms, drift between documentation and runtime behavior, and cognitive bloat in agent prompt contexts.
- **Why Deferred During Stabilization**:
  The harness priority is getting the core macOS daily-driver routing (ChatGPT front-end + Antigravity execution) reliable, fast, and simple. Expanding custom skill libraries adds maintenance surface area before baseline stability is established.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if Matt or agents frequently repeat identical 5+ step manual procedural tasks where agent error rates exceed 20% due to lack of formalized playbooks.

---

## 2. Better Retrieval of Relevant Past Sessions, Decisions, and Project History

- **Potential Value**:
  Enables agents to retrieve relevant context from historical transcripts, past architectural decisions, and resolved edge cases without requiring full file reads or manual search.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Indexing latency, noisy embedding false-positives polluting high-reasoning prompt windows, database lock contention (`state.db`), and background daemon instability.
- **Why Deferred During Stabilization**:
  Active projects already maintain high-signal context through `AG_CONTEXT.md`, `DEVELOPMENT_JOURNAL.md`, and the local Obsidian LLM Wiki. High-reasoning agents (`agy`) can directly inspect repository files without an intermediate retrieval layer.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider when project history exceeds human/agent skimming capacity and repetitive mistakes recur across sessions despite existing context files.

---

## 3. Preference/User-Model Memory with Explicit Scope, Provenance, and Review

- **Potential Value**:
  Maintains an evolving, structured model of user preferences, coding habits, tool affinities, and communication style with clear provenance (when and why a preference was learned).
- **Key Reliability, Maintenance, or Complexity Risk**:
  Hallucinated or stale preference drift, over-fitting on temporary edge cases, accidental privacy leaks across project boundaries, and lack of human review mechanisms.
- **Why Deferred During Stabilization**:
  The system already relies on explicit single-source rules in `.rules/` and compiled instructions (`GEMINI.md`, `CLAUDE.md`, `AGENTS.md`). Matt's explicit preferences are best captured directly in rules rather than an autonomous memory crawler.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if manual rule authoring becomes a recurring bottleneck and personal preferences across diverse projects drift frequently enough to justify reviewed user-model extraction.

---

## 4. Scheduled or Recurring Agent Workflows

- **Potential Value**:
  Automates periodic health checks, daily log rollups, dependency audits, backup synchronization, or quota reporting on background cron intervals.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Runaway token consumption, process accumulation / zombie background tasks, unexpected state mutation while user is working, and failure notification fatigue.
- **Why Deferred During Stabilization**:
  The priority is predictable, synchronous, user-initiated turns with zero phantom background loops or stray UI processes. Existing macOS LaunchAgents handle essential sync services.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if critical maintenance (e.g. cache cleaning, telemetry compaction, backup verification) consistently fails to occur organically at session start/end.

---

## 5. Model/Provider Routing Based on Cost, Quota, Capability, Reliability, and Task Type

- **Potential Value**:
  Fine-grained multi-model dispatch (e.g. routing fast lookups to Flash Lite, math to direct heuristics, deep reasoning to agy, external search to Perplexity, and code review to Sonnet) optimizing cost and quota velocity.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Routing misclassification, cascaded failure chains when an endpoint fails, high latency overhead during multi-tier routing handshakes, and opacity in which model produced a deliverable.
- **Why Deferred During Stabilization**:
  A simple binary rule (ChatGPT for lightweight; Antigravity `agy` for all substantive reasoning when quota is healthy) eliminates classifier ambiguity and keeps routing predictable and debuggable.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if Antigravity quota becomes chronically constrained (< 20% daily) requiring automated tiering to secondary paid providers or cheaper fallback models.

---

## 6. Isolated Delegated Subagents for Bounded Work

- **Potential Value**:
  Allows an orchestrator to spin off isolated, throwaway subagents in parallel sandboxes/worktrees for bounded investigations or verification tasks without cluttering the primary thread context.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Tmux session proliferation, git worktree synchronization conflicts, race conditions on shared filesystem resources, and high cognitive overhead for tracking subagent state.
- **Why Deferred During Stabilization**:
  `agy` natively handles internal tool execution, subagent delegation (`agymcp`), and investigation. Introducing an extra layer of orchestrator-level tmux subagent wrappers adds unnecessary complexity.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if large-scale parallel exploratory work (e.g. benchmarking 10 independent algorithms or refactoring 50 decoupled packages) is routinely required.

---

## 7. Reviewed Learning Pipeline Promoting Validated Lessons into Durable Rules/Skills

- **Potential Value**:
  A structured human-in-the-loop pipeline that collects insights from agent work logs, stages candidate lessons, and promotes validated rules into `.rules/` or custom skills.
- **Key Reliability, Maintenance, or Complexity Risk**:
  Rule proliferation, conflicting directives, auto-generated rule bloat degrading model adherence, and review fatigue.
- **Why Deferred During Stabilization**:
  The existing workflow (`learn_from_moment.py`, manual edits to `.rules/`, and `build_rules.py`) already ensures deliberate, human-reviewed rule updates. Automating promotion risks bloat.
- **Reconsideration Threshold / Observable Problem**:
  Reconsider if valuable lessons from session logs are repeatedly lost and not codified into `.rules/` through the standard postflight review.
