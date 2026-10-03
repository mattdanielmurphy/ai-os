# Codex Worker Default and Fast Override

- Added the non-`agy` Codex fallback policy: for non-trivial requests, the orchestrator delegates worker work to `gpt-6-luna` with low reasoning and reviews the result.
- Updated the repository-owned `/fast` skill to bypass that pattern so the first agent handles the request directly.
- Rebuilt the shared rule artifacts and synchronized the updated skill to the configured local runtimes.
