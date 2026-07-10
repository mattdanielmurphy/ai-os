---
id: "implement-architecture-and-optimization-changes-2026-07-09"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-09T22:47:58.686Z"
modified: "2026-07-09T22:47:58.686Z"
completedAt: null
labels: []
order: "a5"
---
# Implement Architecture and Optimization Changes

# Comprehensive Architecture & Token Optimization Audit

This audit outlines the blueprint for optimizing your workspace, specifically tailored for the **Antigravity IDE sidebar interface**. Because the system executes headlessly via IDE tool calls rather than a persistent terminal CLI session, token conservation relies completely on strict tool boundaries, intent-based handoffs, and absolute path translation.

## I. Token Parsimony & Editing Protocols

### 1. The Fast-Path Edit Protocol (Micro-Edits)

For discrete, programmatic changes, the main orchestrator should entirely bypass LLM-based subagents. If the orchestrator knows the precise line change, variable swap, or file append, it must use local text-mutation utilities.

- **Action:** Force the orchestrator to prioritize `precision_edit.py` for targeted modifications. This script handles `replace`, `append`, and `insert_after_string` programmatically, requiring zero API tokens and executing instantly.

- **Constraint:** Ban the use of Quoted Heredocs (`cat << 'EOF'`) within the sidebar environment. Heredocs risk shell-escaping errors and bloat the orchestrator's output token window with raw code blocks.

### 2. Intent-Driven Macro Delegation

When a file refactor requires architectural reasoning, the orchestrator delegates the change to `mechanical_editor.py` (running a capable, low-cost model like Gemini 2.5 Flash).

- **Action:** Shift from *blueprint* specs to *intent* specs. The orchestrator must not waste premium output tokens writing pseudo-code or line-by-line instructions for the subagent.

- **Example Shift:**

  - *Old Way:* `--spec "Go to line 34, change the variable to let, add a try/catch block, and log the error via telemetry_db."`

  - *New Way:* `--spec "Refactor the stream reader to handle multi-byte UTF-8 character truncation gracefully using telemetry logging."`

**Edit ScaleTarget ToolCognitive LayerToken CostMicro-Edit** (1-5 lines, deterministic)`precision_edit.py`Local Python Engine**ZeroMacro-Edit** (Structural refactor, logic additions)`mechanical_editor.py`Gemini 2.5 Flash (Subagent)Low-tier API Quota

## II. Context Isolation & Discovery Delegation

### 1. The Headless "Retriever Bee"

The primary context-bloat pattern occurs when the main agent runs recursive directory searches, files reads, or global grep operations to find code structures.

- **Action:** Register a dedicated tool: `delegate_research(query)`. This invokes a background script (`scripts/research_agent.py`) powered entirely by a commodity model.

- **The Loop:** When the orchestrator needs to locate a multi-file interaction, it calls the tool. The subagent executes the underlying `ripgrep`, folder scanning, and syntax tracing headlessly. It compiles a succinct markdown index of file paths, signatures, and relevant logic blocks, returning *only* that compressed summary to the sidebar orchestrator.

### 2. Automated Kanban Pre-Processing

Before the main orchestrator evaluates an active task, the context must be staged out-of-band.

- **Action:** When a markdown feature card in `.devtool/features/` switches to `status: "review"`, a background IDE macro runs `generate_repo_map.py` to compile the stable anchor map.

- **The Handoff:** The macro automatically structures the initial prompt payload: **System Instructions** + **Repo Map** + **Active Task Description**. The main agent wakes up with perfect spatial awareness, spending zero tokens on initial discovery.

## III. Global Rules Syntax & Subagent Isolation

### 1. Pruning the Global `GEMINI.md`

Because all system instructions are delivered via a global `GEMINI.md` file, its volume acts as a permanent tax on every conversation turn.

- **Action:** Systematically strip out subagent prompts, technical script implementation details, and structural repository profiles from the global file.

- **Rule:** `GEMINI.md` must strictly contain high-level identity rules, architectural guardrails, and tool execution schemas for the primary orchestrator. Domain knowledge belongs in `AG_CONTEXT.md`; tool operational logic belongs inside the scripts themselves.

