# ChatGPT macOS Home & Default Antigravity Delegation

- Established ChatGPT on macOS as Matt's primary conversational surface and home, with Antigravity (`agy`) as the default capable reasoning and execution agent whenever usable quota is healthy.
- Gated direct ChatGPT handling strictly to obviously lightweight requests (greetings, trivial math, short text rewrites/formatting < 150 chars, context-free one-liners, explicit quick/simple, or explicit user override not to delegate).
- Implemented deliberately low delegation threshold: all substantive requests (technical reasoning, architecture, multi-part, file/rules/memory inspections, planning, debugging, and implementation) route to `agy` by default.
- Implemented Thin Handoff policy: handoffs preserve verbatim user prompt, active repo/cwd, and execution mode/safety boundaries without prompt-expansion bloat.
- Modeled explicit quota states (`healthy`, `low`, `exhausted`, `unavailable`, `unknown`) via `ag-quota -j` with snapshot caching and PA API fallback, providing clean fallback to direct ChatGPT.
- Surfaced full routing visibility (`[ai-os routing]`) across CLI and JSON outputs, detailing backend selection, origin (automatic/explicit), quota status, and concrete fallback reasons.
- Created `.rules/codex_only.md` and compiled into `~/.codex/AGENTS.md` via `scripts/compile_dynamic_prompt.py` and `scripts/build_rules.py`.
- Fixed broken `scripts/triage_task.py` and expanded `tests/test_triage.py` to 9 passing tests covering all 6 required routing scenarios (64/64 total repo tests pass).
- Documented 7 deferred Hermes-inspired capabilities in `docs/parking-lot/hermes-inspired-ideas.md`.
