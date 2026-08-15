# THREAD HANDOFF & SYSTEM PROMPT GATEWAY ARCHITECTURE

## 1. Executive Summary & Objective
This handoff carries over the architectural discoveries and task requirements from the prior session to immediately implement the **Dynamic System Prompt & Unified Triage Gateway** across `ai-os` (Hermes, Antigravity IDE/CLI, Claude Code, agy).

---

## 2. Core Problem Discovered in Prior Thread
- **System Prompt Duplication & Bloat:** Each subagent invocation across Antigravity/Hermes duplicates massive static system prompts (300K+ chars / 40K+ tokens), rapidly exhausting context windows and token quotas.
- **Rule Drift Across Platforms:** Maintaining disparate static system prompts in Hermes, Claude Code, Antigravity, and agy causes synchronization bugs.
- **Conflation Avoided:** **System Directives** (operational rules, safety guardrails in `.rules/`, `GEMINI.md`, `CLAUDE.md`) are strictly distinct from **`AG_CONTEXT.md`** (project-specific durable architectural knowledge).

---

## 3. The New Architecture: "One-Line Gateway & Dynamic Compiler"
- **Minimal Platform System Prompt:** Replace static system prompts across platforms with a single bootstrap instruction:
  `Execute: python3 /Users/matt/projects/ai-os/scripts/preflight.py`
- **Dynamic Preflight Compiler (`preflight.py` & `triage_task.py`):**
  1. Detects host agent type (Orchestrator vs. Leaf Subagent).
  2. Evaluates model quota vectors (`ag-quota`) + Jules session availability (`jules_quota.py`).
  3. Evaluates prompt keywords (heavy vs. quick inline edit vs. domain context like `MAC_ENVIRONMENT.md`).
  4. Dynamically compiles and outputs *only* the minimal required system directives, rules, and context for that specific turn.
  5. Strips leaf subagent prompts so subagents receive zero orchestrator bloat.

---

## 4. Google Jules Integration Assets Already Built
- **Obsidian Master Note:** `[Google Jules Agent Delegation Architecture.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Google%20Jules%20Agent%20Delegation%20Architecture.md)`
- **REST API Delegate Script:** `[jules_delegate.py](file:///Users/matt/projects/ai-os/scripts/jules_delegate.py)` (supports `JULES_API_KEY` and `JULES_API_KEY_ALT` with automatic failover).
- **Micro-Repo Context Provisioner:** `[jules_provisioner.py](file:///Users/matt/projects/ai-os/scripts/jules_provisioner.py)` (bundles task context into `AGENTS.md` and pushes to GitHub).
- **Quota Monitor:** `[jules_quota.py](file:///Users/matt/projects/ai-os/scripts/jules_quota.py)` (aggregates 200 daily sessions across both accounts).
- **Triage Evaluator:** `[triage_task.py](file:///Users/matt/projects/ai-os/scripts/triage_task.py)`.

---

## 5. Next Session Action Items
1. Refactor `build_rules.py` and `.rules/` to build lean, dynamic system prompts for each platform (Antigravity, Hermes, Claude Code, agy).
2. Configure subagent templates so child leaf subagents bypass full system prompt inheritance.
3. Test preflight dynamic prompt compilation end-to-end.
