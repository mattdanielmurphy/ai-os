# ON HOLD: Nimbalyst Integration

# AI-OS & Nimbalyst Architecture Specification

## 1. System Architecture Overview

A text-first local development ecosystem that merges a multi-agent orchestration architecture with local workspace rendering, shared markdown protocols, and cross-model token optimization frameworks.

### 1.1 Dual-Mode Agent Protocols (Triage vs. Worker Bee)

#### Triage Mode Mechanics

- **Target Rule Sets:** Defined within `src/systemPromptConfig.ts` under `TRIAGE_MODE_RULES`.
- **Functional Role:** High-level orchestrator tasked with problem decomposition, structural analysis, and dependency routing.
- **Operational Restrictions:** Strict prohibition on direct code file manipulation or write actions.
- **Delegation Engine:** Splits objectives into isolated tasks and calls execution pipelines to launch dedicated child worker threads.

#### Worker Bee Mode Mechanics

- **Target Rule Sets:** Defined within `src/systemPromptConfig.ts` under `WORKER_BEE_RULES`.
- **Functional Role:** Direct execution engine handling code generation, file composition, and structural refactoring.
- **Core Behaviors:**
  - **Auto-Commit Protocol:** Continuous micro-commits following verification gates.
  - **Context Self-Healing:** Monitors context boundaries and leverages `context_handoff.py` to offload deep histories to fresh child branches when token depth degrades performance.
  - **State Tracking:** Writes persistent state logs to the local `.agent-logs/` directory.

### 1.2 The Triage Editing Gating System

#### Token Optimization & Routing Logic

- **Gating Variable:** Driven by the boolean flag `$AIOS_DELEGATE`.
- **Edits Split Path:**
  - **Precision Refactoring:** Simple modifications or string replacements bypass heavy LLM loops completely and execute via local utilities (`scripts/precision_edit.py`).
  - **Complex Blocks ($AIOS_DELEGATE = true):** Quota-saving mode. Routes structural generation out to DeepSeek via a local LiteLLM proxy instance running on `localhost:4000` via `scripts/subagent.py`.
  - **Complex Blocks ($AIOS_DELEGATE = false):** Premium execution mode. Executes generation directly through the primary model utilizing quoted heredoc boundaries to bypass escaping failures.

#### Telemetry & Quota Accounting

- **Data Layer:** Usage and token burn rates per sub-model are recorded locally into `telemetry_db.py`.
- **Session Termination Loop:** Runs `scripts/get_last_cost.py` automatically at the end of each session to calculate and poll quota status.

## 2. Supporting Infrastructure & Utility Manifest

Infrastructure tooling across the repository is driven by text-first script components that manage codebases, synchronizations, and rule propagation.

### 2.1 Complete Script Matrix

#### History & Differential Discovery

- **`memory_search.sh`:** Initiates the first layer of git log processing by querying project history for specified metadata keywords.
- **`memory_diff.sh`:** Extracts granular code diffs mapped directly from historical reference points uncovered by the search layer.

#### Configuration Sync & Rule Replication

- **`append_system_rule.py`:** Programmatically injects newly discovered or optimized operational constraints directly into repository root configuration records (`GEMINI.md`, `CLAUDE.md`, or both configurations simultaneously).
- **`sync_rules.sh`:** Executes rsync sweeps to move global runtime configurations from user space (`~/.gemini/GEMINI.md`) down into project-level workspace assets (`.gemini/`).

#### Routing & Data Proxies

- **`subagent.py`:** Lightweight proxy client that converts file generation payloads into JSON configurations targeted at the local LiteLLM server gateway.
- **`telemetry_db.py`:** Persistent local store aggregating input/output token counts, execution latencies, and model targets.
- **`context_handoff.py`:** Generates structured handoff sheets summarizing system state, files modified, and next-step assertions before clearing context windows.

## 3. Native Mapping inside the Nimbalyst Environment

Integrating the orchestration architecture into Nimbalyst utilizes native workspace features, including markdown-backed task trackers, automations, and custom extensions.

### 3.1 Natively Aligned Workflows

