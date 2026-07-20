---
id: hermes-triage-interceptor
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-19"
modified: "2026-07-19"
completedAt: null
labels: ["hermes", "triage", "architecture"]
order: 1
---

# Implement Zero-Fork Hermes Triage Interceptor

## Background & Architecture Decisions
We previously implemented `scripts/triage_proxy.py` to intercept `prompt.submit` WebSocket requests before they reached Hermes Agent. However, we realized that completely bypassing Hermes Agent to run `agy` directly causes us to lose all of Hermes's long-term memory, state tracking, and semantic context benefits. Conversely, if we pass the prompt directly to Hermes natively, Hermes uses expensive models (like Claude 3.5 Sonnet) just to evaluate the prompt and spit out an MCP tool call to `agy`, which burns tokens and defeats the purpose of the Tier 1 Triage Gateway.

**The Solution:** We will implement a **Zero-Fork Python Wrapper** for Hermes Agent. Instead of forking the Hermes repo, we will create a wrapper script in `ai-os` that imports Hermes in memory, monkey-patches the core LLM execution function (`agent.chat_completion_helpers.chat_completion_request`), and then starts Hermes.

When a user submits a prompt:
1. The intercepted `chat_completion_request` plucks out *only* the user's latest text string.
2. It sends that string to Gemini Flash-Lite via `triage_router.tier1_triage(text)` (costing basically 0 tokens).
3. The massive Hermes system prompt is intentionally **dropped/ignored** during this step so we don't pay to transmit it.
4. If triage returns `coding_standard` or `coding_complex`, the interceptor instantly returns a **synthetic JSON tool-call response** to Hermes (e.g., "Use the agy MCP tool").
5. Hermes receives this response, assumes its own LLM generated it, blindly executes `agy`, and natively logs the resulting code changes to its long-term memory.

## Investigation Notes (How Hermes Starts)
Hermes is currently launched via a macOS launch daemon.
- **Plist:** `~/Library/LaunchAgents/com.matt.agent.hermes-gateway.plist`
- **Wrapper Script:** `/Users/matt/Library/Scripts/tmux-agent-wrapper.sh`
- **Execution Command:** The plist instructs the tmux wrapper to execute `/Users/matt/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace` inside `/Users/matt/.hermes`.

## Implementation Tasks
- [ ] **Create the Wrapper Script:** Create `/Users/matt/projects/ai-os/scripts/aios_hermes_wrapper.py`. It should:
  - Add `/Users/matt/.hermes/hermes-agent` to `sys.path`.
  - Import `agent.chat_completion_helpers` and monkey-patch `chat_completion_request`.
  - Import `hermes_cli.main` and execute `main()`.
- [ ] **Implement the Triage Intercept Logic:** Inside the monkey-patched function, extract the user's message from the payload, call `triage_router.tier1_triage(text)`, evaluate the quota rules (from `get_quota()`), and return a correctly formatted `mcp_call` synthetic payload if the task is coding. If non-coding, fallback to the original `chat_completion_request`.
- [ ] **Modify Startup Process:** Edit `com.matt.agent.hermes-gateway.plist` (or the underlying tmux script logic) so that it calls our new `aios_hermes_wrapper.py` instead of `-m hermes_cli.main`. 
- [ ] **Test:** Reload the `launchctl` service, trigger a prompt from Hermes WebUI, and verify that the system prompt is suppressed during triage and the `agy` MCP tool is correctly orchestrated without burning Claude tokens.
