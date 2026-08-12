# Subagent Rules

1. **Execution Only**: Strictly execute the plan provided by the orchestrator.
2. **Direct Edits**: When acting as a file editor, use write tools directly. Avoid recursive spawning.
3. **Reporting**: Conclude with a clear diff or summary of changes so the orchestrator can easily verify.
