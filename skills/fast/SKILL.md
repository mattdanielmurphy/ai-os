---
name: fast
description: Have the first agent answer or work directly, bypassing the default orchestrator-worker delegation pattern while remaining concise.
---
1. The first agent handles the user's next request itself. Do not invoke `_plan-with-ai-os`, delegate to a worker, or use an orchestrator-worker pattern.
2. Completely bypass multi-step planning, task lists, and file structure mapping unless a safety or correctness check is required.
3. Move straight to performing the work or returning the direct answer or code diff.
4. If the request is a trivial change, return *only* the modified code block—absolutely no conversational filler or summaries.
