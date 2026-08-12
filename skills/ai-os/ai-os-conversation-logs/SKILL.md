---
name: ai-os-conversation-logs
description: Work on ai-os session/thread logging tooling.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [ai-os, conversation, thread, transcript, discussion, compaction, cache]
    related_skills: [ai-os-auto-commit, ai-os-audit, planner]
---

# AI-OS Conversation & Thread Logs

## When to Use
- Working on ai-os session/thread tooling at `~/projects/ai-os` (preflight, watch_transcripts,
  gen_conversation_md, check_thread_bloat, context_handoff).
- Asked to keep/generate conversation history (thread.md, Discussions.html) for any project.
- Implementing/refining cache-aware thread lifecycle (dormant-thread compaction).

How Matt's ai-os infrastructure documents every agent conversation, and the design decisions
behind rendering, summarization, and cache-aware thread lifecycle. Use this when working on the
ai-os project's session/thread tooling (`~/projects/ai-os`), or when asked to keep/generate
conversation history (thread.md, Discussions.html).

## The pipeline (current state)

Every agent turn in Antigravity.app flows through:

1. **`scripts/preflight.py`** — runs at start of each turn (`--role orchestrator|leaf`). Checks
   quota, triage, LiteLLM, rules, thread bloat, git pull, and starts/uses the transcript
   watcher. Its `step_conversation_response()` ensures `watch_transcripts.py` daemon is running and
   does a one-pass sync of recent convs (last 2h) via `gen_conversation_md.py`.
2. **`scripts/watch_transcripts.py`** — file watcher daemon on `transcript.jsonl`; shows live info
   during the session.
3. **`scripts/gen_conversation_md.py <conv-id> --title "..."`** — reads `transcript.jsonl` (user
   messages, timestamps, forks/undos) + `history/turn_N.md` (agent responses) and renders a
   `thread.md`. Handles undos via fork files, demotes agent headings, strips transient status lines
   and thread.md self-links.
4. **`scripts/check_thread_bloat.py`** — computes token-based compaction signal:
   `T_hist_threshold = S + ((R-1)/M)*(T_sys + S)` where T_sys is rules+skills+MCP+AG_CONTEXT tokens.
   Flags a thread bloated when `T_hist > threshold` (defaults R=4, S=1000, M=5).

Key paths:
- Transcripts: `~/.gemini/antigravity/brain/<conv-id>/.system_generated/logs/transcript.jsonl`
- `context_handoff.py` writes `tmp/context_handoff.md` in the project root (git status, active plan,
  recent decisions) for thread restoration.

## Global rule: Discussions.html per project (user preference)

Durable global preference for ALL projects, not just ai-os:
- **Keep every user prompt verbatim** (full history preserved).
- **Fold large pasted code chunks by default** (`<details>/<summary>`).
- **Summarize verbose agent replies** (keep full detail accessible, show concise version).
- **Auto-generate `Discussions.html`** in every project folder, a browsable discussion history.

`thread.md` (from `gen_conversation_md.py`) is the Markdown precursor; `Discussions.html` is the
generalized, browsable HTML rendering of the same idea applied to every project.

**Implemented (2026-08-09):** `scripts/discussions_html.py` is a standalone, dependency-free
generator that reads a transcript.jsonl (Antigravity format, `--conv-id` or `--transcript`) and
emits a self-contained `Discussions.html`. It renders verbatim user prompts (escape_html, no raw
HTML leakage from user content), folds large fenced code blocks into closed `<details class=
"code-fold">`, and summarizes verbose agent replies with a lead summary + a `<details class=
"full-reply">` toggle showing the full text. A toolbar checkbox toggles `body.folded` (hides full
replies/code bodies). Agent content is read from PLANNER_RESPONSE steps — it does NOT depend on
`history/turn_N.md`. Tested against a real transcript (14 exchanges, 41KB, 5 code folds, 8
full-reply details). `--output` lets it land in any project root (the global-rule target).

## Cache-aware thread handoff (design, not yet implemented)

Because resuming a dormant thread re-ingests the FULL verbatim transcript (cache is only a
cost/speed layer — nothing auto-summarizes on cache expiry), the design couples cache expiry with
compaction:

- Track `last_message_at` per thread (alongside provider/model, since TTL differs).
- Per-provider TTL config (not hardcoded): Anthropic 5min (1h w/ extended), Gemini/Antigravity 60min,
  DeepSeek unknown→conservative 1h, OpenAI 30min. Apply `safety_margin` (default 0.8).
- **DYNAMIC safety margin (2026-08-09 refinement):** the margin must NOT be a flat constant — it
  scales with thread cost. The cost of a wrong cold re-ingest grows with `T_hist` (already computed
  by `check_thread_bloat.py`). Small/short thread → few tokens at risk → relaxed margin (compact
  less eagerly). Large/long thread → huge re-ingest at risk → aggressive margin (compact sooner).
  Shrink `effective_margin` from `base_margin` (0.8) toward a `min_margin` (e.g. 0.35) as
  `T_hist / T_hist_threshold` rises. There's always residual unknown, but this ties handoff
  conservatism to the cost of being wrong.
- Pre-send gate: if `idle_time >= ttl * effective_margin` → summarize old thread with a cheap model, seed a
  new thread with the summary + anti-injection instruction + pointer back to the original, archive
  the old thread. Mechanical decision, no LLM call just to decide.
- Skip if thread < ~2-3K tokens, don't evaluate mid-burst, cap handoff chain length (~3) then flag
  for manual review.
- Config surface: `cache_ttl_overrides`, `safety_margin` (+ `min_margin` + scaling curve driven by
  `T_hist`/`T_hist_threshold`), `min_tokens_to_compact`,
  `summarizer_model`, `max_handoff_chain_length`.

See the full design note:
`~/projects/ai-os/agent-logs/2026-08-09_cache-aware-thread-handoff-design.md`

## Cross-platform transcript sync (idea stage)

Goal: recognize when Matt raises an issue he's discussed before, across all projects and platforms
(Antigravity.app, Hermes, project forks), and pull the prior transcript. Proposed aggregation of
Antigravity `brain/` transcripts + Hermes local session DB + per-project forks, matching incoming
prompts against global history. Agent keeps a lightweight summary in context and digs into the full
prior transcript only when a problem recurs.

## Pitfalls

- `skill_manage`/`skills_list` have a namespace ambiguity in this profile: categorized skills exist
  under BOTH `~/.hermes/skills/<name>/` and `~/.hermes/skills/<category>/<name>/`. Use the
  categorized path (e.g. `ai-os/<name>`) or write directly to the SKILL.md file to avoid
  "Ambiguous skill name" errors.
- `gen_conversation_md.py` strips a lot (transient status lines, thread.md self-links, heading
  demotion) — don't expect a verbatim agent-response mirror; it's a cleaned, human-readable thread,
  NOT a substitute for the raw `transcript.jsonl`.
