# Personalized Prompt Autocomplete

## Problem

Working across multiple agents and threads, it's easy to lose track of your own past prompts and discoveries. You say the same things repeatedly because saving an initial prompt somewhere and recalling it quickly never quite becomes a habit.

## The Idea

**Personalized autocomplete for prompts** — as you type in the ai-os interface, the system scans your history and agent logs in real-time, surfacing relevant completions from past work.

The mechanics:

1. **Foundation layer** — a high-quality, drop-in autocomplete component (CodeMirror extension, Monaco widget, or similar) that handles the UI smoothness: inline suggestion rendering, keyboard-driven acceptance/rejection, fuzzy matching.

2. **Context engine** — as you type, it searches:
   - Your past prompts and conversations (local Hermes session history)
   - Agent logs from current and past projects
   - (Optionally) skills, memories, and saved notes

3. **Intelligent weighting** — recency, project match, and frequency all factor into what gets suggested. A prompt from this morning on the same project scores higher than a similar one from three months ago.

4. **In-the-moment correction** — this is the key advantage over post-hoc search. When a completion appears, you see it while still typing and can immediately reject it ("no, not that") or accept it and refine. The suggestion is live feedback, not a separate search step.

5. **Warm starte** — by the time you finish composing, the context engine has already done its initial searchpass. The follow-up retrieval (feeding context to the model) is far faster because it's been prepped during your typing window.

## Relationship to Agent Logs

The autocomplete idea is independent of the broader question of whether agent logs should remain the primary context store. Skills and memories (auto-created by Hermes) may eventually make agent logs redundant for the context preloading use case. But the autocomplete feature — live, in-flight suggestion from personal history — works well with any backend and stands on its own merits regardless of where the context retrieval debate lands.