# Handover: DeepSeek v4 Flash Low Triage System

We want to build a triage / routing mechanism in the AI OS setup to save token costs and optimize response speeds.

## Core Setup
- **Entry point:** Always start the initial step of a task or query using `claude-haiku-ds-v4-flash-low` (DeepSeek-based fast model).
- **Triage Logic:** The fast/cheap model performs the initial parsing, checks the files, and decides if it can complete the task directly. If the task requires deep reasoning, complex file modifications, or multi-step execution, it triages/hands off the execution to a more powerful model (e.g., `claude-fable-ds-v4-pro-med` or `claude-opus-gem-2.5-pro`).
- **Goal:** Implement this triage protocol automatically in our scripts or command-line wrappers (like `agy` or our custom executors) so the user doesn't have to manually select models.
