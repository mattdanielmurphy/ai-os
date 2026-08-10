# Global Cross-Platform Transcript Sync & Self-Learning — Discussion Notes

**Date:** 2026-08-09
**Status:** Discussion / proposal (global rule — applies to all projects)
**Owner:** ai-os ($HOME/projects/ai-os) — where this conversation evolved to

---

## 1. Global transcript sync across all platforms

**Goal:** Recognize when the user is talking about an issue they've raised before — *across all
projects and all platforms* — and pull that prior transcript to give the agent the context it needs.

Why cross-project / cross-platform: threads sometimes start in the wrong project folder, on a
fork of a project, in Antigravity.app, or in Hermes. We want one synchronized source of history.

**Idea:** A central prompt/transcript history that aggregates:
- Antigravity.app sessions (transcript.jsonl under `~/.gemini/antigravity/brain/<conv-id>/`)
- Hermes sessions (local session DB)
- Any per-project forks / copies

When a new prompt arrives, match it against the global history (by topic/keywords/project) to
identify whether this is a repeat of a previously-discussed issue. If so, pull that prior
transcript into context instead of treating it as brand new.

## 2. Agent self-learning from history

Different levels of context — the agent can *dig deeper when problems arise* (e.g. when the same
thing needs fixing a second/third time). This is more cost-efficient than always loading full
history: the agent keeps a lightweight summary in context, and only retrieves the detailed prior
transcript when a problem recurs.

## 3. GLOBAL RULE — Discussions.html per project

This is a **global rule** for every project folder.

**What we want:**
- Every prompt the user ever writes should be **kept** (verbatim history).
- When the user pastes in big chunks of **code**, it should be **folded by default** (e.g.
  `<details>/<summary>`), so it doesn't blow up the readable feed.
- **Summarized versions of agent replies** — agent replies can be verbose, so show a summary
  (keep the full detail available, but present a concise version by default).
- A `Discussions.html` should be **generated automatically** in every project folder, showing the
  history of discussions in a readable, browsable form.

**Prior art / existing system:** In ai-os we already worked out a system where `preflight.py` runs
at the start of every turn, starts a file watcher on the jsonl log, and extracts tons of info to
display live during the Antigravity session (via `watch_transcripts.py` + `gen_conversation_md.py`,
which generate `thread.md` from `transcript.jsonl` + agent response files). A lot of R&D went into
displaying HTML/CSS in Antigravity's limited markdown/artifact view. This `Discussions.html`
idea generalizes that to every project.

## Proposed layering (summary)
1. **Raw history:** keep every prompt verbatim (per project).
2. **Folding:** fold large code pastes by default (`<details>`/`<summary>`).
3. **Summaries:** summarize verbose agent replies (keep full detail accessible).
4. **Render:** auto-generate `Discussions.html` per project so the history is browsable.
5. **Global matching:** match incoming prompts against the aggregated cross-project/cross-platform
   history to surface repeats, and pull prior transcripts when a problem recurs.

---

*Companion note:* [Cache-Aware Thread Handoff — Design Plan](2026-08-09_cache-aware-thread-handoff-design.md)
