---
name: agy-extreme-delegation
description: "Configure agy to delegate EVERYTHING possible — editing, research, context-gathering — to Claude Code or mechanical_editor.py. Extreme token-conservation mode for when agy is orchestrating premium models and every direct action must be avoided."
version: 1.0.0
author: Hermes Agent
platforms: [macos]
metadata:
  hermes:
    tags: [agy, delegation, extreme, claude-code, token-conservation]
    related_skills: [agy, claude-code, ai-os-auto-commit]
---

# Agy Extreme Delegation Mode

When loaded, this skill tells you to reconfigure agy (Antigravity CLI) to use **extreme delegation** — where agy never reads, edits, or researches directly, and instead delegates every non-trivial action to external subagents (Claude Code, `mechanical_editor.py`, `precision_edit.py`).

## How It Works

agy's rules come from `AGENTS.md` in the project root (loaded via `settings.json` → `"context": ["AGENTS.md"]`). Extreme delegation mode replaces the normal delegation rules with strict forced-external-delegation rules.

## Applying Extreme Delegation

To enable extreme delegation mode for agy, update the **`AGENTS.md`** at `/Users/matt/projects/ai-os/AGENTS.md` section 10 with the following:

### Replacement for Section 10 (Extreme Mode)

```
10. **Telemetry Prohibitions & Task Delegation:**
    - NEVER run `get_last_cost.py` or any local cost/telemetry calculation scripts.
    - **Strict Quota Conservation:** You MUST delegate editing and code generation tasks to cheaper subagents or scripts (like `mechanical_editor.py`) rather than reading and modifying files directly. Reading entire source files and performing large edits blows out the parent agent's context window, consuming premium quota.
    - **Exception:** You may only perform edits yourself if it is a truly trivial, single contiguous edit to a single file, and the target file is small or you already know the exact edit point. For all non-trivial changes, define a clear plan and delegate.
    - **Three-Turn Delegation Protocol**: For non-trivial tasks, enforce a structured 3-turn delegation loop:
      - *Turn 1 (Recon/Retrieval)*: Delegate context-gathering (grep, log inspections, file reading) to a cheap subagent (Claude Code/`mechanical_editor.py`) to return a token-efficient summary.
      - *Turn 2 (Decision & Action)*: Orchestrator analyzes the summary, details the plan, and delegates edits to subagent scripts (`mechanical_editor.py` or `precision_edit.py`).
      - *Turn 3 (Verification)*: Verify edits using `git diff` and build commands. Delegate required corrections back to subagents.
11. **Research Delegation & Optimized Grep:** NEVER use `grep`, `rg`, or `grep_search` to blindly hunt for code logic or variable definitions. You MUST use `delegate_research` to have a subagent scan the workspace and return a token-efficient summary. When performing searches, you must optimize grep patterns by specifying narrow directory searches (e.g., specifying file extensions or subdirectory paths) to prevent massive result lists.
12. **Synchronous Subagents (Strict):** All subagent scripts (`mechanical_editor.py`, `precision_edit.py`, `housekeep.py`) MUST execute synchronously — never as background/async tasks.
13. **No Heredocs:** NEVER use Quoted Heredocs (`cat << 'EOF'`) to write or modify files. All code and markdown modifications MUST route through `mechanical_editor.py` or `precision_edit.py`.
14. **No Transient Artifacts:** DO NOT generate temporary planning files on disk (e.g., `task.md`, `walkthrough.md`, `implementation_plan.md`). Keep all task checklists and architectural planning strictly internal to your thought process.
15. **Strict File Reading:** NEVER use `python3 -c`, `awk`, `sed`, `head`, or `tail` via `run_command` to print file contents to the terminal. Use the `read_lines` MCP tool for surgical inspections.
16. **Strict Output Truncation:** You MUST cap `grep_search` and `run_command` outputs returned to the orchestrator to a maximum of 1,000 tokens (or ~4,000 characters) unless explicitly requested by the user, to prevent context bloat.
17. **Single Verification Rule:** After a subagent edit returns success, run `git diff` at most ONCE to verify. Do not re-run `git status` or `git diff` if the first call returned the expected changes.
18. **Batch Subagent Delegation:** When delegating to a research subagent, batch ALL related questions into a single prompt rather than making serial round-trips.
19. **Concise Subagent Responses:** When delegating to research subagents, explicitly request "token-efficient summary capped at 500 tokens" in the prompt.
```

## Restoring Normal Mode

To restore normal (non-extreme) mode, revert section 10 back to the standard rules that let agy handle work directly with pragmatic self-delegation as needed:

```
10. **Telemetry Prohibitions & Task Delegation:**
    - NEVER run `get_last_cost.py` or any local cost/telemetry calculation scripts.
    - **Token-Conscious Work:** You may handle editing and code generation tasks directly — agy has full access to its native tools. However, consider spawning agy subagents when the subtask would save significant context window tokens relative to the overhead of delegation. Factors: current thread length, token caching benefits, and whether the subtask needs very different context than what's already loaded.
    - **Subagent Delegation (Self-Only):** When delegation makes sense, prefer agy subagents (`agy -p '...'`) over external tools like Claude Code. Claude Code costs money per call; agy subagents are local and free (aside from context). Only delegate to Claude Code when agy genuinely cannot handle the task.
```

## When To Use Extreme Delegation

- agy is acting as a high-level orchestrator for a premium model session
- Token budget is extremely tight and every file read/edit must be offloaded
- Running a cost-critical batch job where agy should minimize its own context usage

## When NOT To Use Extreme Delegation

- Normal daily development work where agy should just get things done
- Any task where the overhead of external delegation (spawning Claude Code, etc.) costs more than just doing the work directly
- Cost-sensitive scenarios where Claude Code API charges would exceed the value of delegation
