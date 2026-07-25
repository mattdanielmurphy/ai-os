# Step 01: Token Evaluator Script (`check_thread_bloat.py`)

## Goal
Dynamically measure system prompt buy-in tokens ($T_{\text{sys}}$) and current conversation history tokens ($T_{\text{hist}}$) to determine economic thread bloat status.

## Target Files
- `scripts/check_thread_bloat.py`
- `scripts/preflight.py`

## Requirements & Detailed Specifications
- Sum token counts for:
  - `GEMINI.md` / `.rules/`
  - Active `SKILL.md` files in `~/.gemini/config/skills/`
  - MCP JSON schemas in `~/.gemini/antigravity/mcp/`
  - `AG_CONTEXT.md`
- Parse `transcript.jsonl` from current conversation directory.
- Compute $T_{\text{hist\_threshold}} = S + \frac{R-1}{M} \cdot (T_{\text{sys}} + S)$ where $R=4, S=1000, M=5$.

## Verification Criteria
- Run `python3 scripts/check_thread_bloat.py` and inspect JSON output for accuracy.
