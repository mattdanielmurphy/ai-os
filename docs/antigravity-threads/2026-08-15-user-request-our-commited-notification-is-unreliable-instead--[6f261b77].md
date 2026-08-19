---
title: "User Request: our 'commited' notification is unreliable. Instead of ap"
date: "2026-08-15"
conversation_id: "6f261b77-3ab3-48f4-b5f5-7b76f16d2123"
source: "antigravity"
---

# User Request: our 'commited' notification is unreliable. Instead of ap

## User

User Request: our 'commited' notification is unreliable. Instead of appending it to the agent's response after the code is committed, let's just add a dynamic Committed status in our thread token counter. If it's red, there's an error or something; if it's yellow, it's uncomitted, if it's green, all committed.

Please act as a senior architect and systems planner for ai-os and userscript-bundler. Output a detailed, actionable implementation plan with:
1. Architectural Strategy: High-level overview of the proposed approach.
2. Data Structures & State Management: Define new data structures or changes to existing state.
3. API/Interface Contracts: Define function signatures, classes, and expected interface contracts.
4. Logic Flow & Algorithms: Step-by-step pseudo-code or logic description for the main execution flow.
5. Error Handling & Edge Cases: Identify potential failure points and mitigation strategies.
6. Implementation Steps: A list of specific files to modify and the required changes in each, ordered for execution.

---

## Assistant

# Architectural & Systems Implementation Plan: Dynamic Git Committed Status Indicator

## 1. Architectural Strategy
Currently, auto-commits append a rendered `<details>` badge directly to the agent’s response in `gen_conversation_md.py` whenever a matching result is written to `.commit_results`. This is unreliable due to timestamp race conditions, incomplete exchange matching, and cluttering the natural conversational stream.

We will replace the inline response badge with a **dynamic "Committed" status column inside the thread token counter metrics table**. 

### Core Components:
1. **Thread Metrics Engine (`postflight_lib.py`)**:
   - Computes the repository's git status dynamically on every metric refresh.
   - Evaluates three explicit states:
     - 🟢 **Committed (Green)**: Repository is completely clean (`git status --porcelain` returns empty).
     - 🟡 **Uncommitted (Yellow)**: Repository has modified, untracked, or staged changes pending auto-commit or manual commit.
     - 🔴 **Error / Conflict (Red)**: Git command failure, merge conflict markers present, or error output detected.
2. **Markdown Generator (`gen_conversation_md.py`)**:
   - Removes the inline `<details style="...">✅ Committed</details>` badge generation logic from `gen_conversation_md.py`.
   - Incorporates the new `"Committed"` column into the pinned footer table schema rendered via `format_metrics_table`.
3. **Transcript & Daemon Watcher (`watch_transcripts.py`)**:
   - Continues triggering background `auto_commit.py` when uncommitted changes exist.
   - Triggering a background re-render of `thread.md` updates the table indicator to 🟢 as soon as `auto_commit.py` finishes and leaves the working tree clean.

---

## 2. Data Structures & State Management

### Metric Output Dictionary Schema (`postflight_lib.py`):
Extend `compute_thread_metrics(conv_id, agent, workspace_root)` output dictionary:

```python
{
    "token_display": "24k",
    "cache_display": "1h",
    "indicator": "🟢",
    "brief_str": "",
    "breakeven_str":
<truncated 1913 bytes>
─► Write rendered thread.md with updated pinned metrics table
```

---

## 5. Error Handling & Edge Cases

1. **Non-Git Directory or Missing Workspace Root**:
   - Fall back to `/Users/matt/projects/ai-os` or detect root via `git rev-parse --show-toplevel`.
   - If git fails or directory is not a repo, return `🔴 Error (Non-Git)`.
2. **Merge Conflicts**:
   - `git status --porcelain` line starting with `UU`, `AA`, `UD`, etc. triggers `🔴 Error (Conflict)`.
3. **Subagent & Parallel Workspace Scenarios**:
   - Workspace root can be passed into `compute_thread_metrics` or resolved via standard git root detection so subagent branches reflect their respective repository status.

---

## 6. Implementation Steps & Required Changes

1. **`scripts/postflight_lib.py`**:
   - Implement `get_git_commit_status(repo_root: str)` helper function.
   - Integrate `git_commit_status` into `compute_thread_metrics()`.
   - Update `format_metrics_table()` to add the `"Committed"` column into the Markdown table.

2. **`scripts/gen_conversation_md.py`**:
   - Remove `.commit_results` JSON scanning (`commit_dir` lookup logic lines 654-674).
   - Remove inline `<details style="...">...✅ Committed</details>` badge insertion (lines 687-691).

3. **`scripts/watch_transcripts.py`**:
   - Retain background `auto_commit.py` invocation when uncommitted changes exist.
   - When auto-commit finishes, trigger thread re-render so the thread token counter table updates from `🟡 Uncommitted` to `🟢 Clean`.

---

### Links & References
- Active Project Board: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)
- Target Files:
  - [`postflight_lib.py`](file:///Users/matt/projects/ai-os/scripts/postflight_lib.py)
  - [`gen_conversation_md.py`](file:///Users/matt/projects/ai-os/scripts/gen_conversation_md.py)
  - [`watch_transcripts.py`](file:///Users/matt/projects/ai-os/scripts/watch_transcripts.py)
- Thread Log:

---
