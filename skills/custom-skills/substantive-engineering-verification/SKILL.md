---
name: substantive-engineering-verification
description: Delegate and verify substantive engineering changes in Matt's projects.
---

# Substantive Engineering Verification

Use this workflow for multi-file feature work, behavior changes, or sustained debugging.

1. Read applicable project instructions and respect their delegation preference. When Antigravity is preferred, route work through the `agymcp` MCP bridge before implementation. Use its `review` or `plan` mode for independent analysis and `execute` only when delegating authorized edits.
2. Inspect the working tree before editing. Preserve unrelated pre-existing changes; never revert them as cleanup.
3. Trace the full behavior across relevant routes, components, state ownership, and persistence. Do not assume a component-level patch solves cross-route behavior.
4. After implementation, inspect the diff and run relevant existing tests plus type checking or build checks by default. Add focused coverage when the behavior is not adequately covered.
5. If a check fails, investigate and fix failures caused by the change. Distinguish pre-existing failures clearly.
6. Report the delegation path, concrete changes, checks and outcomes, and any remaining limits. Do not imply completion without verification.
