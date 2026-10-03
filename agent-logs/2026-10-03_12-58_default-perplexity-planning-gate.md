# Default Perplexity Planning Gate

- Made `_plan-with-ai-os` the default planning gate for all non-trivial Codex work, before any delegation or implementation.
- The workflow now requires a GitHub `origin` before calling `query_aios.js --plan` to obtain a Perplexity plan.
- `/fast` explicitly bypasses both the planning gate and the orchestrator-worker path.
