# Sidebar Project Threads & Context-Pruned Resumption

I have documented your new feature proposal in both the Vision document and the Features ledger. Below is an overview of the concept and the specific updates made.

## Concept Overview
- **Project Threads Sidebar**: A new list in the sidebar displaying past thread history specific to the currently active project.
- **Auto-Clear Harmony**: Threads will default to running `/clear` before a prompt is sent to aggressively prune the active token footprint and prevent context bloat.
- **Pruned Context Feed**: Continuity is maintained by feeding the agent a lightweight summary/index of past logs and discoveries instead of full transcripts or code files.
- **Lazy Retrieval**: The agent can call a dedicated helper command/function to fetch more detailed context (e.g. detailed step logs or full transcripts from `.agent-logs/`) only if required for a task.

---

## Documents Updated

### 1. [VISION.md](file:///Users/matthewmurphy/projects/ai-os/VISION.md)
Added the **Sidebar Project Threads** concept to the *New Unorganized Eventual Features* section:
```markdown
- Sidebar Project Threads: A new sidebar section for each project displaying "Project Threads" (representing a history of past agent logs/conversations).
  - The context of these threads is pruned (omitting code and large file outputs, leaving only high-level steps/discoveries).
  - Designed to work alongside `/clear` by default, recreating continuity by supplying the agent with a lean historical summary of past threads.
  - Allows the agent to query detailed transcripts or full step logs via dedicated helper functions (e.g. leveraging `agy` transcripts/detailed logs) when more information is needed.
```

### 2. [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)
Added a new proposed feature block under `[Proposed] Sidebar Project Threads & Context-Pruned Resumption`:
```markdown
### [Proposed] Sidebar Project Threads & Context-Pruned Resumption
* **Sidebar Project Threads:** Add a project-specific list of past threads/conversations to the sidebar.
* **Pruned Context Feed:** Recreate thread continuity by default while still running `/clear` to minimize token bloat. Feed the agent a highly pruned overview of past step logs/discoveries.
* **Detailed Log Retrieval:** Provide helper functions enabling the agent to JIT pull full transcripts or granular logs (`.agent-logs/transcripts/` or `.agent-logs/details/`) on demand.
```

---

## Background Git Commit
All edits have been successfully committed to the repository:
- **Commit Message**: `docs: propose sidebar project threads feature in VISION.md and FEATURES.md`