### 2. Preventing Rule Contamination (File-Swap Failsafe)

When background subagents are invoked, they naturally look for the global rules file, causing double-loading loops where subagents try to act like high-level architects.

- **Action:** Embed the **File-Swap Technique** directly into your background execution utility.

- **The Mechanism:** The wrapper script instantly renames `~/.gemini/GEMINI.md` to `~/.gemini/GEMINI.md.bak`, initializes the subagent with its specific execution payload, and fires a background thread to restore the original file after a strict **10-second timer** expires. Because the engine only parses rules once at boot, the subagent runs cleanly while ensuring the global configuration is safely restored.

## IV. The Omnipresent "Run Anywhere" Blueprint

To ensure Antigravity functions flawlessly from any directory on your filesystem without breaking cross-project awareness, log tracking, or script paths, deploy the following systemic routing protocol:

```
                  ┌────────────────────────────────────────┐
                  │      Antigravity IDE Sidebar Host      │
                  └───────────────────┬────────────────────┘
                                      │
                   [Detects Execution Path via Workspace]
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       Universal Path Resolver          │
                  │  - Core Tools: ~/projects/ai-os/       │
                  │  - Global Rules: ~/.gemini/GEMINI.md   │
                  └───────────────────┬────────────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│  Local Project Directory     │              │ Cross-Workspace Directory    │
│  - Path: ./                  │              │  - Path: ~/projects/*        │
│  - Logs: ./.agent-logs/      │              │  - Logs: Indexing Search     │
└──────────────────────────────┘              └──────────────────────────────┘
```

### 1. Absolute Path Registry

The IDE extension host must resolve core tooling and instructions against absolute, anchored tracks rather than relying on relative execution paths (`./`).

- All orchestration utilities, helper scripts, and tracking parameters must look to the authoritative base environment variable pointing back to the core repository ecosystem (`/Users/matt/projects/ai-os/`).

- Global rules remain anchored globally at `~/.gemini/GEMINI.md`.

### 2. Hybrid Workspace Log Architecture

To allow agents to organize histories by individual projects while retaining complete cross-workspace visibility, the log engine uses a two-tier discovery strategy:

- **Tier 1: Local Storage**

  When a task finalizes, `scripts/housekeep.py` writes the Markdown engineering log directly into the local project root's folder structure at `./.agent-logs/`. This keeps repositories clean, modular, and safely version-controlled via Git.

- **Tier 2: Cross-Workspace Log Discovery Tool**

  Register a high-efficiency discovery tool for the orchestrator called `search_all_agent_logs(query)`. This script runs headlessly via `ripgrep` across a defined projects sandbox:

Python

```
#!/usr/bin/env python3
# scripts/search_all_agent_logs.py
import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Cross-project engineering log search.")
    parser.add_argument("query", help="Search keyword or architectural string")
    args = parser.parse_args()

    # Authoritative tracking baseline
    search_base = os.path.expanduser("~/projects/")
    
    cmd = [
        "rg",
        "--glob", "*/.agent-logs/*.md",
        "-n", "-C", "2",
        args.query,
        search_base
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"No matching historical context found for query: '{args.query}' across workspace logs.")

if __name__ == "__main__":
    main()
```

### 3. Integrated Tool Schema Contract

Expose this absolute portability directly to the Gemini model inside the sidebar by registering the following universal schema mapping:

JSON

```
[
  {
    "name": "search_all_agent_logs",
    "description": "Scans historical engineering logs across ALL local development directories on the system to retrieve past architectural decisions, solved bugs, or integration lessons.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The specific technical keyword, function name, error string, or architectural system to search for."
        }
      },
      "required": ["query"]
    }
  }
]
```

This structural framework guarantees complete environmental independence. The orchestrator can be initialized in a completely blank scratch directory, pull rules from your global setup, call validation scripts securely via absolute path registration, and dynamically pull past technical contexts from entirely different project directories whenever an architectural puzzle matches your history.