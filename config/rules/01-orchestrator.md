# Orchestrator Rules

1. **Thread Management (Perplexity)**: We do not care about caching when it comes to Perplexity because it's a 100% integer turn-based quota system. We purely care about the cache getting too large for reasoning ability. **You MUST aggressively start new threads (via `new_conversation`) for new topics, tasks, or plans.**
2. **Context Delegation**: Rely on the Planner and Subagents to gather and formulate exact edits.
3. **Dual Environment Nuance**: Ensure tool usage explicitly conforms to whether you are in Hermes or Antigravity mode. Emulate operational behavior when Hermes daemon is inactive.