#### Workspace Trust Layer & Execution Remapping

- **Rule Engine Location:** Nimbalyst reads project rules natively out of the `CLAUDE.md` asset located at the project directory root.
- **Shell Approvals:** Command loops (like auto-commit routines) map into the Nimbalyst trust layer. Security configurations in `.claude/settings.local.json` use patterns like `Bash(git:*)` or specified directory permissions to allow background operations without manual confirmation blocks.
- **Commit Pipelines:** The native `/commit` command automatically handles status staging and generates prefix tags. It can be paired with the **Auto-approve commits** toggle in `Settings > Agent Features` to completely automate verification loops.

#### State Synchronization & Task Trackers

- **Durable State File:** Unified storage maps cleanly into Nimbalyst's schema-driven **Tracker Overview**.
- **Sync Vectors:** Shared statuses, tasks, and architectural decisions are tracked via markdown frontmatter (`trackerStatus`) or inline text blocks utilizing the `#type[...]` tag syntax inside your workspace files. Updates compile bidirectionally between raw markdown text edits and visual Kanban boards.

### 3.2 Dynamic Orchestration via Custom Extensions

To manage the multi-model token-saving routing system natively within Nimbalyst, a specialized extension can be implemented using the platform's hardened SDK.

#### Extension Manifest Specifications (`manifest.json`)

JSON

```javascript
{
  "id": "com.aios.harness",
  "name": "AI-OS Orchestration Engine",
  "version": "1.0.0",
  "main": "dist/index.js",
  "apiVersion": "1.0.0",
  "permissions": {
    "filesystem": true,
    "ai": true
  },
  "contributions": {
    "aiTools": [
      "aios.delegate_edit",
      "aios.optimize_rules"
    ]
  }
}

```

#### Orchestrator Tooling & LiteLLM Integration

- **Subagent Threading:** The Triage mode orchestrator can call native session spawning through the Model Context Protocol. By calling `spawn_session`, the extension kicks off sibling sessions that join the parent workstream context, mirroring your custom context-healing protocol.
- **Stateless LiteLLM Proxying:** To bypass provider limitations, your custom tool utilizes the `ExtensionAIService` with full `ai` permissions. The tool handler calls stateless, non-session completions (`chatCompletion`) with strict output parameters (`responseFormat: { type: "json_object" }`). This lets you handle token tracking programmatically while managing proxy routing logic directly within your TypeScript extension.

## 4. Systematic Self-Modifying Rules Loop

By combining Nimbalyst's localized **Automations** with your custom extension tools, you can establish an automated, self-optimizing feedback loop that updates project constraints on a set schedule.

### 1. The Optimization Cron (Automations File)

Create an automation document within the project directory at `nimbalyst-local/automations/rules-optimizer.md`. This leverages frontmatter controls to run a persistent optimization check entirely backgrounded:
Markdown

```javascript
---
automationStatus:
  id: rules-optimizer
  title: Local Rules Optimization Loop
  enabled: true
  schedule:
    type: interval
    intervalMinutes: 120
  output:
    mode: replace
    location: nimbalyst-local/automations/optimizer-logs/
    fileNameTemplate: "audit-report.md"
---

# Operational Constraint Audit

Review the recent repository git history logs, token tracking values in your telemetry store, and transaction data inside `.agent-logs/`.

Identify recurring compilation faults, rejected diff trends, or excessive cost anomalies. Programmatically formulate an updated rule adjustment to prevent these structural issues.

```

### 2. Execution & Reload Gate

- **Analysis Step:** The automation runs on a local interval timer, using Claude Code to ingest local system logs and performance traces.
- **Modification Step:** If an optimization threshold is reached, the agent invokes your custom tool (`aios.optimize_rules`). The extension handler consumes the payload, verifies file integrity, and appends the optimized constraint to `CLAUDE.md`.
- **Instant Hot-Reload:** Because Nimbalyst watches workspace configuration changes dynamically, the updated rules are pulled into the system state within 30 seconds. The optimization applies to the very next agent task session without requiring a workspace reload or host application restart.
