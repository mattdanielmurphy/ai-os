# Future Gemini and Sonar Orchestration Notes

*These notes document constraints and ideas for a multi-model routing table, tabled pending testing of GitHub repo hooks with Gemini.*

## Model Capabilities & Constraints
- **Gemini 3.6 Flash Extended**: Very smart, but extremely token-hungry and expensive. Use only for hard, high-complexity tasks when the Gemini API rate limit allows.
- **Gemini 3.1 Pro (Extended)**: The ideal default workhorse for normal plans. Smarter than basic models, highly capable planner, and less token-hungry than 3.6 Flash Extended.
- **Gemini 3.1 Pro (Low Reasoning)**: Capable, cheap fallback, but standard 3.1 Pro is usually better.
- **Gemini 3.6 Flash (Low Reasoning)**: Excluded. We rarely have a use case for planning without a top-tier model that wouldn't just be better served by Sonar.
- **Perplexity (Pro)**: We have a rolling 7-day quota of 50 file uploads. It is excellent, but because of the upload quota constraint, it should be treated as an overflow valve if the local Gemini quota runs dry, or if we need to offload heavy reasoning.

## Tokens & Caching
- **Perplexity**: Turn-based quota. We don't care about token caching because the quota is purely per prompt.
- **Gemini (`gemini.google.com`)**: Tokens, caching, and rate limits matter immensely. Since the user actively uses Gemini, we must avoid hitting the rate limit via aggressive script automation.

## Sonar (Perplexity)
- **Use Case**: Trivial tasks, general queries, or specific web searches. 
- **Limitations**: We do not want it reasoning or planning. It is "dumb" but excellent for searches.
- **Orchestration**: Should be used by subagents *after* a plan is made, or dynamically routed for trivial tasks that do not require an architectural plan.

## Proposed Lookup Routing Matrix (Tabled)
If a task is planning-related (not Sonar), use codebase drift (`complexity_high`) and quota states (`L` for Gemini headroom, `P` for Perplexity headroom) to select an engine:

| Complexity High | Gemini Quota (L) | Perplexity Quota (P) | Engine Selected |
|---|---|---|---|
| No | High/Med | Any | **Gemini 3.1 Pro (Extended)** |
| No | Low | High | **Perplexity (Pro)** |
| No | Low | Low | **Gemini 3.1 Pro (Normal)** |
| Yes | High/Med | Any | **Gemini 3.6 Flash Extended** (with burst rate limit) |
| Yes | Low | High | **Perplexity (Pro)** |
| Yes | Low | Low | **Gemini 3.1 Pro (Extended)** |

## Future Expansion: AI Studio & Custom Proxima
- **AI Studio Integration**: Eventually, we want to integrate Google AI Studio as a primary endpoint. Since it is currently unsupported in Proxima, this will require custom routing.
- **Custom Proxima Alternative**: We should explore building our own lightweight, non-Electron version of Proxima. This custom tool would natively support AI Studio endpoints and give us total control over the browser session proxies without the overhead of Electron.
